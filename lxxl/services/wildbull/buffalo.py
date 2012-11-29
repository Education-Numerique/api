from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller
import requests

"""
  set resp.http.Access-Control-Allow-Origin = req.http.origin;
  set resp.http.Access-Control-Allow-Methods = "POST, GET, HEAD, DELETE";
  set resp.http.Access-Control-Expose-Headers = "X-WWW-Authenticate, X-UID, Date, Server, Location";
  set resp.http.Access-Control-Allow-Headers = "X-IID, Authorization, X-Requested-With, X-Signature, Content-Type, X-Gate-Origin";
  set resp.http.Access-Control-Max-Age = 10;
  // This is freaky dangerous debuging trixing
  if(req.http.User-Agent == "Talk to the hand"){
   set resp.http.Access-Control-Allow-Methods = resp.http.Access-Control-Allow-Methods + ", PUT, CONNECT, TRACE, OPTIONS, ROX-PURGE, WHATEVER";
   set resp.http.Access-Control-Allow-Headers = resp.http.Access-Control-Allow-Headers + ", Accept, Range, Expect, Allow, User-Agent, Host";
   set resp.http.Access-Control-Expose-Headers = resp.http.Access-Control-Expose-Headers + ", D-vcl";

"""

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

                if k.lower() in ['accept-encoding', 'keep-alive', 'content-length', 'transfer-encoding']:
                    continue

                if '_' in k:
                    continue

                sendHeaders[k] = v

            if req.method.lower() == 'get':
                data = None
            else:
                data = {}

            try:
                resp = requests.request(req.method, '%s%s' % (
                    'http://localhost:8082',
                    req.path_qs
                ), headers=sendHeaders, data=data, prefetch=True)

            except:
                output.error('Auth Backend fail', 503)

            if int(resp.status_code / 100) != 2:
                for (k, v) in resp.headers.items():
                    wildResponse.headers[k.lower()] = v
                
                if 'X-Requested-With' in req.headers and 'www-authenticate' in wildResponse.headers:
                    wildResponse.headers['X-WWW-Authenticate'] = wildResponse.headers['www-authenticate']
                    del wildResponse.headers['www-authenticate']

                output.success(resp.json, resp.status_code)
                raise Error('break')

            for (k, v) in resp.headers.items():
                if 'x-lxxl' in k.lower():
                    sendHeaders[k] = v

            datas = None
            if req.body:
                datas = req.body

            try:
                resp = requests.request(req.method, '%s%s' % (
                    'http://localhost:8083',
                    req.path_qs
                ), headers=sendHeaders, data=datas, prefetch=True)
            except:
                output.error('Graph backend fail', 503)

            for (k, v) in resp.headers.items():
                wildResponse.headers[k] = v

            output.success(resp.json, resp.status_code)
        except Error:
            pass

        return Controller().getResponse(True)
