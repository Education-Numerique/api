from lxxl.lib.storage import Db, DbError, ObjectId, DESCENDING, ASCENDING
from lxxl.lib.config import Config
from gridfs import NoFile
from gridfs.errors import CorruptGridFile

from lxxl.model.activities import Factory as ActivityFactory


class Factory:

    @staticmethod
    def insert(blobType, release, data, content_type, **args):
        print('insert blobid')
        try:
            blobId = ObjectId()
            dbGrid = Db().getGridFs('blobs')
            dbGrid.put(
                data,
                content_type=content_type,
                filename="%s.%s" % (blobId, release),
                type=blobType,
                blobId=str(blobId),
                release='draft',
                **args
            )

            if 'activity' in args:
                a = ActivityFactory.get(args['activity'])
                if not 'blobs' in a.__dict__[release]:
                    a.__dict__[release]['blobs'] = {}
                if not blobType in a.__dict__[release]['blobs']:
                    a.__dict__[release]['blobs'][blobType] = []

                a.__dict__[release]['blobs'][blobType].append(str(blobId))
                ActivityFactory.update(a)
        except DbError:
            output.error('cannot access db', 503)

        return blobId

    @staticmethod
    def update(blobId, blobType, release, data, content_type, **args):
        try:
            dbGrid = Db().getGridFs('blobs')
            dbGrid.put(
                data,
                content_type=content_type,
                filename="%s.%s" % (blobId, release),
                type=blobType,
                blobId=str(blobId),
                release=release,
                **args
            )
            try:
                oldFile = dbGrid.get_version("%s.%s" % (blobId, release), -2)
                dbGrid.delete(oldFile._id)
            except NoFile:
                pass
            except CorruptGridFile:
                pass
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def getFileIds(**args):
        try:
            collection = Db().get('blobs.files')

            for field in args.keys():
                collection.ensure_index(
                    [(field, DESCENDING)],
                    {'background': False}
                )

            ids = Db().get('blobs.files').find(args, {'_id': True})
            result = []

            for i in ids:
                result.append(str(i['_id']))

            return result
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def getBlobIds(**args):
        try:
            collection = Db().get('blobs.files')

            for field in args.keys():
                collection.ensure_index(
                    [(field, DESCENDING)],
                    {'background': False}
                )

            ids = Db().get('blobs.files').find(args, {'blobId': True})
            result = []

            for i in ids:
                result.append(str(i['blobId']))

            return result
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def publish(blobId):
        try:
            blob = Factory.get(blobId)

            if not blob:
                return False

            metas = blob.__dict__['_file']
            extra = {}
            excludeFields = [
                'blobId', 'chunkSize', 'filename', 'contentType',
                'md5', 'type', 'release', '_id', 'uploadDate',
                'length'
            ]

            for (k, v) in metas.items():
                if k in excludeFields:
                    continue
                extra[k] = v

            Factory.update(
                metas['blobId'],
                metas['type'],
                'published',
                blob.read(),
                metas['contentType'],
                **extra
            )
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def delete(blobId):
        try:
            try:
                dbGrid = Db().getGridFs('blobs')
                thumbnail = dbGrid.get_last_version("%s.draft" % blobId)
                dbGrid.delete(thumbnail._id)
                thumbnail = dbGrid.get_last_version("%s.published" % blobId)
                dbGrid.delete(thumbnail._id)
            except NoFile:
                pass
            except CorruptGridFile:
                pass
        except DbError:
            output.error('cannot access db', 503)

    @staticmethod
    def get(blobId, release='draft'):
        try:
            try:
                blob = None
                dbGrid = Db().getGridFs('blobs')
                blob = dbGrid.get_last_version("%s.%s" % (blobId, release))
            except NoFile:
                pass
            except CorruptGridFile:
                pass
        except DbError:
            output.error('cannot access db', 503)

        return blob
