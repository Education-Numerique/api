from bulbs.model import Relationship, NORMAL
from lib.graph import EdgeId, client
from bulbs.property import String

class DefaultRead(Relationship):
    jsboot_label = "jsboot.acl.default.read"
    jsboot_id = String(default=EdgeId)

class DefaultWrite(Relationship):
    jsboot_label = "jsboot.acl.default.write"
    jsboot_id = String(default=EdgeId)

class DefaultDelete(Relationship):
    jsboot_label = "jsboot.acl.default.delete"
    jsboot_id = String(default=EdgeId)

class DefaultMaster(Relationship):
    jsboot_label = "jsboot.acl.default.master"
    jsboot_id = String(default=EdgeId)
    
class ReadableBy(Relationship):
    jsboot_label = "jsboot.acl.readableBy"
    jsboot_id = String(default=EdgeId)

class WritableBy(Relationship):
    jsboot_label = "jsboot.acl.writableBy"
    jsboot_id = String(default=EdgeId)

class DeletableBy(Relationship):
    jsboot_label = "jsboot.acl.deletableBy"
    jsboot_id = String(default=EdgeId)

class MasterableBy(Relationship):
    jsboot_label = "jsboot.acl.masterableBy"
    jsboot_id = String(default=EdgeId)

class CanCreate(Relationship):
    jsboot_label = "jsboot.acl.canCreate"
    jsboot_id = String(default=EdgeId)

class OwnedBy(Relationship):
    jsboot_label = "jsboot.acl.ownedBy"
    jsboot_id = String(default=EdgeId)

class InstanceOf(Relationship):
    jsboot_label = "jsboot.acl.instanceOf"
    jsboot_id = String(default=EdgeId)


class Factory:
    defaultRead = client.build_proxy(DefaultRead)
    defaultWrite = client.build_proxy(DefaultWrite)
    defaultDelete = client.build_proxy(DefaultDelete)
    defaultMaster = client.build_proxy(DefaultMaster)
    readableBy = client.build_proxy(ReadableBy)
    writaleBy = client.build_proxy(WritableBy)
    deletableBy = client.build_proxy(DeletableBy)
    masterableBy = client.build_proxy(MasterableBy)
    canCreate = client.build_proxy(CanCreate)
    ownedBy = client.build_proxy(OwnedBy)
    instanceOf = client.build_proxy(InstanceOf)
