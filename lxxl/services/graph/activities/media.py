from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller
from lxxl.lib.storage import Db, DbError
from lxxl.model.activities import Activity, Factory as ActivityFactory
from lxxl.model.blob import Factory as BlobFactory


class Media(router.Root):

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
                type="media"
            )

            if not len(blobId):
                blobId = BlobFactory.insert(
                    'media',
                    'draft',
                    req.body,
                    cT,
                    activity=params['rid']
                )
            else:
                blobId = blobId[0]
                BlobFactory.update(
                    blobId,
                    'media',
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
