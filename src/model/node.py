from bulbs.model import Node, NORMAL
from lib.graph import VertexId, client
from bulbs.property import String, Document
import json

class NodeType(Node):
    jsboot_type = "jsboot.node.type"
    jsboot_id = String(default=VertexId)
    label = String()

    def getModel(self):
        datas = self.data()
        for k in datas:
            if hasattr(NodeType, k) or not isinstance(datas[k], str):
                continue

            try:
                self._data[k] = json.loads(datas[k])
            except:
                pass

        return self.data()
        
    

class NodeInstance(Node):
    jsboot_type = "jsboot.node.instance"
    jsboot_id = String(default=VertexId)
    jsboot_tid = String()



class Factory:
    type = client.build_proxy(NodeType)
    instance = client.build_proxy(NodeInstance)