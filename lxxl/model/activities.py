from lxxl.lib.storage import Db, DbError, ObjectId, DESCENDING, ASCENDING
from lxxl.lib.config import Config
import time


class Activity:

    def __init__(self, **entries):
        self.id = None
        self.publicationDate = None
        self.creationDate = None
        self.isPublished = False

        self.hasThumbnail = False
        self.seenCount = 0
        self.attachmentsCount = 0

        self.author = None
        self.contributors = []
        self.extraContributors = []

        self.title = None
        self.description = None
        self.level = None
        self.matter = None
        self.duration = None
        self.difficulty = None
        self.category = []

        self.publishedPages = []
        self.draftedPages = []

        self.deleted = False
        self.reported = False

        self.merge(**entries)

    def publish(self, publish=True):
        if publish:
            self.isPublished = True
            self.publicationDate = int(time.time())
            self.publishedPages = self.draftedPages
        else:
            self.isPublished = False
            self.publicationDate = None
            self.publishedPages = []

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

    def merge(self, **entries):
        entries = entries.copy()
        if '_id' in entries:
            self.id = entries['_id']
            del entries['_id']

        if 'pages' in entries:
            self.draftedPages = entries['pages']
            del entries['pages']

        self.__dict__.update(entries)

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

            id = c.insert(activity.toDatabase(), True)
            activity.id = id
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def delete(activity):
        if not isinstance(activity, Activity):
            raise Exception('invalid activity object', activity)
        try:
            c = Db().get('activities')
            activity.deleted = True
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

            search['deleted'] = False
            data = Db().get('activities').find_one(search)

        except DbError:
            output.error('cannot access db', 503)

        if data is None:
                return None

        return Activity(**data)
