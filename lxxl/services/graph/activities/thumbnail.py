from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller
from lxxl.lib.storage import Db, DbError
from lxxl.model.activities import Activity, Factory as ActivityFactory
from lxxl.model.blob import Factory as BlobFactory


class Thumbnail(router.Root):

    def save(self, environ, params):
        try:
            req = Controller().getRequest()
            router = Controller().getRouter()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('activity not found', 404)

            cT = req.headers['Content-Type'] or 'application/octet-stream'
            cT = 'image/jpeg'
            blobId = BlobFactory.getBlobIds(
                activity=params['rid'],
                release="draft",
                type="thumbnail"
            )

            if not len(blobId):
                blobId = BlobFactory.insert(
                    'thumbnail',
                    'draft',
                    req.body,
                    cT,
                    activity=params['rid']
                )
            else:
                blobId = blobId[0]
                BlobFactory.update(
                    blobId,
                    'thumbnail',
                    'draft',
                    req.body,
                    cT,
                    activity=params['rid']
                )

            resultUrl = router.getRoute('graph.Blob.fetch', {
                'version': params['version'],
                'bid': str(blobId),
                'release': 'draft'
            })
            output.success({
                'url': resultUrl,
                'blobId': str(blobId)
            }, 201)
        except Error:
            pass

        return Controller().getResponse(True)

    def delete(self, environ, params):
        try:
            req = Controller().getRequest()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('activity not found', 404)

            cT = req.headers['Content-Type'] or 'application/octet-stream'
            dbGrid = Db().getGridFs('thumbnail')

            #clean old stuff
            try:
                thumbnail = dbGrid.get_last_version(params['rid'])
                dbGrid.delete(thumbnail._id)
            except NoFile:
                pass
            except CorruptGridFile:
                pass

            a.hasThumbnail = False
            ActivityFactory.update(a)

            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def fetch(self, environ, params):
        try:
            req = Controller().getRequest()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('activity not found', 404)

            dbGrid = Db().getGridFs('thumbnail')
            BlobFactory.publish('50bb679928357e8518eec681')
            #clean old stuff
            try:
                thumbnail = dbGrid.get_last_version(params['rid'])
            except (NoFile or CorruptGridFile):
                output.error('thumbnail not found', 404)

            resp = Controller().getResponse()
            resp.headers['Content-Type'] = thumbnail.content_type
            resp.body = thumbnail.read()

        except Error:
            pass

        return Controller().getResponse(True)
