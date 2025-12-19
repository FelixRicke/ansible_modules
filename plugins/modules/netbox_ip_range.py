#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: netbox_ip_range
short_description: Create, update or delete IP Ranges within NetBox
description:
  - Manages IP Range objects using NetBox's REST API.
  - Supports create, update, and delete operations.
author:
  - Your Name (@yourgithub)
version_added: "3.21.0"
requirements:
  - pynetbox
options:
  netbox_url:
    description: URL of the NetBox instance.
    required: true
    type: str

  netbox_token:
    description: API token for authenticating against NetBox.
    required: true
    type: str

  validate_certs:
    description: Whether to validate SSL certificates.
    required: false
    type: bool
    default: true

  headers:
    description: Additional headers to include in API calls.
    required: false
    type: dict

  query_params:
    description:
      - Optional list of fields to use to uniquely identify the IP range.
      - If omitted, module will use default lookups: C(start_address), C(end_address)
    type: list
    elements: str
    required: false

  state:
    description:
      - The desired state of the IP range.
    type: str
    choices: [present, absent]
    default: present

  data:
    description: Data for the IP range object.
    type: dict
    required: true
    suboptions:
      start_address:
        type: str
        required: true
      end_address:
        type: str
        required: true
      vrf:
        type: int
      tenant:
        type: int
      status:
        type: str
        choices: [active, reserved, deprecated]
      role:
        type: int
      description:
        type: str
      comments:
        type: str
      tags:
        type: list
        elements: raw
      custom_fields:
        type: dict
      mark_populated:
        type: bool
      mark_utilized:
        type: bool
'''

EXAMPLES = r'''
- name: "Test NetBox IP ranges module"
  connection: local
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create an IP range
      netbox.netbox.netbox_ip_range:
        netbox_url: "http://netbox.local"
        netbox_token: "{{ netbox_token }}"
        validate_certs: false
        state: present
        data:
          start_address: "192.0.2.0"
          end_address: "192.0.2.255"
          vrf: 1
          tenant: 2
          status: "active"
          description: "Example IP range"
          mark_populated: false
          mark_utilized: false

    - name: Delete an IP range
      netbox.netbox.netbox_ip_range:
        netbox_url: "http://netbox.local"
        netbox_token: "{{ netbox_token }}"
        state: absent
        data:
          start_address: "192.0.2.0"
          end_address: "192.0.2.255"
'''

RETURN = r'''
ip_range:
  description: Serialized NetBox IP range object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
    NetboxAnsibleModule,
    NETBOX_ARG_SPEC,
)
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_ipam import (
    NetboxIpamModule,
    NB_IP_RANGES,
)
from copy import deepcopy

def main():
    argument_spec = deepcopy(NETBOX_ARG_SPEC)
    argument_spec.update(
        dict(
            data=dict(
                type="dict",
                required=True,
                options=dict(
                    start_address=dict(required=True, type="str"),
                    end_address=dict(required=True, type="str"),
                    vrf=dict(required=False, type="raw"),
                    tenant=dict(required=False, type="raw"),
                    status=dict(required=False, type="str", choices=["active","reserved","deprecated"]),
                    role=dict(required=False, type="raw"),
                    description=dict(required=False, type="str"),
                    comments=dict(required=False, type="str"),
                    tags=dict(required=False, type="list", elements="raw"),
                    custom_fields=dict(required=False, type="dict"),
                    mark_populated=dict(required=False, type="bool"),
                    mark_utilized=dict(required=False, type="bool"),
                )
            )
        )
    )

    required_if = [
        ("state", "present", ["start_address", "end_address"]),
        ("state", "absent", ["start_address", "end_address"]),
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )

    netbox_ip_ranges = NetboxIpamModule(module, NB_IP_RANGES)
    netbox_ip_ranges.run()

if __name__ == "__main__":
    main()
