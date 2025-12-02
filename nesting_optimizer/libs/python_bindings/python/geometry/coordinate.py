"""
LibNest2D Coordinate System Python Interface

This module provides a Python-friendly interface to the LibNest2D coordinate system.
It wraps the low-level C++ bindings with convenient Python functions and classes.
"""

import os
import sys
from typing import Union

# Add the build directory to Python path to find the compiled module
binding_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../build"))
if binding_dir not in sys.path:
    sys.path.insert(0, binding_dir)

try:
    # Import the compiled C++ module (matches PYBIND11_MODULE name)
    import nest2d

    # Re-export the core types and functions from the C++ module
    Coord = nest2d.Coord
    MM_IN_COORDS = nest2d.MM_IN_COORDS

    # Re-export conversion functions
    mm = nest2d.mm
    coord_to_mm = nest2d.coord_to_mm
    from_mm = nest2d.from_mm
    from_cm = nest2d.from_cm
    from_inches = nest2d.from_inches

except ImportError as e:
    raise ImportError(
        f"Failed to import LibNest2D C++ module from {binding_dir}. "
        f"Make sure it's compiled. Error: {e}"
    ) from e


# Python-specific convenience functions and improved interfaces
class Coordinate:
    """
    High-level coordinate system utilities for LibNest2D.

    This class provides convenient methods for working with coordinates
    and unit conversions in a more Pythonic way.
    """

    @staticmethod
    def create_coord(value: Union[int, float], unit: str = 'coord') -> Coord:
        """
        Create a coordinate from a value with specified unit.

        Args:
            value: Numeric value
            unit: Unit type ('coord', 'mm', 'cm', 'inches')

        Returns:
            Coord: Coordinate in internal units

        Example:
            >>> coord = Coordinate.create_coord(10.5, 'mm')
            >>> print(coord)  # 10500000
        """
        unit = unit.lower()
        if unit == 'coord':
            return Coord(int(value))
        elif unit == 'mm':
            return mm(value)
        elif unit == 'cm':
            return from_cm(value)
        elif unit in ['inch', 'inches']:
            return from_inches(value)
        else:
            raise ValueError(f"Unsupported unit: {unit}. Use 'coord', 'mm', 'cm', or 'inches'")

    @staticmethod
    def to_unit(coord: Coord, unit: str = 'mm') -> float:
        """
        Convert coordinate to specified unit.

        Args:
            coord: Coordinate in internal units
            unit: Target unit ('mm', 'cm', 'inches')

        Returns:
            float: Value in requested unit

        Example:
            >>> coord = mm(25.4)
            >>> inches = Coordinate.to_unit(coord, 'inches')
            >>> print(inches)  # 1.0
        """
        unit = unit.lower()
        mm_value = coord_to_mm(coord)

        if unit == 'mm':
            return mm_value
        elif unit == 'cm':
            return mm_value / 10.0
        elif unit in ['inch', 'inches']:
            return mm_value / 25.4
        else:
            raise ValueError(f"Unsupported unit: {unit}. Use 'mm', 'cm', or 'inches'")

    @staticmethod
    def format_coord(coord: Coord, unit: str = 'mm', precision: int = 3) -> str:
        """
        Format coordinate as human-readable string.

        Args:
            coord: Coordinate to format
            unit: Display unit
            precision: Decimal places

        Returns:
            str: Formatted coordinate string

        Example:
            >>> coord = mm(12.345)
            >>> formatted = Coordinate.format_coord(coord, 'mm', 2)
            >>> print(formatted)  # "12.35 mm"
        """
        value = Coordinate.to_unit(coord, unit)
        return f"{value:.{precision}f} {unit}"


def create_point(x: Union[int, float], y: Union[int, float], unit: str = 'mm') -> tuple[Coord, Coord]:
    """
    Create a coordinate pair (x, y) from numeric values.

    Args:
        x: X coordinate value
        y: Y coordinate value
        unit: Input unit ('mm', 'cm', 'inches', 'coord')

    Returns:
        tuple: (x_coord, y_coord) in internal units

    Example:
        >>> x, y = create_point(10.5, 20.3, 'mm')
        >>> print(f"X: {x}, Y: {y}")
    """
    x_coord = Coordinate.create_coord(x, unit)
    y_coord = Coordinate.create_coord(y, unit)
    return (x_coord, y_coord)


def coord_range(start: Union[int, float], stop: Union[int, float],
                step: Union[int, float], unit: str = 'mm') -> list[Coord]:
    """
    Generate a range of coordinates like Python's range() function.

    Args:
        start: Start value
        stop: Stop value (exclusive)
        step: Step size
        unit: Input unit

    Returns:
        list: List of coordinates

    Example:
        >>> coords = coord_range(0, 10, 2.5, 'mm')  # [0mm, 2.5mm, 5mm, 7.5mm]
    """
    coords = []
    current = start
    while current < stop:
        coords.append(Coordinate.create_coord(current, unit))
        current += step
    return coords


# Validation functions
def validate_coord(coord: Coord) -> bool:
    """
    Validate that a coordinate is within reasonable bounds.

    Args:
        coord: Coordinate to validate

    Returns:
        bool: True if coordinate is valid
    """
    # Check for reasonable coordinate bounds (e.g., ±1000 meters)
    max_coord = mm(1000000)  # 1000 meters in each direction
    return -max_coord <= coord <= max_coord


def validate_dimensions(width: Coord, height: Coord) -> bool:
    """
    Validate that dimensions are positive and reasonable.

    Args:
        width: Width coordinate
        height: Height coordinate

    Returns:
        bool: True if dimensions are valid
    """
    return (width > 0 and height > 0 and
            validate_coord(width) and validate_coord(height))


