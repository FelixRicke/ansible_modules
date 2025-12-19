#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: netbox_vlan_translation_policy
short_description: Create, update or delete VLAN Translation Policies within NetBox
description:
  - Manages VLAN Translation Policy objects using NetBox's REST API.
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
      - Optional list of fields to uniquely identify the VLAN translation policy.
      - If omitted, module will use default lookups: C(name)
    type: list
    elements: str
    required: false

  state:
    description:
      - Desired state of the VLAN translation policy.
    type: str
    choices: [present, absent]
    default: present

  data:
    description: Data payload for the VLAN translation policy.
    type: dict
    required: true
    suboptions:
      name:
        type: str
        required: true
      description:
        type: str
'''

EXAMPLES = r'''
- name: "Test NetBox VLAN translation policy module"
  connection: local
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create VLAN Translation Policy
      netbox.netbox.netbox_vlan_translation_policy:
          netbox_url: "http://netbox.local"
          netbox_token: "{{ netbox_token }}"
          validate_certs: false
          state: present
          data:
            name: "Policy A"
            description: "Example translation policy"

    - name: Delete VLAN Translation Policy
      netbox.netbox.netbox_vlan_translation_policy:
          netbox_url: "http://netbox.local"
          netbox_token: "{{ netbox_token }}"
          state: absent
          data:
            name: "Policy A"
'''

RETURN = r'''
vlan_translation_policy:
  description: Serialized NetBox VLAN translation policy object.
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
    NB_VLAN_TRANSLATION_POLICIES,
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
                    name=dict(required=True, type="str"),
                    description=dict(required=False, type="str"),
                )
            )
        )
    )

    required_if = [
        ("state", "present", ["name"]),
        ("state", "absent", ["name"])
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )

    netbox_vlan_translation_policy = NetboxIpamModule(module, NB_VLAN_TRANSLATION_POLICIES)
    netbox_vlan_translation_policy.run()


if __name__ == "__main__":
    main()
