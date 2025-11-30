#ifndef NEST2D_TYPES_HPP
#define NEST2D_TYPES_HPP

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
// Conditional includes for libnest2d
#ifdef LIBNEST2D_AVAILABLE
#include <libnest2d/libnest2d.hpp>
#include <libnest2d/placers/nfpplacer.hpp>
#include <libnest2d/placers/bottomleftplacer.hpp>
#endif
#include <functional>

namespace py = pybind11;
namespace nest2d_wrapper {

#ifdef LIBNEST2D_AVAILABLE
// Type aliases for easier naming - use explicit libnest2d types to avoid conflicts
using Polygon = libnest2d::PolygonImpl;
using Coord = libnest2d::TCoord<libnest2d::PointImpl>;
using LibNest2DPoint = libnest2d::PointImpl;
using LibNest2DBox = libnest2d::Box;
using LibNest2DItem = libnest2d::Item;
using LibNest2DRectangle = libnest2d::Rectangle;
using LibNest2DCircle = libnest2d::Circle;
#else
// Fallback types when libnest2d is not available
using Polygon = std::vector<std::pair<double, double>>;
using Coord = double;
#endif
using LibNest2DSegment = libnest2d::Segment;
using LibNest2DMultiPolygon = libnest2d::MultiPolygon;
using LibNest2DPackGroup = libnest2d::PackGroup;

// Placer types
using LibNest2DNfpPlacer = libnest2d::NfpPlacer;
using LibNest2DBottomLeftPlacer = libnest2d::BottomLeftPlacer;

// Selection types
using LibNest2DFirstFitSelection = libnest2d::FirstFitSelection;
using LibNest2DFillerSelection = libnest2d::FillerSelection;
using LibNest2DDJDHeuristic = libnest2d::DJDHeuristic;

// Configuration types
template<class Placer, class Selector>
using LibNest2DNestConfig = libnest2d::NestConfig<Placer, Selector>;
using LibNest2DNestControl = libnest2d::NestControl;
using LibNest2DProgressFunction = libnest2d::ProgressFunction;
using LibNest2DStopCondition = libnest2d::StopCondition;

// Placer configuration types
using NfpPlacerConfig = libnest2d::placers::NfpPConfig<libnest2d::PolygonImpl>;
using BottomLeftPlacerConfig = int; // BottomLeft placer uses int as config

// Conversion constants
static constexpr double COORD_SCALE = 1000000.0; // 1mm = 1000000 units

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Convert millimeters to internal coordinate units
 */
inline Coord mm_to_coord(double mm) {
    return static_cast<Coord>(mm * COORD_SCALE);
}

/**
 * Convert internal coordinate units to millimeters
 */
inline double coord_to_mm(Coord coord) {
    return static_cast<double>(coord) / COORD_SCALE;
}

/**
 * Convert degrees to radians
 */
libnest2d::Radians degrees_to_radians(double degrees);

/**
 * Convert radians to degrees
 */
double radians_to_degrees(const libnest2d::Radians& radians);

/**
 * Create a polygon from a list of 2D points
 */
Polygon create_polygon(const std::vector<std::vector<double>>& points);

/**
 * Convert polygon back to list of points
 */
std::vector<std::vector<double>> polygon_to_points(const Polygon& polygon);

} // namespace nest2d_wrapper

#endif // NEST2D_TYPES_HPP
