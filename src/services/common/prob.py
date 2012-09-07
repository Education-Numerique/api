from lib import router, output
from lib.app import Error, Controller

class Prob(router.Root):
    
    def alive (self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass
        
        return Controller().getResponse(True) 
    
