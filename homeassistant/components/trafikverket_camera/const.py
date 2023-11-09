"""Adds constants for Trafikverket Camera integration."""
from enum import Enum
from homeassistant.const import Platform

DOMAIN = "trafikverket_camera"
CONF_LOCATION = "location"
PLATFORMS = [Platform.BINARY_SENSOR, Platform.CAMERA, Platform.SENSOR]
ATTRIBUTION = "Data provided by Trafikverket"

ATTR_DESCRIPTION = "description"
ATTR_TYPE = "type"


class TrafficMeasure(Enum):
    Unknown = 0
    Low = 1
    Medium = 2
    High = 3
    Critical = 4

