from __future__ import absolute_import
import os
from netmiko import ConnectHandler
import logging
from openstack import connection
import time

from ryu.services.protocols.bgp.bgpspeaker import (
    RF_VPN_V4 as VPNv4,
    RF_VPN_V6 as VPNv6,
    RF_VPNV4_FLOWSPEC as VPNv4FlowSpec,
    RF_VPNV6_FLOWSPEC as VPNv6FlowSpec,
    ESI_TYPE_LACP as LacpESIType,
    ESI_TYPE_MAC_BASED as MacBasedESIType,
    EVPN_ETH_AUTO_DISCOVERY as EthAutoDiscovery,
    TUNNEL_TYPE_VXLAN as VxlanTunnel,
    EVPN_MULTICAST_ETAG_ROUTE as MulticastEtagRoute,
    EVPN_ETH_SEGMENT as EthSegment,
    EVPN_IP_PREFIX_ROUTE as IpPrefixRoute,
    FLOWSPEC_FAMILY_VPNV4 as VPNv4FlowSpecFamily,
    FLOWSPEC_FAMILY_VPNV6 as VPNv6FlowSpecFamily,
    FLOWSPEC_FAMILY_L2VPN as L2VPNFlowSpecFamily,
    FLOWSPEC_TA_SAMPLE as SampleTA,
    FLOWSPEC_TA_TERMINAL as TerminalTA,
    FLOWSPEC_TPID_TI as TpidTI,
    FLOWSPEC_TPID_TO as TpidTO,
    REDUNDANCY_MODE_SINGLE_ACTIVE as SingleActiveRedundancyMode
)

SSHConfig = {
    'port': 4990,
    'username': 'sidd',
    'host': 'sidd',
    'password': 'sidd'
}

BGPConfig = {
    'local_as': 500,
    'router_id': '50.0.0.1',
    'local_pref': 200,
    'bgp_server_hosts': ['50.0.0.1', '::1'],
    'neighbors': [
        {
            'address': '50.0.0.2',
            'remote_as': 600,
            'enable_ipv4': True,
            'enable_ipv6': True
        }
    ],
    'vrfs': [],
    'routes': []
}

LoggingConfig = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s [%(process)d %(thread)d] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)s %(message)s'
        },
        'stats': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console_stats': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'stats'
        },
        'stats_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('.', 'statistics_bgp.log'),
            'maxBytes': '10000000',
            'formatter': 'stats'
        },
    },
    'loggers': {
        'bgpspeaker': {
            'handlers': ['console', 'log_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'stats': {
            'handlers': ['stats_file', 'console_stats'],
            'level': 'INFO',
            'propagate': False,
            'formatter': 'stats',
        },
    },
    'root': {
        'handlers': ['console', 'log_file'],
        'level': 'DEBUG',
        'propagate': True,
    },
}

def configure_bgp(target):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        connection_params = {
            'device_type': 'cisco_ios',
            'host': target['ip'],
            'username': target['sidd'],
            'password': target['sidd']
        }
        net_connect = ConnectHandler(**connection_params)
        net_connect.send_command_timing('scp bgp_config.py {target["username"]}@{target["ip"]}:/home/{target["username"]}/bgp_config.py')
        net_connect.send_command_timing("sudo ryu-manager --verbose --bgp-app-config-file bgp_config.py ryu/services/protocols/bngp/application.py ryu/ryu/app/simple_switch_13.py &")
        net_connect.send_command_timing("docker run -it . /bin/bash")

        cmds = [
            "sudo ovs-vsctl add-br mybridge",
            "sudo ovs-vsctl add-port mybridge eth0",
            "sudo ovs-vsctl set bridge mybridge protocols=OpenFlow13",
            f"sudo ovs-vsctl set-controller mybridge tcp:{target['ip']}:6633"
        ]
        for command in cmds:
            net_connect.send_command(command)
        return True  
    except Exception as e:
        return False 

def setup_frr(router_info):
    bgp_configuration = ['configure terminal','router bgp 500','neighbor 50.0.0.2 remote-as 600','exit']
    z = ConnectHandler(**router_info)
    scp_command = f'scp Dockerfile {router_info["username"]}@{router_info["ip"]}:/home/{router_info["username"]}/Dockerfile'
    output = z.send_command_timing(scp_command)
    print("File uploaded successfully.")
    z.send_command_timing("docker run -it . /bin/bash")
    z.send_command_timing("service frr start")
    z.send_config_set(bgp_configuration)

OpenStackAuth = {
    'auth_url': "http://198.11.21.22/identity",
    'project_name': "Lab9",
    'username': "admin",
    'password': "secret"
}

def launch_instance(myinstance_name, im_name, conf_name, keypair_name, network_id):
    conn = connection.Connection(**OpenStackAuth)
    im = conn.compute.find_im(im_name)
    conf = conn.compute.find_conf(conf_name)
    key = conn.compute.find_keypair(name_or_id=keypair_name)

    myinstance = conn.compute.create_server(
        name=myinstance_name,
        im_id=im.id,
        conf_id=conf.id,
        networks=[{"uuid": network_id}],
        key_name=keypair.name
    )
    conn.compute.wait_for_server(myinstance)
    net = conn.network.find_network(name_or_id='public')

    net_id = net.id

    floating_ip = conn.network.create_ip(floating_network_id=net_id)
    conn.compute.add_floating_ip_to_server(myinstance, floating_ip.fip)

    myinstance_ip = floating_ip.fip

def allow_icmp(group):
    conn = connection.Connection(**auth_details)
    security_groups = list(conn.network.security_groups(name=group))
    if not security_groups:
        print(f"Security group '{group}' not found.")
        return

    sgid = security_groups[0].id

    icmp_rules = [
        {
            'security_group_id': sgid,
            'direction': 'ingress',
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0'
        },
        {
            'security_group_id': sgid,
            'direction': 'egress',
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0'
        }
    ]
    
    for icmp_rule in icmp_rules:
        conn.network.create_security_group_rule(**icmp_rule)



creds = {
    'auth_url': "http://198.11.21.22/identity",
    'user_domain_name': "default",
    'username': "admin",
    'password': "secret",
    'project_name': "Lab9"
}

def allow_vn(group, net1, net2):
    conn = connection.Connection(**creds)
    security_groups = list(conn.network.security_groups(name=group))
    t = security_groups[0].id
    vn_rules = [
        {
            'security_group_id': t,
            'direction': 'ingress',
            'protocol': None,
            'remote_ip_prefix': net1,
        },{'security_group_id': t,'direction': 'ingress','protocol': None,
            'remote_ip_prefix': net2,
        },
        {
            'security_group_id': t,'direction': 'egress','protocol': None,
            'remote_ip_prefix': net2,
        }
    ]
    
    for rule in vn_rules:
        conn.network.create_security_group_rule(**rule)

def allow_icmp(group):
    conn = connection.Connection(**creds)
    security_groups = list(conn.network.security_groups(name=group))
    t = security_groups[0].id
    icmp_rules = [
        {
            'security_group_id': t,
            'direction': 'ingress',
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0'
        },
        {
            'security_group_id': t,
            'direction': 'egress',
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0'
        }
    ]
    for r in icmp_rules:
        conn.network.create_security_group_rule(**r)

#Sources:
#ChatGPT
#Copilot
#https://docs.openstack.org/openstacksdk/latest/user/guides/connect.html
#https://docs.frrouting.org/en/latest/bgp.html
#https://docs.openstack.org/openstacksdk/latest/user/guides/network.html
#https://docs.openstack.org/openstacksdk/latest/user/

