# -*- coding: utf-8 -*-

# Copyright: (c) 2019. Chris Mills <chris@discreet-its.co.uk>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
netbox.py

A lookup function designed to return data from the NetBox application
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    author: Chris Mills (@cpmills1975)
    name: nb_lookup
    version_added: "0.1.0"
    short_description: Queries and returns elements from NetBox
    description:
        - Queries NetBox via its API to return virtually any information
          capable of being held in NetBox.
    options:
        _terms:
            description:
                - The NetBox object type to query
            required: true
        api_endpoint:
            description:
                - The URL to the NetBox instance to query
            env:
                # in order of precendence
                - name: NETBOX_API
                - name: NETBOX_URL
            required: true
        api_filter:
            description:
                - The api_filter to use. Filters should be key value pairs separated by a space.
            required: false
        plugin:
            description:
                - The NetBox plugin to query
            required: false
        token:
            description:
                - The API token created through NetBox
                - This may not be required depending on the NetBox setup.
            env:
                # in order of precendence
                - name: NETBOX_TOKEN
                - name: NETBOX_API_TOKEN
            required: false
        headers:
            description: Dictionary of headers to be passed to the NetBox API.
            default: {}
            env:
                - name: NETBOX_HEADERS
        validate_certs:
            description:
                - Whether or not to validate SSL of the NetBox instance
            required: false
            default: true
        private_key:
            description:
                - (DEPRECATED) - NetBox 2.11 and earlier only
                - The private key as a string. Mutually exclusive with I(key_file).
            required: false
        key_file:
            description:
                - (DEPRECATED) - NetBox 2.11 and earlier only
                - The location of the private key tied to user account. Mutually exclusive with I(private_key).
            required: false
        raw_data:
            type: bool
            description:
                - Whether to return raw API data with the lookup/query or whether to return a key/value dict
            required: false
    requirements:
        - pynetbox
"""

EXAMPLES = """
tasks:
  # query a list of devices
  - name: Obtain list of devices from NetBox
    debug:
      msg: >
        "Device {{ item.value.display_name }} (ID: {{ item.key }}) was
         manufactured by {{ item.value.device_type.manufacturer.name }}"
    loop: "{{ query('netbox.netbox.nb_lookup', 'devices',
                    api_endpoint='http://localhost/',
                    token='<redacted>') }}"

    # This example uses an API Filter
  - name: Obtain list of devices from NetBox
    debug:
      msg: >
        "Device {{ item.value.display_name }} (ID: {{ item.key }}) was
         manufactured by {{ item.value.device_type.manufacturer.name }}"
    loop: "{{ query('netbox.netbox.nb_lookup', 'devices',
                    api_endpoint='http://localhost/',
                    api_filter='role=management tag=Dell'),
                    token='<redacted>') }}"
    # This example uses an API Filter with a variable and jinja concatenation
  - name: Set hostname fact
    set_fact:
      hostname: "my-server"
  - name: Obtain details of a single device from NetBox
    debug:
      msg: >
        "Device {{item.0.value.display}} (ID: {{item.0.key}}) was
         manufactured by {{ item.0.value.device_type.manufacturer.name }}"
    loop:
      - '{{ query("netbox.netbox.nb_lookup", "devices",
        api_endpoint="http://localhost/",
        api_filter="name=" ~hostname,
        token="<redacted>") }}'
"""

RETURN = """
  _list:
    description:
      - list of composed dictionaries with key and value
    type: list
