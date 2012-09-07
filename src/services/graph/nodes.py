from lib import router, output
from lib.app import Error, Controller
from lib.graph import client
from model.node import Factory

class Nodes(router.Root):

    def fetch (self, environ, params):
        try:
            node = Factory.instance.index.get_unique(jsboot_id=params['nid'])
            script = client.scripts.get('get_instance_stats')
            stats = client.gremlin.execute(script, { '_id' : node.jsboot_eid})

            node.jsboot_actions = stats.content
            output.success(node.data(), 200)
        except Error:
            pass
        
        return Controller().getResponse(True)

    def update (self, environ, params):
        try:
            output.success('node update', 202)
        except Error:
            pass
        
        return Controller().getResponse(True)


    def delete (self, environ, params):
        try:
            output.success('node delete', 202)
        except Error:
            pass
        
        return Controller().getResponse(True)
    
