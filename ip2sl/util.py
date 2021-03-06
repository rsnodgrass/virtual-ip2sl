import logging

import os
import sys
import yaml

def get_host(config):
    # must be externally accessible and routable IP (not 0.0.0.0 or localhost)
    host = '0.0.0.0' # invalid default except for testing

    if ('ip2sl' in config and 'ip' in config['ip2sl']):
        host = config['ip2sl']['ip']

    # allow overridding discovered/configured IP address with ENV variable
    host = os.getenv('IP2SL_SERVER_HOST', host) 
    return host

def load_config(config_file='config/default.yaml'):
    """Load the application configuration"""
    config_file = os.getenv('IP2SL_CONFIG', config_file) # ENV variable overrides all

    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.stderr.write(f"FATAL! {exc}")
            sys.exit(1)

ALLOWED_CLIENT_IPS = []

def configure_allowed_client_ips(config):
    allowed_ips = config.get('allowed_ips')
    if allowed_ips:
        for ip in allowed_ips:
            ALLOWED_CLIENT_IPS.append(ip)

    if len(ALLOWED_CLIENT_IPS) > 0:
        LOG.info(f"Only allowing IP connections for control and proxy from these IP addresses: %s", ALLOWED_CLIENT_IPS)
    return
