#ifndef NEST2D_ADVANCED_GEOMETRY_HPP
#define NEST2D_ADVANCED_GEOMETRY_HPP

#include "types.hpp"
#include <pybind11/pybind11.h>
#include <libnest2d/utils/rotcalipers.hpp>
#include <libnest2d/utils/rotfinder.hpp>
#include <vector>
#include <cmath>

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Advanced geometric utilities using LibNest2D's internal algorithms
 */
class AdvancedGeometry {
public:
    /**
     * Rotating calipers for minimum bounding box
     */
    struct RotatedBoundingBox {
        double width;
        double height;
        double area;
        double angle_degrees; // Rotation angle in degrees
        std::vector<std::vector<double>> corners; // 4 corner points
        std::vector<double> center; // Center point

        py::dict to_dict() const {
            py::dict result;
            result["width"] = width;
            result["height"] = height;
            result["area"] = area;
            result["angle_degrees"] = angle_degrees;
            result["corners"] = corners;
            result["center"] = center;
            return result;
        }
    };

    /**
     * Calculate minimum area bounding box using rotating calipers
     */
    static RotatedBoundingBox minimum_bounding_box(const std::vector<std::vector<double>>& points);

    /**
     * Calculate minimum perimeter bounding box
     */
    static RotatedBoundingBox minimum_perimeter_bounding_box(const std::vector<std::vector<double>>& points);

    /**
     * Calculate convex hull using LibNest2D algorithms
     */
    static std::vector<std::vector<double>> convex_hull(const std::vector<std::vector<double>>& points);

    /**
     * Remove collinear points from polygon
     */
    static std::vector<std::vector<double>> remove_collinear_points(
        const std::vector<std::vector<double>>& points, double epsilon = 1e-9);

    /**
     * Calculate polygon diameter (maximum distance between any two points)
     */
    static double polygon_diameter(const std::vector<std::vector<double>>& points);

    /**
     * Calculate polygon width in a specific direction
     */
    static double polygon_width_in_direction(const std::vector<std::vector<double>>& points, double angle_degrees);

    /**
     * Find all optimal rotation angles for a polygon
     */
    static std::vector<double> find_optimal_rotations(const std::vector<std::vector<double>>& points,
                                                     double angle_resolution = 1.0);

    /**
     * Fit a polygon to a rectangle with specific aspect ratio
     */
    static py::dict fit_to_rectangle(const std::vector<std::vector<double>>& points,
                                    double target_width, double target_height);

    /**
     * Calculate shape similarity using various metrics
     */
    static double hausdorff_distance(const std::vector<std::vector<double>>& shape1,
                                    const std::vector<std::vector<double>>& shape2);

    /**
     * Calculate Frechet distance between two polygons
     */
    static double frechet_distance(const std::vector<std::vector<double>>& shape1,
                                  const std::vector<std::vector<double>>& shape2);
};

/**
 * Edge cache for fast point-on-boundary queries
 */
class EdgeCache {
private:
    struct EdgeInfo {
        std::vector<double> start_point;
        std::vector<double> end_point;
        double length;
        double cumulative_length;
    };

    std::vector<EdgeInfo> edges_;
    double total_perimeter_;
    mutable std::vector<double> corner_cache_;
    mutable bool corner_cache_valid_ = false;

public:
    explicit EdgeCache(const std::vector<std::vector<double>>& polygon);

    /**
     * Get a point on the polygon boundary at parameter t [0,1]
     * t=0 gives first vertex, t=1 gives last vertex (same as first)
     */
    std::vector<double> point_at_parameter(double t) const;

    /**
     * Get multiple points distributed along the boundary
     */
    std::vector<std::vector<double>> sample_points(int count) const;

    /**
     * Get points at corners (vertices) optimized for access
     */
    const std::vector<double>& get_corner_points() const;

    /**
     * Find parameter value for closest point on boundary to given point
     */
    double find_closest_parameter(const std::vector<double>& point) const;

