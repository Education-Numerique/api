from lxxl.lib.storage import Db, DbError, DESCENDING, ASCENDING
from lxxl.lib.config import Config


class Activity:

    def __init__(self, **entries):
        self.id = None
        self.publicationData = None
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

        self.__dict__.update(entries)

    def toObject(self):
        obj = self.__dict__.copy()
        del obj['_id']
        obj['id'] = str(obj['id'])
        return obj


class Factory:

    @staticmethod
    def new(activity):
        if not isinstance(activity, Activity):
            raise Exception('invalid activity object', activity)

        c = Db().get('activities')

        id = c.insert(activity.__dict__, True)
        activity.id = id
