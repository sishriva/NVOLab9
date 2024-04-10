from openstack import connection

OpenStackAuth = {'auth_url': "http://198.11.21.22/identity", 'project_name': "Lab9", 'username': 'admin', 'password': "secret", 'user_domain_name': "default"}

def launch_instance(vm, image, flavour, key, subnet):
    conn = connection.Connection(**OpenStackAuth)
    image = conn.compute.find_image(image)
    flavor = conn.compute.find_flavor(flavour)

    existing_keypair = conn.compute.find_keypair(name_or_id=key)

    keypair = None
    if existing_keypair:
        keypair = existing_keypair
    else:
        keypair = conn.compute.create_keypair(name=key)

    vm = conn.compute.create_server(name=vm,image_id=image.id,flavor_id=flavor.id,networks=[{"uuid": subnet}],key_name=keypair.name)
    conn.compute.wait_for_server(vm)
    opennetwork = conn.network.find_network(name_or_id='public')
    public_subnet = opennetwork.id
    floating_ip = conn.network.create_ip(floating_subnet=public_subnet)
    conn.compute.add_floating_ip_to_server(vm, floating_ip.floating_ip_address)
    vm_ip = floating_ip.floating_ip_address
