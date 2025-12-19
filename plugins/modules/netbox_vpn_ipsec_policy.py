#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: netbox_vpn_ipsec_policy
short_description: Manage IPsec Policies in NetBox
description:
  - Create, update, or delete IPsec policies in NetBox's VPN application.
requirements:
  - pynetbox
version_added: "3.21.0"
author:
  - Your Name (@yourgithub)
extends_documentation_fragment:
  - netbox.netbox.common
options:
  data:
    description:
      - Data structure defining the IPsec policy
    required: true
    type: dict
    suboptions:
      name:
        description: Name of the IPsec policy
        required: true
        type: str
      description:
        description: Description of the IPsec policy
        type: str
      proposals:
        description: List of IPsec proposal IDs
        type: list
        elements: int
      pfs_group:
        description: Diffie-Hellman group for Perfect Forward Secrecy
        type: int
      comments:
        description: Comments for the IPsec policy
        type: str
      tags:
        description: Tags to assign
        type: list
        elements: raw
      custom_fields:
        description: Custom fields (must exist in NetBox)
        type: dict
  state:
    description:
      - Desired state
    default: present
    choices:
      - present
      - absent
    type: str
"""

EXAMPLES = r"""
- name: Create IPsec policy
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Add IPsec policy example
      netbox.netbox.netbox_vpn_ipsec_policy:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IPSEC-POLICY-1
          proposals: [1,2]
          pfs_group: 14
        state: present

- name: Delete IPsec policy
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Remove IPsec policy
      netbox.netbox.netbox_vpn_ipsec_policy:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IPSEC-POLICY-1
        state: absent
"""

RETURN = r"""
ipsec_policy:
  description: Serialized object of the IPsec policy as created or updated.
  returned: when state=present
  type: dict
msg:
  description: Message describing the outcome
  returned: always
  type: str
"""

from copy import deepcopy
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
    NETBOX_ARG_SPEC, NetboxAnsibleModule
)
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_vpn import (
    NetboxVpnModule, NB_IPSEC_POLICIES
)


def main():
    argument_spec = deepcopy(NETBOX_ARG_SPEC)
    argument_spec.update(
        dict(
            data=dict(
                type="dict",
                required=True,
                options=dict(
                    name=dict(type="str", required=True),
                    description=dict(type="str", required=False),
                    proposals=dict(type="list", elements="int", required=False),
                    pfs_group=dict(type="int", required=False),
                    comments=dict(type="str", required=False),
                    tags=dict(type="list", elements="raw", required=False),
                    custom_fields=dict(type="dict", required=False),
                ),
            )
        )
    )

    required_if = [("state", "present", ["data","data.name"])]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if
    )

    netbox_module = NetboxVpnModule(module, NB_IPSEC_POLICIES)
    netbox_module.run()


if __name__ == "__main__":
    main()
