"""
Configuration classes for nesting algorithms.
"""

import os
import sys
from typing import List, Optional, Callable, Union

# Import the C++ extension
wrapper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cpp/build"))
if wrapper_dir not in sys.path:
    sys.path.insert(0, wrapper_dir)

try:
    import nest2d_wrapper
    _NestConfig = nest2d_wrapper.NestConfig
except ImportError as e:
    raise ImportError(f"Failed to import C++ nest2d_wrapper: {e}. "
                     f"Make sure the C++ extension is built in {wrapper_dir}")


class NestConfig:
    """
    Configuration for nesting algorithms.

    Examples:
        >>> config = NestConfig()
        >>> config.placer_type = "nfp"
        >>> config.rotations = [0, 90, 180, 270]
        >>> config.spacing = 2.0
    """

    def __init__(self):
        """Create default nesting configuration."""
        self._internal = _NestConfig()

    # Placer settings
    @property
    def placer_type(self) -> str:
        """
        Placer algorithm type.

        Options:
            - "nfp": No-Fit Polygon placer (recommended, most accurate)
            - "bottom_left": Bottom-left placer (faster, simpler)
        """
        return self._internal.placer_type

    @placer_type.setter
    def placer_type(self, value: str):
        if value not in ["nfp", "bottom_left"]:
            raise ValueError("placer_type must be 'nfp' or 'bottom_left'")
        self._internal.placer_type = value

    @property
    def rotations(self) -> List[float]:
        """List of allowed rotation angles in degrees."""
        return self._internal.rotations

    @rotations.setter
    def rotations(self, value: List[float]):
        self._internal.rotations = value

    @property
    def alignment(self) -> str:
        """
        Result alignment for packed items.

        Options: "bottom_left", "center", "bottom_right", "top_left", "top_right"
        """
        return self._internal.alignment

    @alignment.setter
    def alignment(self, value: str):
        valid_alignments = ["bottom_left", "center", "bottom_right", "top_left", "top_right"]
        if value not in valid_alignments:
            raise ValueError(f"alignment must be one of {valid_alignments}")
        self._internal.alignment = value

    @property
    def starting_point(self) -> str:
        """Starting placement point (same options as alignment)."""
        return self._internal.starting_point

    @starting_point.setter
    def starting_point(self, value: str):
        valid_points = ["bottom_left", "center", "bottom_right", "top_left", "top_right"]
        if value not in valid_points:
            raise ValueError(f"starting_point must be one of {valid_points}")
        self._internal.starting_point = value

    @property
    def accuracy(self) -> float:
        """
        Quality vs speed trade-off (0.0 to 1.0).

        - 0.0: Fastest but lowest quality
        - 1.0: Slowest but highest quality
        - 0.65: Good balance (default)
        """
        return self._internal.accuracy

    @accuracy.setter
    def accuracy(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError("accuracy must be between 0.0 and 1.0")
        self._internal.accuracy = value

    @property
    def explore_holes(self) -> bool:
        """Whether to place items inside holes of other items."""
        return self._internal.explore_holes

    @explore_holes.setter
    def explore_holes(self, value: bool):
        self._internal.explore_holes = value

    @property
    def parallel(self) -> bool:
        """Whether to use parallel processing."""
        return self._internal.parallel

    @parallel.setter
    def parallel(self, value: bool):
        self._internal.parallel = value

    # Selector settings
    @property
    def selector_type(self) -> str:
        """
        Selection strategy for bin assignment.

        Options:
            - "firstfit": Place in first bin that fits
            - "filler": Fill bins optimally
            - "djd": Dynamic Johnson-Dekkers heuristic
        """
        return self._internal.selector_type

    @selector_type.setter
    def selector_type(self, value: str):
        valid_selectors = ["firstfit", "filler", "djd"]
        if value not in valid_selectors:
            raise ValueError(f"selector_type must be one of {valid_selectors}")
        self._internal.selector_type = value

    # General settings
    @property
    def spacing(self) -> float:
        """Minimum spacing between items in millimeters."""
        return self._internal.spacing

    @spacing.setter
    def spacing(self, value: float):
        if value < 0:
            raise ValueError("spacing must be non-negative")
        self._internal.spacing = value

    def __str__(self) -> str:
        return self._internal.__str__()

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def create_fast(cls) -> 'NestConfig':
        """Create configuration optimized for speed."""
        config = cls()
        config.placer_type = "bottom_left"
        config.accuracy = 0.3
        config.parallel = True
        config.rotations = [0.0]  # No rotation for speed
        return config

    @classmethod
    def create_quality(cls) -> 'NestConfig':
        """Create configuration optimized for quality."""
        config = cls()
        config.placer_type = "nfp"
        config.accuracy = 0.9
        config.parallel = True
        config.explore_holes = True
        config.rotations = [0.0, 90.0, 180.0, 270.0]
        return config

    @classmethod
    def create_balanced(cls) -> 'NestConfig':
        """Create balanced configuration (default)."""
        config = cls()
        config.placer_type = "nfp"
        config.accuracy = 0.65
        config.parallel = True
        config.rotations = [0.0, 90.0, 180.0, 270.0]
        return config
