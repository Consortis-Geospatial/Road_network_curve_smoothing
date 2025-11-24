# -*- coding: utf-8 -*-
"""
Init file for the Road Network Curve Smoothing QGIS Plugin.
"""

def classFactory(iface):
    """Load RoadNetworkCurveSmoothing class from file."""
    from .road_network_curve_smoothing import RoadNetworkCurveSmoothing
    return RoadNetworkCurveSmoothing(iface)
