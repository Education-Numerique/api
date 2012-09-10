from lib import router, output
from lib.app import Error, Controller
import requests


class Buffalo(router.Root):
    SESSION = requests.session()

    def zebuit(self, environ, params):
        try:
            req = Controller().getRequest()
            wildResponse = Controller().getResponse()

            sendHeaders = {}
            for (k, v) in req.headers.items():
                if not v:
                    continue

                if k.lower() in ['host', 'keep-alive']:
                    continue

                sendHeaders[k] = v

            try:
                resp = Buffalo.SESSION.request(req.method, '%s%s' % (
                    'http://localhost:8082',
                    req.path_qs
                ), headers=sendHeaders)
            except:
                output.error('Auth Backend fail', 503)

            if int(resp.status_code / 100) != 2:
                for (k, v) in resp.headers.items():
                    wildResponse.headers[k] = v
                output.success(resp.json, resp.status_code)
                raise Error('break')

            for (k, v) in resp.headers.items():
                if 'x-lxxl' in k.lower():
                    sendHeaders[k] = v

            datas = {}
            for (k, v) in req.POST.items():
                datas[k] = v

            try:
                resp = Buffalo.SESSION.request(req.method, '%s%s' % (
                    'http://localhost:8083',
                    req.path_qs
                ), headers=sendHeaders, data=datas)
            except:
                output.error('Graph backend fail', 503)

            for (k, v) in resp.headers.items():
                wildResponse.headers[k] = v

            output.success(resp.json, resp.status_code)
        except Error:
            pass

        return Controller().getResponse(True)
