from lib import router, output
from lib.app import Error, Controller


class Handler(router.Root):

    def read (self, environ, params):
        try:
            output.success('woooohooooo', 202)
        except Error:
            pass
        
        return Controller().getResponse(True) 

    def create (self, environ, params):
        try:
            output.success('woooohooooo', 202)
        except Error:
            pass
        
        return Controller().getResponse(True)

    def update (self, environ, params):
        try:
            output.success('woooohooooo', 202)
        except Error:
            pass
        
        return Controller().getResponse(True) 

    def delete (self, environ, params):
        try:
            output.success('woooohooooo', 202)
        except Error:
            pass
        
        return Controller().getResponse(True) 
    
