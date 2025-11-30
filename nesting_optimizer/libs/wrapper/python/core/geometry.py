"""
Geometry classes for 2D nesting operations.
"""

import os
import sys
from typing import List, Tuple, Union, Optional

# Import the C++ extension
wrapper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cpp/build"))
if wrapper_dir not in sys.path:
    sys.path.insert(0, wrapper_dir)

try:
    import nest2d_wrapper
    _Point = nest2d_wrapper.Point
    _Sheet = nest2d_wrapper.Sheet
    _Shape = nest2d_wrapper.Shape
except ImportError as e:
    raise ImportError(f"Failed to import C++ nest2d_wrapper: {e}. "
                     f"Make sure the C++ extension is built in {wrapper_dir}")

class Point:
    """
    2D Point with x, y coordinates.

    Examples:
        >>> p = Point(10.0, 20.0)
        >>> print(p.x, p.y)
        10.0 20.0
    """

    def __init__(self, x: float = 0.0, y: float = 0.0):
        """Create a new point.

        Args:
            x: X coordinate in millimeters
            y: Y coordinate in millimeters
        """
        self._internal = _Point(x, y)

    @property
    def x(self) -> float:
        """X coordinate in millimeters."""
        return self._internal.x

    @x.setter
    def x(self, value: float):
        self._internal.x = value

    @property
    def y(self) -> float:
        """Y coordinate in millimeters."""
        return self._internal.y

    @y.setter
    def y(self, value: float):
        self._internal.y = value

    def __str__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6

    def distance_to(self, other: 'Point') -> float:
        """Calculate distance to another point."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx*dx + dy*dy) ** 0.5


class Sheet:
    """
    Material sheet that shapes will be cut from.

    Examples:
        >>> sheet = Sheet(100.0, 200.0)
        >>> print(sheet.width, sheet.height)
        100.0 200.0
    """

    def __init__(self, width: float, height: float):
        """Create a new sheet.

        Args:
            width: Width in millimeters
            height: Height in millimeters
        """
        self._internal = _Sheet(width, height)

    @property
    def width(self) -> float:
        """Width in millimeters."""
        return self._internal.width

    @width.setter
    def width(self, value: float):
        self._internal.width = value

    @property
    def height(self) -> float:
        """Height in millimeters."""
        return self._internal.height

    @height.setter
    def height(self, value: float):
        self._internal.height = value

    @property
    def area(self) -> float:
        """Area of the sheet."""
        return self.width * self.height

    def __str__(self) -> str:
        return f"Sheet(width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return self.__str__()


class Shape:
    """
    2D Shape that will be cut from a sheet.

    Examples:
        >>> # Create a rectangle
        >>> rect_points = [[0, 0], [10, 0], [10, 5], [0, 5]]
        >>> shape = Shape(rect_points)
        >>> print(shape.area())
        50.0

        >>> # Transform the shape
        >>> shape.translate(5, 10)
        >>> shape.rotate(45)
    """

    def __init__(self, points: List[List[float]]):
        """Create a shape from a list of points.

        Args:
            points: List of [x, y] coordinates defining the polygon outline
        """
        self._internal = _Shape(points)

    # Geometric properties
    def area(self) -> float:
        """Get area of the shape in square millimeters."""
        return self._internal.area()

    def vertex_count(self) -> int:
        """Get number of vertices."""
        return self._internal.vertex_count()

    def is_convex(self) -> bool:
        """Check if the shape is convex."""
        return self._internal.is_convex()

    def bounding_box(self) -> dict:
        """Get bounding box as dictionary with min_x, min_y, max_x, max_y, width, height."""
        return self._internal.bounding_box()

    # Transformations
    def translate(self, x: float, y: float) -> None:
        """Translate (move) the shape by given offset.

        Args:
            x: X offset in millimeters
            y: Y offset in millimeters
        """
        self._internal.translate(x, y)

    def rotate(self, angle_degrees: float) -> None:
        """Rotate the shape by given angle.

        Args:
            angle_degrees: Rotation angle in degrees
        """
        self._internal.rotate(angle_degrees)

    def set_inflation(self, distance: float) -> None:
        """Set polygon offset distance (positive = expand, negative = shrink).

        Args:
            distance: Offset distance in millimeters
        """
        self._internal.set_inflation(distance)

    # State management
    def set_sheet_id(self, sheet_id: int) -> None:
        """Set which sheet this shape belongs to."""
        self._internal.set_sheet_id(sheet_id)

    def get_sheet_id(self) -> int:
        """Get sheet ID (-1 means not assigned)."""
        return self._internal.get_sheet_id()

    def set_priority(self, priority: int) -> None:
        """Set shape priority (higher priority shapes are placed first)."""
        self._internal.set_priority(priority)

    def get_priority(self) -> int:
        """Get shape priority."""
        return self._internal.get_priority()

    def is_fixed(self) -> bool:
        """Check if shape is fixed in position."""
        return self._internal.is_fixed()

    def mark_as_fixed_in_sheet(self, sheet_id: int) -> None:
        """Mark shape as fixed in specific sheet."""
        self._internal.mark_as_fixed_in_sheet(sheet_id)

    # Shape access
    def get_transformed_shape(self) -> List[List[float]]:
        """Get final transformed polygon points."""
        return self._internal.get_transformed_shape()

    def get_raw_shape(self) -> List[List[float]]:
        """Get original polygon points before transformation."""
        return self._internal.get_raw_shape()

    def reset_transformation(self) -> None:
        """Reset all transformations to original state."""
        self._internal.reset_transformation()

    # Position info
    def get_translation(self) -> Point:
        """Get current translation as Point."""
        internal_point = self._internal.get_translation()
        return Point(internal_point.x, internal_point.y)

    def get_rotation_degrees(self) -> float:
        """Get current rotation in degrees."""
        return self._internal.get_rotation_degrees()

    # Geometric queries
    def is_point_inside(self, x: float, y: float) -> bool:
        """Check if a point is inside this shape."""
        return self._internal.is_point_inside(x, y)

    def contains_shape(self, other: 'Shape') -> bool:
        """Check if this shape completely contains another shape."""
        return self._internal.contains_shape(other._internal)

    def __str__(self) -> str:
        return self._internal.__str__()

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def create_rectangle(width: float, height: float) -> 'Shape':
        """Create a rectangular shape.

        Args:
            width: Rectangle width in millimeters
            height: Rectangle height in millimeters

        Returns:
            New rectangular Shape
        """
        points = [[0, 0], [width, 0], [width, height], [0, height]]
        return Shape(points)

    @staticmethod
    def create_circle(radius: float, segments: int = 32) -> 'Shape':
        """Create a circular shape (approximated with polygon).

        Args:
            radius: Circle radius in millimeters
            segments: Number of segments for approximation

        Returns:
            New circular Shape
        """
        import math
        points = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append([x, y])
        return Shape(points)
