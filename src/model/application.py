from bulbs.model import Node, NORMAL
from lib.graph import VertexId, client
from bulbs.property import String



class Application(Node):
    jsboot_type = "jsboot.application"
    jsboot_id = String(default=VertexId)
    name = String()


class Factory:
    proxy = client.build_proxy(Application)
