#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: netbox_vlan_translation_rule
short_description: Create, update or delete VLAN Translation Rules within NetBox
description:
  - Manages VLAN Translation Rule objects using NetBox's REST API.
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
      - Optional fields used to uniquely identify a VLAN translation rule.
      - If omitted, module will use:
        - C(policy), C(local_vid), C(remote_vid)
    type: list
    elements: str
    required: false

  state:
    description:
      - Desired state of the VLAN translation rule.
    type: str
    choices: [present, absent]
    default: present

  data:
    description: Data payload for the VLAN translation rule.
    type: dict
    required: true
    suboptions:
      policy:
        type: raw
        required: true
      local_vid:
        type: int
        required: true
      remote_vid:
        type: int
        required: true
      description:
        type: str
'''

EXAMPLES = r'''
- name: "Test NetBox VLAN translation rule module"
  connection: local
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create VLAN translation rule
      netbox.netbox.netbox_vlan_translation_rule:
          netbox_url: "http://netbox.local"
          netbox_token: "{{ netbox_token }}"
          validate_certs: false
          state: present
          data:
            policy: "Policy01"
            local_vid: 100
            remote_vid: 200
            description: "Rule example"

    - name: Delete VLAN translation rule
      netbox.netbox.netbox_vlan_translation_rule:
          netbox_url: "http://netbox.local"
          netbox_token: "{{ netbox_token }}"
          state: absent
          data:
            policy: "Policy01"
            local_vid: 100
            remote_vid: 200
'''

RETURN = r'''
vlan_translation_rule:
  description: Serialized NetBox VLAN translation rule object.
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
    NB_VLAN_TRANSLATION_RULES,
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
                    policy=dict(required=True, type="raw"),
                    local_vid=dict(required=True, type="int"),
                    remote_vid=dict(required=True, type="int"),
                    description=dict(required=False, type="str"),
                )
            )
        )
    )

    required_if = [
        ("state", "present", ["policy", "local_vid", "remote_vid"]),
        ("state", "absent", ["policy", "local_vid", "remote_vid"]),
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )

    netbox_vlan_translation_rule = NetboxIpamModule(module, NB_VLAN_TRANSLATION_RULES)
    netbox_vlan_translation_rule.run()

if __name__ == "__main__":
    main()
