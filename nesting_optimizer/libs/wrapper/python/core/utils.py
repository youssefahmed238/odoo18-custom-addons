"""
Utility functions for geometric operations and conversions.
"""

import os
import sys
from typing import List, Dict, Any, Tuple

# Import the C++ extension
wrapper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cpp/build"))
if wrapper_dir not in sys.path:
    sys.path.insert(0, wrapper_dir)

try:
    import nest2d_wrapper
    _polygon_area = nest2d_wrapper.polygon_area
    _polygon_bounds = nest2d_wrapper.polygon_bounds
    _point_in_polygon = nest2d_wrapper.point_in_polygon
    _polygon_centroid = nest2d_wrapper.polygon_centroid
    _polygon_is_convex = nest2d_wrapper.polygon_is_convex
    _polygon_rotate = nest2d_wrapper.polygon_rotate
    _polygon_translate = nest2d_wrapper.polygon_translate
    _polygon_offset = nest2d_wrapper.polygon_offset
    _mm_to_coord = nest2d_wrapper.mm_to_coord
    _coord_to_mm = nest2d_wrapper.coord_to_mm
except ImportError as e:
    raise ImportError(f"Failed to import C++ nest2d_wrapper: {e}. "
                     f"Make sure the C++ extension is built in {wrapper_dir}")


def polygon_area(points: List[List[float]]) -> float:
    """
    Calculate the area of a polygon.

    Args:
        points: List of [x, y] coordinates defining the polygon

    Returns:
        Area in square millimeters

    Examples:
        >>> # Area of a 10x5 rectangle
        >>> rect = [[0, 0], [10, 0], [10, 5], [0, 5]]
        >>> area = polygon_area(rect)
        >>> print(area)  # 50.0
    """
    return _polygon_area(points)


def polygon_bounds(points: List[List[float]]) -> Dict[str, float]:
    """
    Get the bounding box of a polygon.

    Args:
        points: List of [x, y] coordinates defining the polygon

    Returns:
        Dictionary with keys: min_x, min_y, max_x, max_y, width, height

    Examples:
        >>> rect = [[5, 10], [15, 10], [15, 20], [5, 20]]
        >>> bounds = polygon_bounds(rect)
        >>> print(bounds)
        {'min_x': 5.0, 'min_y': 10.0, 'max_x': 15.0, 'max_y': 20.0, 'width': 10.0, 'height': 10.0}
    """
    return _polygon_bounds(points)


def point_in_polygon(polygon_points: List[List[float]], x: float, y: float) -> bool:
    """
    Check if a point is inside a polygon.

    Args:
        polygon_points: List of [x, y] coordinates defining the polygon
        x: X coordinate of the test point
        y: Y coordinate of the test point

    Returns:
        True if point is inside polygon, False otherwise

    Examples:
        >>> rect = [[0, 0], [10, 0], [10, 10], [0, 10]]
        >>> point_in_polygon(rect, 5, 5)  # Inside
        True
        >>> point_in_polygon(rect, 15, 5)  # Outside
        False
    """
    return _point_in_polygon(polygon_points, x, y)


def polygon_centroid(points: List[List[float]]) -> List[float]:
    """
    Get the centroid (geometric center) of a polygon.

    Args:
        points: List of [x, y] coordinates defining the polygon

    Returns:
        List with [x, y] coordinates of the centroid

    Examples:
        >>> rect = [[0, 0], [10, 0], [10, 10], [0, 10]]
        >>> center = polygon_centroid(rect)
        >>> print(center)  # [5.0, 5.0]
    """
    return _polygon_centroid(points)


def polygon_is_convex(points: List[List[float]]) -> bool:
    """
    Check if a polygon is convex.

    Args:
        points: List of [x, y] coordinates defining the polygon

    Returns:
        True if polygon is convex, False otherwise

    Examples:
        >>> rect = [[0, 0], [10, 0], [10, 10], [0, 10]]
        >>> polygon_is_convex(rect)
        True

        >>> # L-shaped polygon (concave)
        >>> l_shape = [[0, 0], [5, 0], [5, 5], [10, 5], [10, 10], [0, 10]]
        >>> polygon_is_convex(l_shape)
        False
    """
    return _polygon_is_convex(points)


def polygon_rotate(points: List[List[float]], angle_degrees: float) -> List[List[float]]:
    """
    Rotate a polygon by a given angle.

    Args:
        points: List of [x, y] coordinates defining the polygon
        angle_degrees: Rotation angle in degrees (positive = counterclockwise)

    Returns:
        List of rotated [x, y] coordinates

    Examples:
        >>> rect = [[0, 0], [10, 0], [10, 5], [0, 5]]
        >>> rotated = polygon_rotate(rect, 90)  # Rotate 90 degrees
    """
    return _polygon_rotate(points, angle_degrees)


def polygon_translate(points: List[List[float]], dx: float, dy: float) -> List[List[float]]:
    """
    Translate (move) a polygon by a given offset.

    Args:
        points: List of [x, y] coordinates defining the polygon
        dx: X offset in millimeters
        dy: Y offset in millimeters

    Returns:
        List of translated [x, y] coordinates

    Examples:
        >>> rect = [[0, 0], [10, 0], [10, 5], [0, 5]]
        >>> moved = polygon_translate(rect, 5, 10)
        >>> # Now rect is at position (5, 10) instead of (0, 0)
    """
    return _polygon_translate(points, dx, dy)


def polygon_offset(points: List[List[float]], distance: float) -> List[List[float]]:
    """
    Offset/inflate a polygon by a given distance.

    Args:
        points: List of [x, y] coordinates defining the polygon
        distance: Offset distance in millimeters (positive = expand, negative = shrink)

    Returns:
        List of offset [x, y] coordinates

    Examples:
        >>> rect = [[0, 0], [10, 0], [10, 10], [0, 10]]
        >>> expanded = polygon_offset(rect, 1.0)  # Expand by 1mm
        >>> shrunk = polygon_offset(rect, -1.0)   # Shrink by 1mm
    """
    return _polygon_offset(points, distance)


def mm_to_coord(mm: float) -> int:
    """
    Convert millimeters to internal coordinate units.

    Args:
        mm: Distance in millimeters

    Returns:
        Distance in internal coordinate units

    Note:
        This is mainly for internal use. The wrapper handles conversions automatically.
    """
    return _mm_to_coord(mm)


def coord_to_mm(coord: int) -> float:
    """
    Convert internal coordinate units to millimeters.

    Args:
        coord: Distance in internal coordinate units

    Returns:
        Distance in millimeters

    Note:
        This is mainly for internal use. The wrapper handles conversions automatically.
    """
    return _coord_to_mm(coord)


def calculate_area(polygon_points: List[List[float]]) -> float:
    """
    Legacy function name for backward compatibility.

    This is an alias for polygon_area().
    """
    return polygon_area(polygon_points)


def get_bounds(polygon_points: List[List[float]]) -> Dict[str, float]:
    """
    Legacy function name for backward compatibility.

    This is an alias for polygon_bounds().
    """
    return polygon_bounds(polygon_points)


def is_point_inside(polygon_points: List[List[float]], x: float, y: float) -> bool:
    """
    Legacy function name for backward compatibility.

    This is an alias for point_in_polygon().
    """
    return point_in_polygon(polygon_points, x, y)
