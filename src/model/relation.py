from bulbs.model import Relationship, NORMAL
from lib.graph import EdgeId, client
from bulbs.property import String
import json

class RelationType(Relationship):
    jsboot_label = "jsboot.relation.type"
    jsboot_id = String(default=EdgeId)

    def getModel(self):
        datas = self.data()
        for k in datas:
            if hasattr(RelationType, k) or not isinstance(datas[k], str):
                continue

            try:
                self._data[k] = json.loads(datas[k])
            except Exception as e:
                pass

        return self.data()
    

class RelationInstance(Relationship):
    jsboot_id = String(default=EdgeId)
    jsboot_label = "jsboot.relation.instance"



class Factory:
    type = client.build_proxy(RelationType)
    instance = client.build_proxy(RelationInstance)