#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: netbox_vpn_ipsec_profile
short_description: Manage IPsec Profiles in NetBox
description:
  - Create, update, or delete IPsec profiles in NetBox's VPN application.
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
      - Data structure defining the IPsec profile
    required: true
    type: dict
    suboptions:
      name:
        description: Name of the IPsec profile
        required: true
        type: str
      description:
        description: Description of the IPsec profile
        type: str
      mode:
        description: Mode of the IPsec profile (esp or ah)
        required: true
        type: str
        choices: [ "esp", "ah" ]
      ike_policy:
        description: ID of the associated IKE policy
        required: true
        type: int
      ipsec_policy:
        description: ID of the associated IPsec policy
        required: true
        type: int
      comments:
        description: Comments for the IPsec profile
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
- name: Create IPsec profile
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Add IPsec profile example
      netbox.netbox.netbox_vpn_ipsec_profile:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IPSEC-PROFILE-1
          mode: esp
          ike_policy: 1
          ipsec_policy: 2
        state: present

- name: Delete IPsec profile
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Remove IPsec profile
      netbox.netbox.netbox_vpn_ipsec_profile:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IPSEC-PROFILE-1
        state: absent
"""

RETURN = r"""
ipsec_profile:
  description: Serialized object of the IPsec profile as created or updated.
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
    NetboxVpnModule, NB_IPSEC_PROFILES
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
                    mode=dict(type="str", required=True, choices=["esp", "ah"]),
                    ike_policy=dict(type="int", required=True),
                    ipsec_policy=dict(type="int", required=True),
                    comments=dict(type="str", required=False),
                    tags=dict(type="list", elements="raw", required=False),
                    custom_fields=dict(type="dict", required=False),
                ),
            )
        )
    )

    required_if = [("state", "present", ["data", "data.name"])]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if
    )

    netbox_module = NetboxVpnModule(module, NB_IPSEC_PROFILES)
    netbox_module.run()


if __name__ == "__main__":
    main()
