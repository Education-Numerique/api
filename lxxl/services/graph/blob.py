from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller
from lxxl.model.blob import Factory as BlobFactory


class Blob(router.Root):

    def fetch(self, environ, params):
        try:
            req = Controller().getRequest()
            b = BlobFactory.get(params['bid'], params['release'])
            if not b:
                output.error('blob not found', 404)

            resp = Controller().getResponse()
            resp.headers['Content-Type'] = b.content_type
            resp.body = b.read()
        except Error:
            pass

        return Controller().getResponse(True)

    def update(self, environ, params):
        try:
            req = Controller().getRequest()
            router = Controller().getRouter()
            b = BlobFactory.get(params['bid'])
            if not b:
                output.error('blob not found', 404)

            cT = req.headers['Content-Type'] or 'application/octet-stream'

            BlobFactory.update(
                params['bid'],
                b.type,
                'draft',
                req.body,
                cT,
                activity=b.activity
            )

            resultUrl = router.getRoute('graph.Blob.fetch', {
                'version': params['version'],
                'bid': params['bid'],
                'release': 'draft'
            })
            output.success({
                'url': resultUrl,
                'blobId': params['bid']
            }, 202)
        except Error:
            pass

        return Controller().getResponse(True)

    def delete(self, environ, params):
        try:
            b = BlobFactory.get(params['bid'])
            if not b:
                output.error('blob not found', 404)

            BlobFactory.delete(params['bid'])
            output.success('blob deleted', 202)
        except Error:
            pass

        return Controller().getResponse(True)
