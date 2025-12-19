#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: netbox_vpn_ike_policy
short_description: Create, update, or delete IKE policies in NetBox
description:
  - Manages IKE policies within NetBox using the VPN module.
notes:
  - Must be run with connection C(local) against C(localhost).
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
      - Data structure defining the IKE policy.
    required: true
    type: dict
    suboptions:
      name:
        description:
          - Name of the IKE policy.
        required: true
        type: str
      description:
        description:
          - Policy description.
        type: str
      version:
        description:
          - IKE version.
        type: int
        choices:
          - 1
          - 2
      mode:
        description:
          - IKE mode.
        type: str
        choices:
          - aggressive
          - main
      proposals:
        description:
          - List of IKE proposal IDs.
        type: list
        elements: int
      preshared_key:
        description:
          - Preshared authentication key.
        type: str
      comments:
        description:
          - Comments for the object.
        type: str
      tags:
        description:
          - Tags to apply.
        type: list
        elements: raw
      custom_fields:
        description:
          - Custom field values (must already exist in NetBox).
        type: dict
  state:
    description:
      - Whether the policy should exist or not.
    choices:
      - present
      - absent
    default: present
    type: str
"""

EXAMPLES = r"""
- name: Create IKE policy
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Create IKE policy example
      netbox.netbox.netbox_vpn_ike_policy:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IKE-POLICY-1
          version: 2
          mode: main
          proposals:
            - 1
            - 2
          preshared_key: "SuperSecretKey"
          description: "IKEv2 main mode policy"
        state: present

- name: Delete IKE policy
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Remove IKE policy
      netbox.netbox.netbox_vpn_ike_policy:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IKE-POLICY-1
        state: absent
"""

RETURN = r"""
ike_policy:
  description: Serialized object of the IKE policy as created or updated.
  returned: when state=present
  type: dict
msg:
  description: Message describing the outcome.
  returned: always
  type: str
"""

from copy import deepcopy

from ansible_collections.netbox.netbox.plugins.module_utils.netbox_vpn import (
    NetboxVpnModule,
    NB_IKE_POLICIES,
)
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
    NETBOX_ARG_SPEC,
)
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
    NetboxAnsibleModule,
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
                    version=dict(type="int", required=False, choices=[1, 2]),
                    mode=dict(type="str", required=False,
                              choices=["aggressive", "main"]),
                    proposals=dict(type="list", elements="int", required=False),
                    preshared_key=dict(type="str", required=False),
                    comments=dict(type="str", required=False),
                    tags=dict(type="list", elements="raw", required=False),
                    custom_fields=dict(type="dict", required=False),
                ),
            ),
        )
    )

    required_if = [
        ("state", "present", ["data", "data.name"]),
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if
    )

    netbox_module = NetboxVpnModule(module, NB_IKE_POLICIES)
    netbox_module.run()


if __name__ == "__main__":
    main()
