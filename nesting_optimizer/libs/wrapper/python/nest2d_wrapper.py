import os
import sys

wrapper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cpp/build"))
if wrapper_dir not in sys.path:
    sys.path.append(wrapper_dir)

from nest2d_wrapper import add, nest_polygons, polygon_area, polygon_bounds, point_in_polygon


def add_numbers(a, b):
    """Legacy test function"""
    return add(a, b)


def nest_shapes(polygons, sheet_width, sheet_height, spacing=0.0):
    """
    Nest a list of polygon shapes on material sheets.

    Args:
        polygons: List of polygons, where each polygon is a list of [x, y] points
        sheet_width: Width of the material sheet in units
        sheet_height: Height of the material sheet in units
        spacing: Minimum spacing between objects (default: 0.0)

    Returns:
        Dictionary with nesting results including items, bins_used, positions, etc.
    """
    return nest_polygons(polygons, sheet_width, sheet_height, spacing)


def calculate_area(polygon_points):
    """
    Calculate the area of a polygon.

    Args:
        polygon_points: List of [x, y] points defining the polygon

    Returns:
        Area of the polygon
    """
    return polygon_area(polygon_points)


def get_bounds(polygon_points):
    """
    Get the bounding box of a polygon.

    Args:
        polygon_points: List of [x, y] points defining the polygon

    Returns:
        Dictionary with min_x, min_y, max_x, max_y, width, height
    """
    return polygon_bounds(polygon_points)


def is_point_inside(polygon_points, x, y):
    """
    Check if a point is inside a polygon.

    Args:
        polygon_points: List of [x, y] points defining the polygon
        x: X coordinate of the point
        y: Y coordinate of the point

    Returns:
        True if point is inside polygon, False otherwise
    """
    return point_in_polygon(polygon_points, x, y)

