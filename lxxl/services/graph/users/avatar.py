from lxxl.lib import router, output
from lxxl.lib.app import Controller, Error
from lxxl.lib.config import Config
from lxxl.lib.flush import FlushRequest
from lxxl.lib.storage import Db, DbError
from lxxl.model.blob import Factory as BlobFactory
from lxxl.model.users import Factory as UserFactory


class Avatar(router.Root):

    def get(self, environ, params):
        try:
            req = Controller().getRequest()
            blobId = BlobFactory.getBlobIds(
                user=params['uid'],
                release='published',
                type="avatar"
            )

            if not len(blobId):
                output.error('avatar not found', 404)

            blobId = blobId.pop()

            b = BlobFactory.get(blobId, 'published')
            resp = Controller().getResponse()
            resp.headers['Content-Type'] = b.content_type
            resp.body = b.read()
        except Error:
            pass

        return Controller().getResponse(True)

    def set(self, environ, params):
        try:
            Controller().checkToken()
            req = Controller().getRequest()
            router = Controller().getRouter()
            u = UserFactory.get(params['uid'])
            if not u:
                output.error('user not found', 404)

            cT = req.headers['Content-Type'] or 'application/octet-stream'
            blobId = BlobFactory.getBlobIds(
                user=params['uid'],
                release='published',
                type="avatar"
            )

            if not len(blobId):
                blobId = BlobFactory.insert(
                    'avatar',
                    'published',
                    req.body,
                    cT,
                    user=params['uid']
                )
            else:
                blobId = blobId[0]
                BlobFactory.update(
                    blobId,
                    'avatar',
                    'published',
                    req.body,
                    cT,
                    user=params['uid']
                )

            UserFactory.setAvatar(u.uid, True)
            resultUrl = router.getRoute('graph.Blob.fetch', {
                'version': params['version'],
                'bid': str(blobId),
                'release': 'published'
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
            Controller().checkToken()

            if Controller().getApiType() != 1:
                output.error('Not your api business', 403)

            u = UserFactory.get(params['uid'])
            if not u:
                output.error('user not found', 404)

            uid = params['uid']

            blobId = BlobFactory.getBlobIds(
                user=params['uid'],
                release='published',
                type="avatar"
            )

            if not len(blobId):
                output.error('avatar not found', 404)

            blobId = blobId.pop()
            BlobFactory.delete(blobId, 'published')

            UserFactory.setAvatar(u.uid, False)

            output.success('avatar deleted', 200)
        except Error:
            pass

        return Controller().getResponse(True)
