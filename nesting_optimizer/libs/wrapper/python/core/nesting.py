"""
Main nesting functions for 2D bin packing.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable, Union

from .geometry import Item, Box
from .config import NestConfig

# Import the C++ extension
wrapper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cpp/build"))
if wrapper_dir not in sys.path:
    sys.path.insert(0, wrapper_dir)

try:
    import nest2d_wrapper
    _nest_items = nest2d_wrapper.nest_items
    _nest_polygons = nest2d_wrapper.nest_polygons
    _nest_polygons_batch = nest2d_wrapper.nest_polygons_batch
except ImportError as e:
    raise ImportError(f"Failed to import C++ nest2d_wrapper: {e}. "
                     f"Make sure the C++ extension is built in {wrapper_dir}")


def nest_items(items: List[Item],
               bin_box: Box,
               config: Optional[NestConfig] = None,
               progress_callback: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
    """
    Nest a list of items in a bin with full configuration control.

    Args:
        items: List of Item objects to nest
        bin_box: Box representing the bin dimensions
        config: NestConfig with algorithm settings (optional)
        progress_callback: Function called with remaining item count (optional)

    Returns:
        Dictionary with nesting results:
        {
            'items': List of item results with positions, rotations, etc.
            'bins_used': Number of bins used
            'success': Whether nesting was successful
            'total_item_area': Total area of all items
            'total_sheet_area': Total area of all bins used
            'utilization': Utilization percentage
            'placer_used': Which placer algorithm was used
            'bin_width': Bin width
            'bin_height': Bin height
        }

    Examples:
        >>> items = [Item.create_rectangle(10, 5), Item.create_rectangle(8, 6)]
        >>> bin_box = Box(50, 50)
        >>> config = NestConfig.create_balanced()
        >>> result = nest_items(items, bin_box, config)
        >>> print(f"Used {result['bins_used']} bins with {result['utilization']:.1f}% utilization")
    """
    if config is None:
        config = NestConfig.create_balanced()

    # Extract internal objects for C++ call
    internal_items = [item._internal for item in items]
    internal_bin = bin_box._internal
    internal_config = config._internal

    # Call C++ function
    result = _nest_items(internal_items, internal_bin, internal_config, progress_callback)

    # Update the Python items with the results from C++
    for i, item in enumerate(items):
        if i < len(result['items']):
            item_result = result['items'][i]
            item.set_bin_id(item_result['bin_id'])

    return result


def nest_polygons(polygons: List[List[List[float]]],
                 sheet_width: float,
                 sheet_height: float,
                 spacing: float = 0.0,
                 rotations: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Simple polygon nesting function for basic use cases.

    Args:
        polygons: List of polygons (each polygon is list of [x,y] points)
        sheet_width: Width of the sheet/bin in millimeters
        sheet_height: Height of the sheet/bin in millimeters
        spacing: Minimum spacing between pieces in millimeters
        rotations: List of allowed rotation angles in degrees (default: [0, 90, 180, 270])

    Returns:
        Dictionary with nesting results (same format as nest_items)

    Examples:
        >>> # Create some simple shapes
        >>> rect1 = [[0, 0], [10, 0], [10, 5], [0, 5]]
        >>> rect2 = [[0, 0], [8, 0], [8, 6], [0, 6]]
        >>> polygons = [rect1, rect2]
        >>>
        >>> # Nest them on a 50x50mm sheet
        >>> result = nest_polygons(polygons, 50, 50, spacing=1.0)
        >>> print(f"Utilization: {result['utilization']:.1f}%")
    """
    if rotations is None:
        rotations = [0.0, 90.0, 180.0, 270.0]

    return _nest_polygons(polygons, sheet_width, sheet_height, spacing, rotations)


def nest_polygons_batch(polygons: List[List[List[float]]],
                       sheet_width: float,
                       sheet_height: float,
                       batch_size: int = 50,
                       config: Optional[NestConfig] = None) -> Dict[str, Any]:
    """
    Batch process large numbers of polygons to avoid memory issues.

    This function automatically splits large polygon lists into smaller batches
    and processes them separately, which helps avoid memory issues with very
    large nesting jobs.

    Args:
        polygons: List of polygons to nest
        sheet_width: Width of sheets in millimeters
        sheet_height: Height of sheets in millimeters
        batch_size: Number of items per batch (default: 50)
        config: NestConfig for algorithm settings (optional)

    Returns:
        Dictionary with combined nesting results:
        {
            'items': Combined list of all item results
            'bins_used': Total number of bins used
            'success': Whether nesting was successful
            'batch_count': Number of batches processed
            'items_per_batch': Items per batch
            'total_item_area': Total area of all items
            'total_sheet_area': Total area of all bins used
            'utilization': Overall utilization percentage
        }

    Examples:
        >>> # Create a large list of polygons
        >>> polygons = []
        >>> for i in range(200):
        ...     rect = [[0, 0], [5, 0], [5, 3], [0, 3]]
        ...     polygons.append(rect)
        >>>
        >>> # Process in batches of 25
        >>> config = NestConfig.create_fast()  # Use fast config for large batches
        >>> result = nest_polygons_batch(polygons, 100, 100, batch_size=25, config=config)
        >>> print(f"Processed {result['batch_count']} batches, used {result['bins_used']} sheets")
    """
    if config is None:
        config = NestConfig.create_balanced()

    internal_config = config._internal

    return _nest_polygons_batch(polygons, sheet_width, sheet_height, batch_size, internal_config)


def nest_shapes_legacy(shapes: List[List[List[float]]],
               sheet_width: float,
               sheet_height: float,
               spacing: float = 0.0) -> Dict[str, Any]:
    """
    Legacy function name for backward compatibility.

    This is an alias for nest_polygons().
    """
    return nest_polygons(shapes, sheet_width, sheet_height, spacing)
