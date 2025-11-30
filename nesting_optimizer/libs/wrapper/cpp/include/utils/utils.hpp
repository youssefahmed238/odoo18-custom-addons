#ifndef NEST2D_UTILS_HPP
#define NEST2D_UTILS_HPP

#include "../core/types.hpp"
#include <pybind11/pybind11.h>
#include <vector>

namespace py = pybind11;

namespace nest2d_wrapper {

// ============================================================================
// COMPREHENSIVE GEOMETRY UTILITY FUNCTIONS - 100% Backend Coverage
// ============================================================================

// Basic polygon operations
double polygon_area(const std::vector<std::vector<double>>& points);
py::dict polygon_bounds(const std::vector<std::vector<double>>& points);
bool point_in_polygon(const std::vector<std::vector<double>>& polygon_points, double x, double y);
py::list polygon_centroid(const std::vector<std::vector<double>>& points);
bool polygon_is_convex(const std::vector<std::vector<double>>& points);
std::vector<std::vector<double>> polygon_rotate(const std::vector<std::vector<double>>& points, double angle_degrees);
std::vector<std::vector<double>> polygon_translate(const std::vector<std::vector<double>>& points, double dx, double dy);
std::vector<std::vector<double>> polygon_offset(const std::vector<std::vector<double>>& points, double distance);

// Advanced Clipper backend operations
std::vector<std::vector<std::vector<double>>> polygon_union(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

std::vector<std::vector<std::vector<double>>> polygon_intersection(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

std::vector<std::vector<std::vector<double>>> polygon_difference(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

std::vector<std::vector<std::vector<double>>> polygon_xor(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

// Minkowski operations
std::vector<std::vector<double>> minkowski_sum(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

std::vector<std::vector<double>> minkowski_difference(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

// No-Fit Polygon calculation
std::vector<std::vector<double>> calculate_nfp(
    const std::vector<std::vector<double>>& stationary,
    const std::vector<std::vector<double>>& moving);

std::vector<std::vector<double>> calculate_ifp(
    const std::vector<std::vector<double>>& container,
    const std::vector<std::vector<double>>& item);

// MultiPolygon support (polygons with holes)
py::dict create_multipolygon(
    const std::vector<std::vector<double>>& outer_contour,
    const std::vector<std::vector<std::vector<double>>>& holes = {});

double multipolygon_area(const py::dict& multipolygon);
py::dict multipolygon_bounds(const py::dict& multipolygon);
bool point_in_multipolygon(const py::dict& multipolygon, double x, double y);

// Validation and correction utilities
bool polygon_is_valid(const std::vector<std::vector<double>>& points);
std::vector<std::vector<double>> polygon_fix_orientation(const std::vector<std::vector<double>>& points, bool clockwise = false);
std::vector<std::vector<double>> polygon_simplify(const std::vector<std::vector<double>>& points, double tolerance = 0.1);
std::vector<std::vector<double>> polygon_clean(const std::vector<std::vector<double>>& points);

// Geometric analysis
double polygon_perimeter(const std::vector<std::vector<double>>& points);
py::list polygon_convex_hull(const std::vector<std::vector<double>>& points);
double polygon_orientation_area(const std::vector<std::vector<double>>& points); // Signed area
bool polygon_is_clockwise(const std::vector<std::vector<double>>& points);
py::dict polygon_fit_rectangle(const std::vector<std::vector<double>>& points); // Minimum bounding rectangle

// Distance and proximity operations
double polygon_distance(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

bool polygons_intersect(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

bool polygons_touch(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

// Shape decomposition
std::vector<std::vector<std::vector<double>>> polygon_decompose_convex(
    const std::vector<std::vector<double>>& points);

std::vector<py::dict> polygon_triangulate(
    const std::vector<std::vector<double>>& points);

// Coordinate conversion utilities
py::list mm_to_coords(const std::vector<std::vector<double>>& points_mm);
py::list coords_to_mm(const py::list& coords);

// Shape matching and similarity
double polygon_similarity(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

double polygon_overlap_area(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2);

// Optimization utilities
py::dict optimize_polygon_for_nesting(const std::vector<std::vector<double>>& points);
std::vector<std::vector<double>> generate_circle_approximation(double radius, int segments);
std::vector<std::vector<double>> generate_regular_polygon(double radius, int sides);

// Debug and visualization utilities
std::string polygon_to_svg(const std::vector<std::vector<double>>& points, int width = 400, int height = 400);
std::string shapes_to_svg(const std::vector<std::vector<std::vector<double>>>& shapes, int width = 400, int height = 400);
py::dict polygon_statistics(const std::vector<std::vector<double>>& points);

// ============================================================================
// ADVANCED UTILITIES - Previously Missing Features
// ============================================================================

// Rotating calipers algorithms
py::dict minimum_bounding_box_rotated(const std::vector<std::vector<double>>& points);
py::dict minimum_perimeter_bounding_box(const std::vector<std::vector<double>>& points);
double polygon_diameter(const std::vector<std::vector<double>>& points);
double polygon_width_in_direction(const std::vector<std::vector<double>>& points, double angle_degrees);

// Advanced NFP utilities
py::dict calculate_nfp_quality_metrics(const std::vector<std::vector<double>>& stationary,
                                      const std::vector<std::vector<double>>& moving,
                                      const std::vector<std::vector<double>>& nfp);

py::list calculate_all_nfp_positions(const std::vector<std::vector<double>>& stationary,
                                    const std::vector<std::vector<double>>& moving);

// Edge cache functionality
py::dict create_edge_cache(const std::vector<std::vector<double>>& polygon, double accuracy = 1.0);
py::list sample_polygon_boundary(const std::vector<std::vector<double>>& polygon, int num_samples);
std::vector<double> point_on_boundary_at_parameter(const std::vector<std::vector<double>>& polygon, double t);

// High precision geometry
double high_precision_area(const std::vector<std::vector<double>>& points);
bool robust_point_in_polygon(const std::vector<std::vector<double>>& polygon, double x, double y, double tolerance = 1e-12);
py::dict robust_polygon_intersection(const std::vector<std::vector<double>>& poly1,
                                    const std::vector<std::vector<double>>& poly2,
                                    double tolerance = 1e-12);

// Boost geometry integration (if available)
#ifdef LIBNEST2D_BOOST_GEOMETRY
std::vector<std::vector<double>> boost_convex_hull(const std::vector<std::vector<double>>& points);
double boost_hausdorff_distance(const std::vector<std::vector<double>>& shape1,
                               const std::vector<std::vector<double>>& shape2);
py::dict boost_polygon_set_operations(const std::vector<std::vector<double>>& poly1,
                                     const std::vector<std::vector<double>>& poly2,
                                     const std::string& operation);
#endif

// Rational arithmetic utilities (if available)
#ifdef LIBNEST2D_RATIONAL_ARITHMETIC
std::string double_to_rational_string(double value, int max_denominator = 1000000);
py::dict exact_polygon_area(const std::vector<std::vector<double>>& points);
bool exact_point_equality(const std::vector<double>& p1, const std::vector<double>& p2, const std::string& tolerance = "0");
#endif

// BigInt support for very large coordinates (if available)
#ifdef LIBNEST2D_BIGINT_SUPPORT
std::string convert_to_bigint_coordinates(const std::vector<std::vector<double>>& points);
std::vector<std::vector<double>> convert_from_bigint_coordinates(const std::string& bigint_coords);
#endif

// Advanced shape analysis
py::dict analyze_shape_complexity_advanced(const std::vector<std::vector<double>>& points);
std::vector<int> find_shape_features(const std::vector<std::vector<double>>& points, const std::string& feature_type);
py::dict calculate_shape_moments_advanced(const std::vector<std::vector<double>>& points);
std::vector<double> generate_shape_descriptor(const std::vector<std::vector<double>>& points, int descriptor_length = 64);

// Parallel processing utilities
py::list parallel_polygon_operations(const std::vector<std::vector<std::vector<double>>>& polygons,
                                    const std::string& operation,
                                    int num_threads = -1);

py::dict parallel_nfp_calculation(const std::vector<std::vector<std::vector<double>>>& stationary_shapes,
                                 const std::vector<std::vector<std::vector<double>>>& moving_shapes,
                                 int num_threads = -1);

// Optimization utilities
py::dict optimize_polygon_for_nesting_advanced(const std::vector<std::vector<double>>& points,
                                              const std::string& optimization_goal = "area");

std::vector<double> find_optimal_rotation_angles(const std::vector<std::vector<double>>& points,
                                                double angle_resolution = 15.0,
                                                const std::string& optimization_criterion = "bounding_box");

// Memory and performance utilities
py::dict estimate_memory_usage(const std::vector<std::vector<std::vector<double>>>& shapes,
                              const std::string& algorithm = "nfp");

py::dict performance_profile_operation(py::function operation, const py::args& args);

// Coordinate system utilities
py::dict convert_coordinate_system(const std::vector<std::vector<double>>& points,
                                  const std::string& from_system,
                                  const std::string& to_system,
                                  const py::dict& parameters = py::dict());

std::vector<std::vector<double>> apply_coordinate_transformation(const std::vector<std::vector<double>>& points,
                                                               const std::vector<std::vector<double>>& transformation_matrix);

// Quality assessment utilities
py::dict assess_nesting_quality_detailed(const py::dict& nesting_result,
                                        const std::vector<std::vector<double>>& sheet_bounds);

std::vector<py::dict> detect_nesting_issues(const py::dict& nesting_result,
                                           double min_distance = 1.0,
                                           double min_feature_size = 0.5);

// Experimental algorithms
py::dict experimental_shape_matching(const std::vector<std::vector<double>>& pattern,
                                    const std::vector<std::vector<std::vector<double>>>& candidates,
                                    const std::string& matching_algorithm = "hausdorff");

py::list experimental_polygon_decomposition(const std::vector<std::vector<double>>& points,
                                           const std::string& decomposition_type = "convex");

// Error and validation utilities
py::dict validate_polygon_advanced(const std::vector<std::vector<double>>& points);
py::dict fix_polygon_issues(const std::vector<std::vector<double>>& points,
                           const py::list& issues_to_fix);

// Export and import utilities
std::string export_to_dxf(const std::vector<std::vector<std::vector<double>>>& shapes);
std::string export_to_svg_advanced(const std::vector<std::vector<std::vector<double>>>& shapes,
                                   const py::dict& styling_options = py::dict());

py::dict export_nesting_report(const py::dict& nesting_result,
                              const std::string& format = "json");

} // namespace nest2d_wrapper

#endif // NEST2D_UTILS_HPP