"""

import os
import functools
import json
from pprint import pformat

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.parsing.splitter import parse_kv, split_args
from ansible.utils.display import Display
from importlib.metadata import version

try:
    import pynetbox
except ImportError as imp_exc:
    PYNETBOX_LIBRARY_IMPORT_ERROR = imp_exc
else:
    PYNETBOX_LIBRARY_IMPORT_ERROR = None

try:
    import requests
except ImportError as imp_exc:
    REQUESTS_LIBRARY_IMPORT_ERROR = imp_exc
else:
    REQUESTS_LIBRARY_IMPORT_ERROR = None

try:
    from packaging.version import Version

    HAS_PACKAGING = True
    PACKAGING_IMPORT_ERROR = ""
except ImportError as imp_exc:
    PACKAGING_IMPORT_ERROR = imp_exc
    HAS_PACKAGING = False


def get_endpoint(netbox, term):
    """
    get_endpoint(netbox, term)
        netbox: a predefined pynetbox.api() pointing to a valid instance
                of NetBox
        term: the term passed to the lookup function upon which the api
              call will be identified
    """

    netbox_endpoint_map = {
    # Circuits
    "circuit-group-assignments":    {"endpoint": netbox.circuits.circuit_group_assignments},
    "circuit-groups":               {"endpoint": netbox.circuits.circuit_groups},
    "circuit-terminations":         {"endpoint": netbox.circuits.circuit_terminations},
    "circuit-types":                {"endpoint": netbox.circuits.circuit_types},
    "circuits":                     {"endpoint": netbox.circuits.circuits},
    "provider-accounts":            {"endpoint": netbox.circuits.provider_accounts},
    "provider-networks":            {"endpoint": netbox.circuits.provider_networks},
    "providers":                    {"endpoint": netbox.circuits.providers},
    "virtual-circuit-terminations": {"endpoint": netbox.circuits.virtual_circuit_terminations},
    "virtual-circuit-types":        {"endpoint": netbox.circuits.virtual_circuit_types},
    "virtual-circuits":             {"endpoint": netbox.circuits.virtual_circuits},

    # DCIM
    "cable-terminations":           {"endpoint": netbox.dcim.cable_terminations},
    "cables":                       {"endpoint": netbox.dcim.cables},
    "connected-device":             {"endpoint": netbox.dcim.connected_device},
    "console-port-templates":       {"endpoint": netbox.dcim.console_port_templates},
    "console-ports":                {"endpoint": netbox.dcim.console_ports},
    "console-server-port-templates":{"endpoint": netbox.dcim.console_server_port_templates},
    "console-server-ports":         {"endpoint": netbox.dcim.console_server_ports},
    "device-bay-templates":         {"endpoint": netbox.dcim.device_bay_templates},
    "device-bays":                  {"endpoint": netbox.dcim.device_bays},
    "device-roles":                 {"endpoint": netbox.dcim.device_roles},
    "device-types":                 {"endpoint": netbox.dcim.device_types},
    "devices":                      {"endpoint": netbox.dcim.devices},
    "front-port-templates":         {"endpoint": netbox.dcim.front_port_templates},
    "front-ports":                  {"endpoint": netbox.dcim.front_ports},
    "interface-templates":          {"endpoint": netbox.dcim.interface_templates},
    "interfaces":                   {"endpoint": netbox.dcim.interfaces},
    "inventory-item-roles":         {"endpoint": netbox.dcim.inventory_item_roles},
    "inventory-item-templates":     {"endpoint": netbox.dcim.inventory_item_templates},
    "inventory-items":              {"endpoint": netbox.dcim.inventory_items},
    "locations":                    {"endpoint": netbox.dcim.locations},
    "mac-addresses":                {"endpoint": netbox.dcim.mac_addresses},
    "manufacturers":                {"endpoint": netbox.dcim.manufacturers},
    "module-bay-templates":         {"endpoint": netbox.dcim.module_bay_templates},
    "module-bays":                  {"endpoint": netbox.dcim.module_bays},
    "module-type-profiles":         {"endpoint": netbox.dcim.module_types_profiles},
    "module-types":                 {"endpoint": netbox.dcim.module_types},
    "modules":                      {"endpoint": netbox.dcim.modules},
    "platforms":                    {"endpoint": netbox.dcim.platforms},
    "power-feeds":                  {"endpoint": netbox.dcim.power_feeds},
    "power-outlet-templates":       {"endpoint": netbox.dcim.power_outlet_templates},
    "power-outlets":                {"endpoint": netbox.dcim.power_outlets},
    "power-panels":                 {"endpoint": netbox.dcim.power_panels},
    "power-port-templates":         {"endpoint": netbox.dcim.power_port_templates},
    "power-ports":                  {"endpoint": netbox.dcim.power_ports},
    "rack-reservations":            {"endpoint": netbox.dcim.rack_reservations},
    "rack-roles":                   {"endpoint": netbox.dcim.rack_roles},
    "rack-types":                   {"endpoint": netbox.dcim.rack_types},
    "racks":                        {"endpoint": netbox.dcim.racks},
    "rear-port-templates":          {"endpoint": netbox.dcim.rear_port_templates},
    "rear-ports":                   {"endpoint": netbox.dcim.rear_ports},
    "regions":                      {"endpoint": netbox.dcim.regions},
    "site-groups":                  {"endpoint": netbox.dcim.site_groups},
    "sites":                        {"endpoint": netbox.dcim.sites},
    "virtual-chassis":              {"endpoint": netbox.dcim.virtual_chassis},
    "virtual-device-contexts":      {"endpoint": netbox.dcim.virtual_device_contexts},

    # Extras
    "config-context-profiles":      {"endpoint": netbox.extras.config_context_profiles},
    "config-contexts":              {"endpoint": netbox.extras.config_contexts},
    "config-templates":             {"endpoint": netbox.extras.config_templates},
    "custom-field-choice-sets":     {"endpoint": netbox.extras.custom_field_choice_sets},
    "custom-fields":                {"endpoint": netbox.extras.custom_fields},
    "custom-links":                 {"endpoint": netbox.extras.custom_links},
    "event-rules":                  {"endpoint": netbox.extras.event_rules},
    "export-templates":             {"endpoint": netbox.extras.export_templates},
    "image-attachments":            {"endpoint": netbox.extras.image_attachments},
    "journal-entries":              {"endpoint": netbox.extras.journal_entries},
    "notification-groups":          {"endpoint": netbox.extras.notification_groups},
    "notifications":                {"endpoint": netbox.extras.notifications},
    "object-types":                 {"endpoint": netbox.extras.object_types},
    "saved-filters":                {"endpoint": netbox.extras.saved_filters},
    "scripts":                      {"endpoint": netbox.extras.scripts},
    "subscriptions":                {"endpoint": netbox.extras.subscriptions},
    "table-configs":                {"endpoint": netbox.extras.table_configs},
    "tagged-objects":               {"endpoint": netbox.extras.tagged_objects},
    "tags":                         {"endpoint": netbox.extras.tags},
    "webhooks":                     {"endpoint": netbox.extras.webhooks},

    # IPAM
    "aggregates":                   {"endpoint": netbox.ipam.aggregates},
    "asn-ranges":                   {"endpoint": netbox.ipam.asn_ranges},
    "asns":                         {"endpoint": netbox.ipam.asns},
    "fhrp-group-assignments":       {"endpoint": netbox.ipam.fhrp_group_assignments},
    "fhrp-groups":                  {"endpoint": netbox.ipam.fhrp_groups},
    "ip-addresses":                 {"endpoint": netbox.ipam.ip_addresses},
    "ip-ranges":                    {"endpoint": netbox.ipam.ip_ranges},
    "prefixes":                     {"endpoint": netbox.ipam.prefixes},
    "rirs":                         {"endpoint": netbox.ipam.rirs},
    "roles":                        {"endpoint": netbox.ipam.roles},
    "route-targets":                {"endpoint": netbox.ipam.route_targets},
    "service-templates":            {"endpoint": netbox.ipam.service_templates},
    "services":                     {"endpoint": netbox.ipam.services},
    "vlan-groups":                  {"endpoint": netbox.ipam.vlan_groups},
    "vlan-translation-policies":    {"endpoint": netbox.ipam.vlan_translation_policies},
    "vlan-translation-rules":       {"endpoint": netbox.ipam.vlan_translation_rules},
    "vlans":                        {"endpoint": netbox.ipam.vlans},
    "vrfs":                         {"endpoint": netbox.ipam.vrfs},

    # Tenancy
    "contact-assignments":          {"endpoint": netbox.tenancy.contact_assignments},
    "contact-groups":               {"endpoint": netbox.tenancy.contact_groups},
    "contact-roles":                {"endpoint": netbox.tenancy.contact_roles},
    "contacts":                     {"endpoint": netbox.tenancy.contacts},
    "tenant-groups":                {"endpoint": netbox.tenancy.tenant_groups},
    "tenants":                      {"endpoint": netbox.tenancy.tenants},
    
    # Users
    "config":                       {"endpoint": netbox.users.config},
    "groups":                       {"endpoint": netbox.users.groups},
    "permissions":                  {"endpoint": netbox.users.permissions},
    "tokens":                       {"endpoint": netbox.users.tokens},
    "users":                        {"endpoint": netbox.users.users},

    # Virtualization
    "cluster-groups":               {"endpoint": netbox.virtualization.cluster_groups},
    "cluster-types":                {"endpoint": netbox.virtualization.cluster_types},
    "clusters":                     {"endpoint": netbox.virtualization.clusters},
    "virtualization-interfaces":    {"endpoint": netbox.virtualization.interfaces},
    "virtual-disks":                {"endpoint": netbox.virtualization.virtual_disks},
    "virtual-machines":             {"endpoint": netbox.virtualization.virtual_machines},

    # VPN
    "ike-policies":                 {"endpoint": netbox.vpn.ike_policies},
    "ike-proposals":                {"endpoint": netbox.vpn.ike_proposals},
    "ipsec-policies":               {"endpoint": netbox.vpn.ipsec_policies},
    "ipsec-profiles":               {"endpoint": netbox.vpn.ipsec_profiles},
    "ipsec-proposals":              {"endpoint": netbox.vpn.ipsec_proposals},
    "l2vpn-terminations":           {"endpoint": netbox.vpn.l2vpn_terminations},
    "l2vpns":                       {"endpoint": netbox.vpn.l2vpns},
    "tunnel-groups":                {"endpoint": netbox.vpn.tunnel_groups},
    "tunnel-terminations":          {"endpoint": netbox.vpn.tunnel_terminations},
    "tunnels":                      {"endpoint": netbox.vpn.tunnels},

    # Deprecated / Removed
    # DCIM
    "console-connections": {"endpoint": netbox.dcim.console_connections},
    "interface-connections": {"endpoint": netbox.dcim.interface_connections},
    "rack-groups": {"endpoint": netbox.dcim.rack_groups},
    "module-bay-types": {"endpoint": netbox.dcim.module_bay_types},
    "power-connections": {"endpoint": netbox.dcim.power_connections},
    "export-templates": {"endpoint": netbox.dcim.export_templates},
}

    major, minor, patch = tuple(map(int, pynetbox.__version__.split(".")))
    netbox_versiontuple = tuple(map(int, netbox.version.split(".")))

    if (major, minor, patch) >= (6, 4):
        netbox_endpoint_map["wireless-lan-groups"] = {
            "endpoint": netbox.wireless.wireless_lan_groups
        }
        netbox_endpoint_map["wireless-lan-groups"] = {
            "endpoint": netbox.wireless.wireless_lan_groups
        }
        netbox_endpoint_map["wireless-lans"] = {
            "endpoint": netbox.wireless.wireless_lans
        }
        netbox_endpoint_map["wireless-links"] = {
            "endpoint": netbox.wireless.wireless_links
        }

    else:
        if "wireless" in term:
            Display().v(
                "pynetbox version %d.%d.%d does not support wireless app; please update to v6.4.0 or newer."
                % (major, minor, patch)
            )

    if (major, minor, patch) < (7, 0, 1):
        netbox_endpoint_map["secret-roles"] = {"endpoint": netbox.secrets.secret_roles}
        netbox_endpoint_map["secrets"] = {"endpoint": netbox.secrets.secrets}

    if netbox_versiontuple >= (3, 7):
        if (major, minor, patch) >= (7, 3):
            netbox_endpoint_map["l2vpn-terminations"] = {
                "endpoint": netbox.vpn.l2vpn_terminations
            }
            netbox_endpoint_map["l2vpns"] = {"endpoint": netbox.vpn.l2vpns}
            netbox_endpoint_map["tunnel-terminations"] = {
                "endpoint": netbox.vpn.tunnel_terminations
            }
            netbox_endpoint_map["tunnels"] = {"endpoint": netbox.vpn.tunnels}

        else:
            if "l2vpn" in term:
                Display().v(
                    "pynetbox version %d.%d.%d does not support vpn app; please update to v7.3.0 or newer."
                    % (major, minor, patch)
                )

    else:
        netbox_endpoint_map["l2vpn-terminations"] = {
            "endpoint": netbox.ipam.l2vpn_terminations
        }
        netbox_endpoint_map["l2vpns"] = {"endpoint": netbox.ipam.l2vpns}

    if netbox_versiontuple >= (4, 2):
        netbox_endpoint_map["mac-addresses"] = {"endpoint": netbox.dcim.mac_addresses}

    return netbox_endpoint_map[term]["endpoint"]


def build_filters(filters):
    """
    This will build the filters to be handed to NetBox endpoint call if they exist.

    Args:
        filters (str): String of filters to parse.

    Returns:
        result (list): List of dictionaries to filter by.
    """
    filter = {}
    args_split = split_args(filters)
    args = [parse_kv(x) for x in args_split]
    for arg in args:
        for k, v in arg.items():
            if k not in filter:
                filter[k] = list()
                filter[k].append(v)
            else:
                filter[k].append(v)

    return filter


def get_plugin_endpoint(netbox, plugin, term):
    """
    get_plugin_endpoint(netbox, plugin, term)
        netbox: a predefined pynetbox.api() pointing to a valid instance
                of NetBox
        plugin: a string referencing the plugin name
        term: the term passed to the lookup function upon which the api
              call will be identified
    """
    attr = "plugins.%s.%s" % (plugin, term)

    def _getattr(netbox, attr):
        return getattr(netbox, attr)

    return functools.reduce(_getattr, [netbox] + attr.split("."))


def make_netbox_call(nb_endpoint, filters=None):
    """
    Wrapper for calls to NetBox and handle any possible errors.

    Args:
        nb_endpoint (object): The NetBox endpoint object to make calls.

    Returns:
        results (object): Pynetbox result.

    Raises:
        AnsibleError: Ansible Error containing an error message.
    """
    try:
        if filters:
            results = nb_endpoint.filter(**filters)
        else:
            results = nb_endpoint.all()
    except pynetbox.RequestError as e:
        if e.req.status_code == 404 and "plugins" in e:
            raise AnsibleError(
                "{0} - Not a valid plugin endpoint, please make sure to provide valid plugin endpoint.".format(
                    e.error
                )
            )
        else:
            raise AnsibleError(e.error)

    return results


class LookupModule(LookupBase):
    """
    LookupModule(LookupBase) is defined by Ansible
    """

    def run(self, terms, variables=None, **kwargs):
        if PYNETBOX_LIBRARY_IMPORT_ERROR:
            raise AnsibleError(
                "pynetbox must be installed to use this plugin"
            ) from PYNETBOX_LIBRARY_IMPORT_ERROR

        if REQUESTS_LIBRARY_IMPORT_ERROR:
            raise AnsibleError(
                "requests must be installed to use this plugin"
            ) from REQUESTS_LIBRARY_IMPORT_ERROR

        netbox_api_token = (
            kwargs.get("token")
            or os.getenv("NETBOX_TOKEN")
            or os.getenv("NETBOX_API_TOKEN")
        )
        netbox_api_endpoint = (
            kwargs.get("api_endpoint")
            or os.getenv("NETBOX_API")
            or os.getenv("NETBOX_URL")
        )
        netbox_headers = kwargs.get("headers") or os.getenv("NETBOX_HEADERS") or {}
        netbox_ssl_verify = kwargs.get("validate_certs", True)
        netbox_private_key = kwargs.get("private_key")
        netbox_private_key_file = kwargs.get("key_file")
        netbox_api_filter = kwargs.get("api_filter")
        netbox_raw_return = kwargs.get("raw_data")
        netbox_plugin = kwargs.get("plugin")

        if not isinstance(terms, list):
            terms = [terms]

        if isinstance(netbox_headers, str):
            netbox_headers = json.loads(netbox_headers)

        try:
            session = requests.Session()
            session.headers = netbox_headers
            session.verify = netbox_ssl_verify

            if Version(version("pynetbox")) < Version("7.0.0"):
                netbox = pynetbox.api(
                    netbox_api_endpoint,
                    token=netbox_api_token if netbox_api_token else None,
                    private_key=netbox_private_key,
                    private_key_file=netbox_private_key_file,
                )
            else:
                netbox = pynetbox.api(
                    netbox_api_endpoint,
                    token=netbox_api_token if netbox_api_token else None,
                )
            netbox.http_session = session
        except FileNotFoundError:
            raise AnsibleError(
                "%s cannot be found. Please make sure file exists."
                % netbox_private_key_file
            )

        results = []
        for term in terms:
            if netbox_plugin:
                endpoint = get_plugin_endpoint(netbox, netbox_plugin, term)
            else:
                try:
                    endpoint = get_endpoint(netbox, term)
                except KeyError:
                    raise AnsibleError(
                        "Unrecognised term %s. Check documentation" % term
                    )

            Display().vvvv(
                "NetBox lookup for %s to %s using token %s filter %s"
                % (term, netbox_api_endpoint, netbox_api_token, netbox_api_filter)
            )

            if netbox_api_filter:
                filter = build_filters(netbox_api_filter)

                if "id" in filter and len(filter["id"]) == 1:
                    Display().vvvv(
                        "Filter is: %s and includes id, will use .get instead of .filter"
                        % (filter)
                    )
                    try:
                        id = int(filter["id"][0])
                        nb_data = endpoint.get(id)
                        data = dict(nb_data)
                        Display().vvvvv(pformat(data))
                        return [data]
                    except pynetbox.RequestError as e:
                        raise AnsibleError(e.error)

                Display().vvvv("filter is %s" % filter)

            # Make call to NetBox API and capture any failures
            nb_data = make_netbox_call(
                endpoint, filters=filter if netbox_api_filter else None
            )

            for data in nb_data:
                data = dict(data)
                Display().vvvvv(pformat(data))

                if netbox_raw_return:
                    results.append(data)
                else:
                    key = data["id"]
                    result = {key: data}
                    results.extend(self._flatten_hash_to_list(result))

        return results
