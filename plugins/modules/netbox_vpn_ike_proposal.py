#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: netbox_vpn_ike_proposal
short_description: Manage IKE Proposals in NetBox
description:
  - Create, update, or delete IKE proposals in NetBox's VPN application.
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
      - Data structure defining the IKE proposal.
    required: true
    type: dict
    suboptions:
      name:
        description: Name of the IKE proposal
        required: true
        type: str
      description:
        description: Description of the proposal
        type: str
      authentication_method:
        description:
          - Authentication method
        required: true
        type: str
        choices:
          - preshared-keys
          - certificates
          - rsa-signatures
          - dsa-signatures
      encryption_algorithm:
        description: Encryption algorithm
        required: true
        type: str
        choices:
          - aes-128-cbc
          - aes-128-gcm
          - aes-192-cbc
          - aes-192-gcm
          - aes-256-cbc
          - aes-256-gcm
          - 3des-cbc
          - des-cbc
      authentication_algorithm:
        description: Authentication algorithm
        type: str
        choices:
          - hmac-sha1
          - hmac-sha256
          - hmac-sha384
          - hmac-sha512
          - hmac-md5
      group:
        description: Diffie-Hellman group ID
        required: true
        type: int
      sa_lifetime:
        description: Security association lifetime in seconds
        type: int
      comments:
        description: Comments for the object
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
- name: Create IKE proposal
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Add IKE proposal example
      netbox.netbox.netbox_vpn_ike_proposal:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IKE-PROPOSAL-1
          authentication_method: preshared-keys
          encryption_algorithm: aes-256-gcm
          authentication_algorithm: hmac-sha256
          group: 14
        state: present

- name: Delete IKE proposal
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Remove IKE proposal
      netbox.netbox.netbox_vpn_ike_proposal:
        netbox_url: http://netbox.local
        netbox_token: myToken
        data:
          name: IKE-PROPOSAL-1
        state: absent
"""

RETURN = r"""
ike_proposal:
  description: Serialized object of the IKE proposal as created or updated.
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
    NetboxVpnModule, NB_IKE_PROPOSALS
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
                    authentication_method=dict(type="str", required=True,
                                               choices=["preshared-keys","certificates","rsa-signatures","dsa-signatures"]),
                    encryption_algorithm=dict(type="str", required=True,
                                              choices=["aes-128-cbc","aes-128-gcm","aes-192-cbc","aes-192-gcm","aes-256-cbc","aes-256-gcm","3des-cbc","des-cbc"]),
                    authentication_algorithm=dict(type="str", required=False,
                                                  choices=["hmac-sha1","hmac-sha256","hmac-sha384","hmac-sha512","hmac-md5"]),
                    group=dict(type="int", required=True),
                    sa_lifetime=dict(type="int", required=False),
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

    netbox_module = NetboxVpnModule(module, NB_IKE_PROPOSALS)
    netbox_module.run()


if __name__ == "__main__":
    main()
