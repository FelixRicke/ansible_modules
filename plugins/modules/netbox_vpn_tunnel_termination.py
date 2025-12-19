#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: netbox_vpn_tunnel_termination
short_description: Create, update or delete VPN tunnel terminations in NetBox
description:
  - Creates, updates, or removes VPN tunnel termination objects in NetBox.
  - This module uses the C(NetboxVpnModule) helper from the netbox.netbox collection.
notes:
  - This should be run with C(connection=local) and C(hosts=localhost).
author:
  - Your Name (@yourgithub)
requirements:
  - pynetbox
version_added: "3.21.0"
extends_documentation_fragment:
  - netbox.netbox.common
options:
  data:
    description:
      - Dictionary defining the VPN tunnel termination configuration.
    required: true
    type: dict
    suboptions:
      tunnel:
        description:
          - The tunnel associated with this termination.
        required: true
        type: raw
      role:
        description:
          - Role of this tunnel termination.
        choices:
          - peer
          - hub
          - spoke
        type: str
      termination_type:
        description:
          - Object type of the associated termination (interface or VM interface, etc.)
        required: true
        type: str
      termination_id:
        description:
          - The object ID associated with the termination.
        type: int
      outside_ip:
        description:
          - Outside IP address associated with the tunnel termination (as integer).
        type: int
      tags:
        description:
          - Tags to apply.
        type: list
        elements: raw
      custom_fields:
        description:
          - Must exist in NetBox.
        type: dict
  state:
    description:
      - State of object.
    choices:
      - present
      - absent
    default: present
    type: str
"""

EXAMPLES = r"""
- name: Create a tunnel termination
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Create VPN tunnel termination
      netbox.netbox.netbox_vpn_tunnel_termination:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          tunnel:
            name: ipsec-tunnel1
          termination_type: dcim.interface
          termination_id: 42
          role: hub
          outside_ip: 3232235521
        state: present

- name: Delete a tunnel termination
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Remove VPN tunnel termination
      netbox.netbox.netbox_vpn_tunnel_termination:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          tunnel:
            name: ipsec-tunnel1
          termination_type: dcim.interface
          termination_id: 42
        state: absent
"""

RETURN = r"""
tunnel_termination:
  description: Serialized representation of the created or updated tunnel termination.
  returned: when state=present
  type: dict
msg:
  description: Details about what the module accomplished.
  returned: always
  type: str
"""

from copy import deepcopy

from ansible_collections.netbox.netbox.plugins.module_utils.netbox_vpn import (
    NetboxVpnModule,
    NB_TUNNEL_TERMINATIONS,
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
                    tunnel=dict(type="raw", required=True),
                    role=dict(type="str", required=False,
                              choices=["peer", "hub", "spoke"]),
                    termination_type=dict(type="str", required=True),
                    termination_id=dict(type="int", required=False),
                    outside_ip=dict(type="int", required=False),
                    tags=dict(type="list", elements="raw", required=False),
                    custom_fields=dict(type="dict", required=False),
                ),
            ),
        )
    )

    required_if = [
        ("state", "present", ["data"]),
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if
    )

    netbox_module = NetboxVpnModule(module, NB_TUNNEL_TERMINATIONS)
    netbox_module.run()


if __name__ == "__main__":
    main()
