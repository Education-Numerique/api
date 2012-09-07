

def get_model(_id) {
    return g.v(_id).in('jsboot.acl.instanceOf');
}


def get_instance_stats(_id) {
    m = [:];
    g.v(_id).bothE().jsboot_label.groupCount(m);
    return m;
}