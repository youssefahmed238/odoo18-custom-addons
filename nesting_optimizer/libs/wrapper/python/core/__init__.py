"""
LibNest2D Python Wrapper - Core Module
=====================================

This module provides Python classes and functions that wrap the C++ libnest2d library
for 2D bin packing and nesting optimization.
"""

from .geometry import Point, Sheet, Shape
from .config import NestConfig
from .nesting import nest_shapes, nest_polygons, nest_polygons_batch
from .utils import (
    polygon_area, polygon_bounds, point_in_polygon,
    polygon_centroid, polygon_is_convex, polygon_rotate,
    polygon_translate, polygon_offset, mm_to_coord, coord_to_mm
)

__all__ = [
    # Core classes
    'Point', 'Sheet', 'Shape', 'NestConfig',

    # Main nesting functions
    'nest_shapes', 'nest_polygons', 'nest_polygons_batch',

    # Utility functions
    'polygon_area', 'polygon_bounds', 'point_in_polygon',
    'polygon_centroid', 'polygon_is_convex', 'polygon_rotate',
    'polygon_translate', 'polygon_offset',

    # Conversion utilities
    'mm_to_coord', 'coord_to_mm',
]

# Version information
__version__ = "1.0.0"
__author__ = "LibNest2D Python Wrapper Team"
__description__ = "2D bin packing and nesting optimization library"