    /**
     * Get total perimeter
     */
    double get_perimeter() const { return total_perimeter_; }

    /**
     * Get edge information
     */
    py::list get_edges_info() const;
};

/**
 * No-fit polygon calculation utilities
 */
class NFPCalculator {
public:
    /**
     * Calculate detailed NFP with additional information
     */
    static py::dict calculate_detailed_nfp(const std::vector<std::vector<double>>& stationary,
                                          const std::vector<std::vector<double>>& moving);

    /**
     * Calculate multiple NFPs for different orientations
     */
    static py::list calculate_nfp_orientations(const std::vector<std::vector<double>>& stationary,
                                              const std::vector<std::vector<double>>& moving,
                                              const std::vector<double>& angles);

    /**
     * Calculate Inner-fit Polygon (IFP) for container and item
     */
    static py::dict calculate_detailed_ifp(const std::vector<std::vector<double>>& container,
                                          const std::vector<std::vector<double>>& item);

    /**
     * Validate NFP calculation and return quality metrics
     */
    static py::dict validate_nfp(const std::vector<std::vector<double>>& stationary,
                                 const std::vector<std::vector<double>>& moving,
                                 const std::vector<std::vector<double>>& nfp);

    /**
     * Find all touching positions between two polygons
     */
    static std::vector<std::vector<double>> find_touching_positions(
        const std::vector<std::vector<double>>& stationary,
        const std::vector<std::vector<double>>& moving);
};

/**
 * Precision arithmetic utilities for high-precision calculations
 */
class PrecisionUtils {
public:
    /**
     * Check if two points are equal within tolerance
     */
    static bool points_equal(const std::vector<double>& p1,
                           const std::vector<double>& p2,
                           double tolerance = 1e-9);

    /**
     * Calculate area with high precision
     */
    static double high_precision_area(const std::vector<std::vector<double>>& points);

    /**
     * Clean polygon by removing degenerate elements
     */
    static std::vector<std::vector<double>> clean_polygon_precision(
        const std::vector<std::vector<double>>& points, double tolerance = 1e-9);

    /**
     * Snap polygon to grid for better numerical stability
     */
    static std::vector<std::vector<double>> snap_to_grid(
        const std::vector<std::vector<double>>& points, double grid_size = 0.001);

    /**
     * Calculate signed area (positive for CCW, negative for CW)
     */
    static double signed_area(const std::vector<std::vector<double>>& points);

    /**
     * Robust orientation test for three points
     */
    enum class Orientation { CLOCKWISE, COUNTERCLOCKWISE, COLLINEAR };
    static Orientation point_orientation(const std::vector<double>& p,
                                        const std::vector<double>& q,
                                        const std::vector<double>& r);
};

/**
 * Shape analysis and decomposition utilities
 */
class ShapeAnalysis {
public:
    /**
     * Analyze shape complexity and characteristics
     */
    static py::dict analyze_shape_complexity(const std::vector<std::vector<double>>& points);

    /**
     * Find bottleneck features in a shape
     */
    static py::list find_bottlenecks(const std::vector<std::vector<double>>& points,
                                    double threshold_ratio = 0.5);

    /**
     * Decompose shape into simpler convex parts
     */
    static std::vector<std::vector<std::vector<double>>> decompose_to_convex(
        const std::vector<std::vector<double>>& points);

    /**
     * Find natural break points for shape subdivision
     */
    static std::vector<int> find_subdivision_points(const std::vector<std::vector<double>>& points,
                                                   int max_subdivisions = 4);

    /**
     * Calculate shape moments for pattern recognition
     */
    static py::dict calculate_moments(const std::vector<std::vector<double>>& points);

    /**
     * Generate shape signature for matching
     */
    static std::vector<double> generate_shape_signature(const std::vector<std::vector<double>>& points,
                                                       int signature_length = 64);
};

} // namespace nest2d_wrapper

#endif // NEST2D_ADVANCED_GEOMETRY_HPP
