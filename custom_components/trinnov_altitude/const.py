"""Constants for the Trinnov Altitude integration."""

import socket

CLIENT_ID = "Home Assistant Trinnov Altitude Integration"
DOMAIN = "trinnov_altitude"
MANUFACTURER = "Trinnov"
MODEL = "Altitude"
NAME = f"{MANUFACTURER} {MODEL}"

ATTR_ENTRY_ID = "entry_id"
ATTR_SOURCE = "source"
ATTR_PRESET_ID = "preset_id"
ATTR_UPMIXER = "upmixer"

SERVICE_SET_SOURCE_BY_NAME = "set_source_by_name"
SERVICE_SET_PRESET = "set_preset"
SERVICE_SET_UPMIXER = "set_upmixer"

CONF_WOL_HOST = "wol_host"
CONF_WOL_PORT = "wol_port"
CONF_WOL_INTERFACE = "wol_interface"
CONF_WOL_FAMILY = "wol_family"
DEFAULT_WOL_HOST = "255.255.255.255"
DEFAULT_WOL_PORT = 9
DEFAULT_WOL_FAMILY = "ipv4"
WOL_FAMILIES = {
    "ipv4": socket.AF_INET,
    "ipv6": socket.AF_INET6,
}
