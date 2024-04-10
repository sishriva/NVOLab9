from openstack import connection
router_alias = "Lab9Router"
network_alias = 'MyNetwork1'
subnet_alias = 'MySubnet1'
cidr_alias = '10.0.0.1/24'
data = {'auth_url': "http://198.11.21.22/identity",'project_name': "Lab9",'username': "admin",'password': "secret"}
def create_network(network_name, subnet_name, cidr, router_name):
    conn = connection.Connection(**data)
    ip_version = 4
    net = conn.network.create_network(name=network_name)
    mask = conn.network.create_subnet(name=subnet_name,network_id=net.id,cidr=cidr,ip_version=ip_version)
    router = conn.network.find_router(router_name)
    conn.network.add_interface_to_router(router, subnet_id=mask.id)
    return net.id
