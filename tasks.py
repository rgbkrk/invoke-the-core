#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Sets up a CoreOS cluster on rackspace, utilizing the CoreOS discovery service
to create a brand-spanking-new cluster.
'''

import os
import requests
import tempfile

from invoke import run, task

token_get_url = "https://discovery.etcd.io/new"

################################################################################
# IMAGES! 
# 
#
# Image IDs likely to change, hardcoding for now because I'm just tinkering
# Any more advanced than this script and we should be using real provisioning
# tools
#
################################################################################
COREOS_ALPHA  = "c6ba33e5-d48e-4c2d-95c1-2badcdc07231"
COREOS_BETA   = "b63e1435-a46f-4726-b984-e3f15ae92753"
COREOS_STABLE = "7fd88211-ce43-41bf-9a85-e73df4066581"

COREOS_ALPHA_ONMETAL = 

COREOS_ALPHA_ONMETAL = "f616abe4-773b-4c15-92a8-7e036ea906df"
COREOS_BETA_ONMETAL = "d3d03b8b-a955-4031-ae3b-f912828a4257"
COREOS_STABLE_ONMETAL = "dd7bc23b-10a9-463b-8d5a-089ecb9aa868"

default_image = COREOS_STABLE

################################################################################
# FLAVORS!
#
# Get more flavors by visiting Baskin Robbins. Whoops, I mean by running
#   nova flavor-list
#
################################################################################
ONMETAL_COMPUTE = "onmetal-compute1"

FLAVORS = {
  "onmetal-compute1": {"Memory_MB": 32768,  "CPUs": 20},
  "onmetal-io1":      {"Memory_MB": 131072, "CPUs": 40},
  "onmetal-memory1":  {"Memory_MB": 524288, "CPUs": 24},
  "performance1-1":   {"Memory_MB": 1024,   "CPUs": 1},
  "performance1-2":   {"Memory_MB": 2048,   "CPUs": 2},
  "performance1-4":   {"Memory_MB": 4096,   "CPUs": 4},
  "performance1-8":   {"Memory_MB": 8192,   "CPUs": 8},
  "performance2-15":  {"Memory_MB": 15360,  "CPUs": 4},
  "performance2-30":  {"Memory_MB": 30720,  "CPUs": 8},
  "performance2-60":  {"Memory_MB": 61440,  "CPUs": 16},
  "performance2-90":  {"Memory_MB": 92160,  "CPUs": 24},
  "performance2-120": {"Memory_MB": 122880, "CPUs": 32},
}

default_flavor = "performance2-15"

nova_template = '''nova boot \
           --image {image_id} \
           --flavor {flavor_id} \
           --key-name {key_name} \
           --user-data {user_data_file} \
           --config-drive true \
           {nodename}'''


cloud_config_template = '''#cloud-config
coreos:
  etcd:
    # generate a new token for each unique cluster from https://discovery.etcd.io/new
    discovery: {discovery_url}
    # multi-region and multi-cloud deployments need to use $public_ipv4
    # feel free to switch to $private_ipv4
    addr: $public_ipv4:4001
    peer-addr: $public_ipv4:7001
  fleet:
    metadata: provider=rackspace,region={region}
  units:
    - name: etcd.service
      command: start
    - name: fleet.service
      command: start
  update:
    group: stable
'''

@task
def cluster(basename="n", num_nodes=3, key_name="main"):
    # Get a token for this cluster
    resp = requests.get(token_get_url)
    discovery_url = resp.text
    print("Using discovery URL: {}".format(discovery_url))

    # OpenStack defaults for region, used for the fleet metadata
    region = os.environ.get("OS_REGION_NAME", os.environ.get("OS_REGION"))

    if region is None:
        raise Exception("$OS_REGION_NAME or $OS_REGION not set")

    node_names = ["{}{:02}".format(basename, node_id) for node_id in range(num_nodes)]

    # Total hack for user data, should probably be using the nova API or pyrax

    # This could easily be inside the loop if you need to create per node
    # configurations
    cloud_config = cloud_config_template.format(discovery_url=discovery_url,
                                                region=region)
    temp_cc = tempfile.NamedTemporaryFile("w", delete=False)
    temp_cc.write(cloud_config)
    temp_cc.close()

    for node_num,node_name in enumerate(node_names):
        node(node_name, user_data=temp_cc.name, key_name=key_name)

    os.remove(temp_cc.name)

    print("Go to {} in your browser of choice,".format(discovery_url))
    print("Then continuously hit REFRESH")

@task
def node(nodename="corenode",
         user_data="./cloud_config.yml",
         key_name="main",
         image_id=default_image,
         flavor_id=default_flavor):

    nova_line = nova_template.format(nodename=nodename,
                                     image_id=image_id,
                                     flavor_id=flavor_id,
                                     user_data_file=user_data,
                                     key_name=key_name)

    run(nova_line)

