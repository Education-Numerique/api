from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller
from lxxl.model.activities import Activity, Factory as ActivityFactory
from lxxl.model.users import Factory as UserFactory
from lxxl.model.blob import Factory as BlobFactory
import time


class Activities(router.Root):

    def create(self, environ, params):
        try:
            req = Controller().getRequest()

            if not req.json:
                output.error('invalid json', 400)

            a = Activity()
            a.saveDraft(**req.json)
            a.setAuthor(UserFactory.get(Controller().getUid()))
            a.creationDate = int(time.time())
            ActivityFactory.new(a)
            output.success(a.toObject(), 201)
        except Error:
            pass

        return Controller().getResponse(True)

    def fetch(self, environ, params):
        try:
            req = Controller().getRequest()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def fetchPublic(self, environ, params):
        try:
            req = Controller().getRequest()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            if not a.isPublished:
                output.error('unauthorized access', 403)

            del a.draft
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def list(self, environ, params):
        try:
            req = Controller().getRequest()
            criteria = {}

            if params['filter'] == 'mine':
                criteria['author.uid'] = Controller().getUid()
            elif params['filter'] == 'reported':
                criteria['isReported'] = True
            elif params['filter'] == 'published':
                criteria['isPublished'] = True

            for key in req.GET:
                criteria[key] = req.GET[key]

            search = ActivityFactory.list(criteria)
            result = []
            for activity in search:
                result.append(activity.toObject())

            output.success(result, 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def delete(self, environ, params):
        try:
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            ActivityFactory.delete(a)
            output.success('Activity deleted', 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def publish(self, environ, params):
        try:
            req = Controller().getRequest()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            a.publish()
            for (blobType, values) in a.published['blobs'].items():
                for blobId in values:
                    BlobFactory.publish(blobId)

            ActivityFactory.update(a)
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def unpublish(self, environ, params):
        try:
            req = Controller().getRequest()
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            for (blobType, values) in a.published['blobs'].items():
                for blobId in values:
                    BlobFactory.delete(blobId, 'published')

            a.publish(False)
            ActivityFactory.update(a)
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def save(self, environ, params):
        try:
            req = Controller().getRequest()

            if not req.json:
                output.error('invalid json', 400)

            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            a.saveDraft(**req.json)
            ActivityFactory.update(a)
            output.success(a.toObject(), 200)

        except Error:
            pass

        return Controller().getResponse(True)

    def report(self, environ, params):
        try:
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            a.isReported = True
            ActivityFactory.update(a)
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def unreport(self, environ, params):
        try:
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            a.isReported = False
            ActivityFactory.update(a)
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def seen(self, environ, params):
        try:
            a = ActivityFactory.get(params['rid'])
            if not a:
                output.error('not found', 404)

            ActivityFactory.incSeen(a)
            output.success(a.toObject(), 200)
        except Error:
            pass

        return Controller().getResponse(True)
