#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import deepcopy

DOCUMENTATION = r'''
---
module: netbox_virtualization_interface
short_description: Create, update or delete Virtualization Interfaces within NetBox
description:
  - Manages Virtualization Interface objects in NetBox via its REST API.
  - Supports create, update, and delete operations.
author:
  - Your Name (@yourgithub)
version_added: "3.21.0"
requirements:
  - pynetbox
options:
  netbox_url:
    required: true
    type: str
    description: URL of the NetBox instance.

  netbox_token:
    required: true
    type: str
    description: API token for authentication.

  validate_certs:
    required: false
    type: bool
    default: true

  headers:
    required: false
    type: dict

  query_params:
    required: false
    type: list
    elements: str
    description:
      - Optional list of fields used to uniquely identify the interface.
      - Defaults: C(virtual_machine), C(name)

  state:
    required: false
    type: str
    choices: [present, absent]
    default: present

  data:
    required: true
    type: dict
    description: Data for the interface object.
    suboptions:
      virtual_machine:
        type: raw
        required: true
      name:
        type: str
        required: true
      enabled:
        type: bool
        required: false
      parent:
        type: raw
        required: false
      bridge:
        type: raw
        required: false
      mtu:
        type: int
        required: false
      primary_mac_address:
        type: str
        required: false
      description:
        type: str
        required: false
      mode:
        type: str
        required: false
        choices:
          - access
          - tagged
          - tagged-all
          - q-in-q
      untagged_vlan:
        type: raw
        required: false
      tagged_vlans:
        type: list
        required: false
        elements: raw
      qinq_svlan:
        type: raw
        required: false
      vlan_translation_policy:
        type: raw
        required: false
      vrf:
        type: raw
        required: false
      tags:
        type: list
        elements: raw
        required: false
      custom_fields:
        type: dict
        required: false
'''

EXAMPLES = r'''
- name: "Test NetBox virtualization interface module"
  connection: local
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create vNIC on VM
      netbox.netbox.netbox_virtualization_interface:
        netbox_url: "http://netbox.local"
        netbox_token: "{{ netbox_token }}"
        validate_certs: false
        state: present
        data:
          virtual_machine: "VM1"
          name: "eth0"
          enabled: true
          mtu: 1500
          description: "Main interface"
          vlan_translation_policy: "Policy A"
          untagged_vlan:
            name: Wireless
            site: Test Site
          tagged_vlans:
            - name: Data
              site: Test Site
            - name: VoIP
              site: Test Site
          mode: "tagged"
          tags:
            - "prod"
            - "vnic"
          custom_fields:
            location: "rack12"

    - name: Delete vNIC
      netbox.netbox.netbox_virtualization_interface:
        netbox_url: "http://netbox.local"
        netbox_token: "{{ netbox_token }}"
        state: absent
        data:
            virtual_machine: "VM1"
            name: "eth0"
'''

RETURN = r'''
virtualization_interface:
  description: Serialized NetBox virtualization interface object.
  returned: success
  type: dict
'''

from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
    NetboxAnsibleModule,
    NETBOX_ARG_SPEC,
)

from ansible_collections.netbox.netbox.plugins.module_utils.netbox_virtualization import (
    NetboxVirtualizationModule,
    NB_INTERFACES,
)

def main():
    argument_spec = deepcopy(NETBOX_ARG_SPEC)
    argument_spec.update(
        dict(
            data=dict(
                type="dict",
                required=True,
                options=dict(
                    virtual_machine=dict(required=True, type="raw"),
                    name=dict(required=True, type="str"),
                    enabled=dict(required=False, type="bool"),
                    parent=dict(required=False, type="raw"),
                    bridge=dict(required=False, type="raw"),
                    mtu=dict(required=False, type="int"),
                    primary_mac_address=dict(required=False, type="str"),
                    description=dict(required=False, type="str"),
                    mode=dict(
                        required=False,
                        type="str",
                        choices=["access", "tagged", "tagged-all", "q-in-q"],
                    ),
                    untagged_vlan=dict(required=False, type="raw"),
                    tagged_vlans=dict(required=False, type="list", elements="raw"),
                    qinq_svlan=dict(required=False, type="raw"),
                    vlan_translation_policy=dict(required=False, type="raw"),
                    vrf=dict(required=False, type="raw"),
                    tags=dict(required=False, type="list", elements="raw"),
                    custom_fields=dict(required=False, type="dict"),
                ),
            )
        )
    )

    required_if = [
        ("state", "present", ["virtual_machine", "name"]),
        ("state", "absent", ["virtual_machine", "name"]),
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    netbox_virtualization_interface = NetboxVirtualizationModule(module, NB_INTERFACES)
    netbox_virtualization_interface.run()


if __name__ == "__main__":
    main()
