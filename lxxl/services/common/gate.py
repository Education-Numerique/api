from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller
import requests


class Gate(router.Root):

    def fetch(self, environ, params):
        try:
            host = "https://api.education-et-numerique.fr"
            path = "/jsboot.js/%s/gate.html" % (params['gate'])
            gate = requests.get(host + path, verify=False)

            resp = Controller().getResponse()
            resp.text = gate.content.decode('utf-8')
            resp.headers['Content-type'] = 'text/html'
        except Error:
            pass

        return Controller().getResponse(True)
