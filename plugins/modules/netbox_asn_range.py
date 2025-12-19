#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: netbox_asn_range
short_description: Create, update or delete ASN Ranges within NetBox
description:
  - Manages ASN Range objects using NetBox's REST API.
  - Supports create, update, and delete operations.
author:
  - Felix Ricke (@FelixRicke)
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
      - Optional list of fields to use to uniquely identify the ASN range.
      - If omitted, module will use default lookups: C(name), C(slug).
    type: list
    elements: str
    required: false

  state:
    description:
      - The desired state of the ASN range.
    type: str
    choices: [present, absent]
    default: present

  data:
    description: Data for the ASN range object.
    type: dict
    required: true
    suboptions:
      name:
        type: str
        required: true
      slug:
        type: str
        required: true
      rir:
        description: RIR ID (integer)
        type: int
        required: true
      start:
        description: Start ASN (integer)
        type: int
        required: true
      end:
        description: End ASN (integer)
        type: int
        required: true
      tenant:
        description: Tenant ID (integer)
        type: int
      description:
        type: str
      tags:
        type: list
        elements: raw
      custom_fields:
        type: dict
'''

EXAMPLES = r'''
- name: Create an ASN range
  netbox.netbox.netbox_asn_range:
    netbox_url: "http://netbox.local"
    netbox_token: "{{ netbox_token }}"
    validate_certs: false
    state: present
    data:
      name: "Private ASN block"
      slug: "private-asn-block"
      rir: 1
      start: 64512
      end: 65535
      description: "Private ASN range"
      tenant: 2
      tags:
        - "asn"
      custom_fields:
        region: "internal"

- name: Delete an ASN range
  netbox.netbox.netbox_asn_range:
    netbox_url: "http://netbox.local"
    netbox_token: "{{ netbox_token }}"
    state: absent
    data:
      name: "Private ASN block"
      slug: "private-asn-block"
'''

RETURN = r'''
asn_range:
  description: Serialized NetBox ASN range object.
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
    NB_ASN_RANGES,
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
                    slug=dict(required=False, type="str"),
                    rir=dict(required=False, type="raw"),
                    start=dict(required=False, type="int"),
                    end=dict(required=False, type="int"),
                    description=dict(required=False, type="str"),
                    tags=dict(required=False, type="list", elements="raw"),
                    tenant=dict(required=False, type="raw"),
                    custom_fields=dict(required=False, type="dict"),
                ),
            ),
        )
    )

    required_if = [
        (
            "state",
            "present",
            [
                "name",
                "rir",
                "start",
                "end",
            ],
        ),
        ("state", "absent", ["name"])
    ]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )

    netbox_asn_ranges = NetboxIpamModule(module, NB_ASN_RANGES)
    netbox_asn_ranges.run()

if __name__ == "__main__":
    main()
