# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import common_logging_conf_contents, ZatoCommand
from zato.common.defaults import http_plain_server_port

# bzrlib
from bzrlib.lazy_import import lazy_import

lazy_import(globals(), """
    # quicli
    import os, uuid
    
""")

config_template = """{
  "haproxy_command": "haproxy",
  "host": "localhost",
  "port": 20151,
  "keyfile": "./zato-lba-priv-key.pem",
  "certfile": "./zato-lba-cert.pem",
  "ca_certs": "./zato-lba-ca-certs.pem",
  "work_dir": "../",
  "verify_fields": {},
  "log_config": "./logging.conf",
  "pid_file": "zato-lb-agent.pid"
}
"""

zato_config_template = """
# ##############################################################################

global
    log 127.0.0.1:514 local0 debug # ZATO global:log
    stats socket {stats_socket} # ZATO global:stats_socket

# ##############################################################################

defaults
    log global
    option httpclose

    stats uri /zato-lb-stats # ZATO defaults:stats uri

    timeout connect 15000 # ZATO defaults:timeout connect
    timeout client 15000 # ZATO defaults:timeout client
    timeout server 15000 # ZATO defaults:timeout server

    stats enable
    stats realm   Haproxy\ Statistics

    # Note: The password below is a UUID4 written in plain-text.
    stats auth    admin1:{stats_password}

    stats refresh 5s

# ##############################################################################

backend bck_http_plain
    mode http
    balance roundrobin
    
# ZATO begin backend bck_http_plain

{default_backend}

# ZATO end backend bck_http_plain

# ##############################################################################

frontend front_http_plain

    mode http
    default_backend bck_http_plain

    option httplog # ZATO frontend front_http_plain:option log-http-requests
    bind 127.0.0.1:11223 # ZATO frontend front_http_plain:bind
    maxconn 200 # ZATO frontend front_http_plain:maxconn

    monitor-uri /zato-lb-alive # ZATO frontend front_http_plain:monitor-uri
"""

default_backend = """
    server http_plain--server1 127.0.0.1:{server01_port} check inter 2s rise 2 fall 2 # ZATO backend bck_http_plain:server--server1
    server http_plain--server2 127.0.0.1:{server02_port} check inter 2s rise 2 fall 2 # ZATO backend bck_http_plain:server--server2
"""

class Create(ZatoCommand):
    """ Creates a new Zato load-balancer
    """
    opts = []
    opts.append({'name':'pub_key_path', 'help':"Path to the load-balancer agent's public key in PEM"})
    opts.append({'name':'priv_key_path', 'help':"Path to the load-balancer agent's private key in PEM"})
    opts.append({'name':'cert_path', 'help':"Path to the load-balancer agent's certificate in PEM"})
    opts.append({'name':'ca_certs_path', 'help':"Path to the a PEM list of certificates the load-balancer's agent will trust"})

    needs_empty_dir = True

    def __init__(self, args):
        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path) # noqa

    def execute(self, args, use_default_backend=False, server02_port=None, show_output=True):
        os.mkdir(os.path.join(self.target_dir, 'config')) # noqa
        os.mkdir(os.path.join(self.target_dir, 'config', 'zdaemon')) # noqa
        os.mkdir(os.path.join(self.target_dir, 'logs')) # noqa
        
        repo_dir = os.path.join(self.target_dir, 'config', 'repo') # noqa
        os.mkdir(repo_dir) # noqa

        log_path = os.path.abspath(os.path.join(repo_dir, '..', '..', 'logs', 'lb-agent.log')) # noqa
        stats_socket = os.path.join(self.target_dir, 'haproxy-stat.sock') # noqa

        open(os.path.join(repo_dir, 'lb-agent.conf'), 'w').write(config_template) # noqa
        open(os.path.join(repo_dir, 'logging.conf'), 'w').write((common_logging_conf_contents.format(log_path=log_path))) # noqa
        
        if use_default_backend:
            backend = default_backend.format(server01_port=http_plain_server_port, server02_port=server02_port)
        else:
            backend = '\n# ZATO default_backend_empty'

        zato_config = zato_config_template.format(stats_socket=stats_socket, stats_password=uuid.uuid4().hex, default_backend=backend) # noqa
        open(os.path.join(repo_dir, 'zato.config'), 'w').write(zato_config) # noqa
        self.copy_lb_crypto(repo_dir, args)
        
        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.LOAD_BALANCER.code)

        if show_output:
            if self.verbose:
                msg = "Successfully created a load-balancer's agent in {}".format(self.target_dir)
                self.logger.debug(msg)
            else:
                self.logger.info('OK')
