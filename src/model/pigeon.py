from bulbs.property import Document, String, List, Float, Integer, Long, DateTime
from bulbs.utils import current_datetime
from lib.graph import client


def createType(name, model, properties):
    stuff = {}

    for p in properties:
        
        if hasattr(model, p):
            continue

        stuff[p] = Document()

    tmpModel = type(name, (model,), stuff)

    return client.build_proxy(tmpModel)

def createModel(name, model, properties):

    stuff = {}

    for p in properties:

        
        if hasattr(model, p) or not isinstance(properties[p], dict):
            continue
            
        customeType = String

        if (properties[p]['type'].lower() == 'string'):
            customeType = String
        elif (properties[p]['type'].lower() == 'integer'):
            customeType = Integer
        elif (properties[p]['type'].lower() == 'long'):
            customeType = Long
        elif (properties[p]['type'].lower() == 'array'):
            customeType = List
        elif (properties[p]['type'].lower() == 'document'):
            customeType = Document
        elif (properties[p]['type'].lower() == 'float'):
            customeType = Float
        elif (properties[p]['type'].lower() == 'datetime'):
            customeType = DateTime
            if properties[p]['default'] == "now":
                properties[p]['default'] = current_datetime

        stuff[p] = customeType(nullable=properties[p]['mandatory'], default=properties[p]['default'])
 

    tmpModel = type(name, (model,), stuff)

    return client.build_proxy(tmpModel)


