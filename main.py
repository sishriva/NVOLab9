from create_new_instance import *
from openstack import connection
from dockerfile_parse import *
from bgp_vm_configuration_frr_rule_add import *


network1_id = create_network("MyNetwork1", "MySubnet1", "10.0.0.0/24", "Lab9Router")

network2_id = create_network("MyNetwork2", "MySubnet2", "20.0.0.0/24", "Lab9Router")

allow_all_between_vn("default", "10.0.0.0/24", "20.0.0.0/24")

one = new_vm(vm_name="Instance1", image_name="mini", flavor_name="m1.small", keypair_name="mykeyPair", network_id=network1_id)
two = new_vm(vm_name="Instance2", image_name="mini", flavor_name="m1.small", keypair_name="mykeyPair", network_id=network1_id)
three=new_vm(vm_name="Instance3", image_name="mini", flavor_name="m1.small", keypair_name="mykeyPair", network_id=network2_id)

instance2 = {'device_type': 'linux','host': two,'username': 'new_username','password': 'new_password'}
docker_call(instance2)
bgp_Call(instance2)