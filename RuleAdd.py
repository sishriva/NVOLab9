from openstack import connection

data = {
    'auth_url': "http://127.0.0.1/identity",
    'user_domain_name': "sidd",
    'username': "sidd",
    'password': "sidd",
    'project_name': "sidd"
}

def allow_vn(gorup, net1, net2):
    conn = connection.Connection(**data)
    security_groups = list(conn.network.security_groups(name=gorup))
    if not security_groups:
        print(f"Security group '{gorup}' not found.")
        break

    rule = [
        {
            'security_group_id': gorup,
            'direction': 'ingress',
            'protocol': None,
            'remote_ip_prefix': net1,
        },
        {
            'security_group_id': gorup,
            'direction': 'ingress',
            'protocol': None,
            'remote_ip_prefix': net2,
        },
        {
            'security_group_id': gorup,
            'direction': 'egress',
            'protocol': None,
            'remote_ip_prefix': net2,
        }
    ]
    
    for r in rule:
        conn.network.create_security_group_rule(**r)