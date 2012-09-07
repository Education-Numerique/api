from lib import router, output
from lib.app import Error, Controller
from model.node import Factory, NodeType, NodeInstance
from model.application import Factory as AppFactory
from model.acl import Factory as AclFactory
from model.pigeon import createType, createModel
from lib.graph import client

class Types(router.Root):

    def create (self, environ, params):
        try:
            datas = Controller().getPostJson()

            if not datas['label']:
                output.error('need label', 400)
        
            user = Factory.instance.index.get_unique(jsboot_id="50364877015bf4208216565b0")
            app = AppFactory.proxy.index.get_unique(jsboot_id="503644a1015bf4208216565a0")
            typeExists = Factory.type.index.count(label=datas['label'])

            if typeExists > 0:
                output.error('endpoint %s exists' % (datas['label']), 403)

            properties = {}

            for (key, value) in datas.items():

                properties[key] = value

                print(key, value)

                if key == 'label':
                    continue


            model = createType('Type', NodeType, properties)

            cType = model.create(**properties)
            AclFactory.instanceOf.create(cType, app)
            AclFactory.ownedBy.create(cType, user)

            output.success(cType.jsboot_id, 202)
        except Error:
            pass
        
        return Controller().getResponse(True)
    
    def info (self, environ, params):
        try:
            print(params['nid'])
            cType = Factory.type.index.get_unique(jsboot_id=params['nid'])

            output.success(cType.data(), 202)
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
            cType = Factory.type.index.get_unique(jsboot_id=params['nid'])

            if not cType:
                output.error('no endpoint %s' % (params['nid']), 404)

            cType.getModel()

            t = createModel('Toto', NodeInstance, cType.data())

            if not datas:
                datas = {}

            datas['jsboot_tid'] = cType.jsboot_id

            try:
                result = t.create(**datas)

                AclFactory.instanceOf.create(result, cType)
                AclFactory.ownedBy.create(result, user)
            except Exception as e:
                output.error('model error %s' % e, 400)

            output.success(result.jsboot_eid, 202)
        except Error:
            pass
        
        return Controller().getResponse(True)
