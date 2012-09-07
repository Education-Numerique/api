from bson.objectid import ObjectId
from bulbs.neo4jserver import Graph, NEO4J_URI, Config, DEBUG
config = Config(NEO4J_URI)
config.type_var = 'jsboot_type'
config.label_var = 'jsboot_label'
config.id_var = 'jsboot_eid'
#config.set_logger(DEBUG)
import logging

a = logging.getLogger()
#a.setLevel(logging.DEBUG)
client = Graph(config)

client.scripts.update('scripts/gremlin.groovy')


class VertexId(ObjectId):

	def __init__(self): 
		super().__init__()
		self.__id = super().__str__() + "0"

	def __str__(self):
		return self.__id

	def __repr__(self):
		return "VertexId('%s')" % (str(self),)


class EdgeId(ObjectId):

	def __init__(self): 
		super().__init__()
		self.__id = super().__str__() + "1"

	def __str__(self):
		return self.__id

	def __repr__(self):
		return "EdgeId('%s')" % (str(self),)