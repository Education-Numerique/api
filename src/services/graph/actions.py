from lib import router, output
from lib.app import Error, Controller
from model.relation import Factory, RelationType, RelationInstance
from model.node import Factory as NodeFactory
from model.application import Factory as AppFactory
from model.acl import Factory as AclFactory
from model.pigeon import createType, createModel
from lib.graph import client

class Actions(router.Root):

    def create (self, environ, params):
        try:
            datas = Controller().getPostJson()

            if not 'label' in datas or not 'jsboot_target' in datas:
                output.error('need label / jsboot_target', 400)
        
            user = Factory.instance.index.get_unique(jsboot_id="50364877015bf4208216565b0")
            app = AppFactory.proxy.index.get_unique(jsboot_id="503644a1015bf4208216565a0")
            baseNode = NodeFactory.type.index.get_unique(jsboot_id=params['nid'])
            targetNode = NodeFactory.type.index.get_unique(jsboot_id=datas['jsboot_target'])

            if not baseNode:
                output.error('unknown node %s' % params['nid'], 404)

            if not targetNode:
                output.error('unknown target node %s' % datas['jsboot_target'], 400)

            typeExists = Factory.type.index.count(label=datas['label'])

            if typeExists > 0:
                output.error('endpoint %s exists' % (datas['label']), 403)

            properties = {}

            for (key, value) in datas.items():

                if key == 'jsboot_target':
                    continue

                if key == 'label':
                    key = 'jsboot_label'
                properties[key] = value

                print(key, value)

                


            model = createType('Type', RelationType, properties)
            cType = model.create(baseNode, targetNode, properties)

            output.success(cType.jsboot_eid, 201)
        except Error:
            pass
        
        return Controller().getResponse(True)
    
    def info (self, environ, params):
        try:
            cType = Factory.type.index.get_unique(jsboot_id=params['nid'])

            output.success(cType.getModel(), 200)
        except Error:
            pass
        
        return Controller().getResponse(True)

    def list(self, environ, params):
        try:
            app = AppFactory.proxy.index.get_unique(jsboot_id="503644a1015bf4208216565a0")
            script = client.scripts.get('get_model')
            types = client.gremlin.query(script, { '_id' : app.jsboot_eid})

            result = []
            for model in types:
                result.append(model.getModel())

            output.success(result, 200)
        except Error:
            pass
        
        return Controller().getResponse(True)

    def createInstance(self, environ, params):
        try:
            datas = Controller().getPostJson()

            user = Factory.instance.index.get_unique(jsboot_id="50364877015bf4208216565b0")
            app = AppFactory.proxy.index.get_unique(jsboot_id="503644a1015bf4208216565a0")
            originNode = NodeFactory.instance.index.get_unique(jsboot_id=params['nid'])

            if not originNode:
                output.error('no node %s' % (params['nid']), 404)

            actionType = Factory.type.index.get_unique(jsboot_id=params['aid'])

            if not actionType:
                output.error('no action type %s' % params['aid'], 404)

            targetNode = NodeFactory.instance.index.get_unique(jsboot_id=datas['jsboot_target'])

            if not targetNode:
                output.error('unknown targeted node %s' % (datas['jsboot_target']))

            t = createModel('RelationInstance', RelationInstance, actionType.getModel())

            datas['jsboot_tid'] = actionType.jsboot_id
            del datas['jsboot_target']

            # try:
            result = t.create(originNode, targetNode, datas)

            output.success(result.data(), 201)
        except Error:
            pass
        
        return Controller().getResponse(True)
