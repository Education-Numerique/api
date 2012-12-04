from lxxl.lib.storage import Db, DbError, ObjectId, DESCENDING, ASCENDING
from lxxl.lib.config import Config
import time


class Activity:

    def __init__(self, **entries):
        self.id = None
        self.publicationDate = None
        self.creationDate = None
        self.isPublished = False
        self.author = None
        self.isDeleted = False
        self.isReported = False

        self.seenCount = 0

        self.draft = {}
        self.draft['contributors'] = []
        self.draft['extraContributors'] = []
        self.draft['blobs'] = {}
        self.draft['title'] = ''
        self.draft['description'] = ''
        self.draft['level'] = None
        self.draft['matter'] = None
        self.draft['duration'] = None
        self.draft['difficulty'] = None
        self.draft['category'] = []
        self.draft['pages'] = []
        self.draft['extra'] = None

        self.published = {}
        self.published['contributors'] = []
        self.published['extraContributors'] = []
        self.published['blobs'] = {}
        self.published['title'] = ''
        self.published['description'] = ''
        self.published['level'] = None
        self.published['matter'] = None
        self.published['duration'] = None
        self.published['difficulty'] = None
        self.published['category'] = []
        self.published['pages'] = []
        self.published['extra'] = None

        entries = entries.copy()
        if '_id' in entries:
            self.id = entries['_id']
            del entries['_id']
        self.__dict__.update(entries)

    def publish(self, publish=True):
        if publish:
            self.isPublished = True
            self.publicationDate = int(time.time())
            self.published = self.draft
        else:
            self.isPublished = False
            self.publicationDate = None
            self.published = {}

    def setAuthor(self, user):
        self.author = {}
        self.author['uid'] = user.uid
        self.author['username'] = user.username

    def toObject(self):
        obj = self.__dict__.copy()

        if '_id' in obj:
            del obj['_id']

        obj['id'] = str(obj['id'])
        return obj

    def saveDraft(self, **entries):
        entries = entries.copy()
        draftList = ['title', 'description', 'level', 'matter',
                     'duration', 'difficulty', 'category', 'pages', 'extra']

        for (k, v) in entries.items():
            if not k in draftList:
                continue
            self.draft[k] = v

    def toDatabase(self):
        obj = self.__dict__.copy()

        if 'id' in obj:
            obj['_id'] = obj['id']
            del obj['id']

        if not obj['_id']:
            del obj['_id']

        if 'pages' in obj:
            del obj['pages']

        return obj


class Factory:

    @staticmethod
    def new(activity):
        if not isinstance(activity, Activity):
            raise Exception('invalid activity object', activity)
        try:
            c = Db().get('activities')
            tmp = activity.toDatabase()
            if '_id' in tmp:
                del tmp['_id']
            id = c.insert(tmp, True)
            activity.id = id
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def delete(activity):
        if not isinstance(activity, Activity):
            raise Exception('invalid activity object', activity)
        try:
            c = Db().get('activities')
            activity.isDeleted = True
            Factory.update(activity)
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def update(activity):
        if not isinstance(activity, Activity):
            raise Exception('invalid activity object', activity)
        try:
            c = Db().get('activities')
            c.update(
                {'_id': ObjectId(activity.id)},
                activity.toDatabase(),
                True
            )
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def incSeen(activity):
        if not isinstance(activity, Activity):
            raise Exception('invalid activity object', activity)
        try:
            c = Db().get('activities')
            c.update(
                {'_id': ObjectId(activity.id)},
                {'$inc': {'seenCount': 1}},
                True
            )
            activity.seenCount += 1
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def get(search):
        try:
            if isinstance(search, str):
                search = {'_id': ObjectId(search)}
            else:
                tmp = {}
                for (key, value) in search.items():
                    tmp[key] = value.lower()
                search = tmp
                del tmp

            search['isDeleted'] = False
            data = Db().get('activities').find_one(search)

        except DbError:
            output.error('cannot access db', 503)

        if data is None:
                return None

        return Activity(**data)

    @staticmethod
    def list(search):
        try:
            if isinstance(search, str):
                search = {'_id': ObjectId(search)}
            else:
                tmp = {}
                for (key, value) in search.items():
                    tmp[key] = value
                    Db().get('activities').ensure_index(
                        [(key, DESCENDING)],
                        {'background': False}
                    )
                search = tmp
                del tmp

            search['isDeleted'] = False
            data = Db().get('activities').find(search)

        except DbError:
            output.error('cannot access db', 503)

        result = []
        if data is None:
                return result

        for tmp in data:
            result.append(Activity(**tmp))

        return result
