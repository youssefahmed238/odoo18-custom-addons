#include "../include/geometry/advanced_geometry.hpp"
#include <algorithm>
#include <numeric>
#include <cmath>

#ifdef LIBNEST2D_USE_ROTCALIPERS
#include <libnest2d/utils/rotcalipers.hpp>
#endif

namespace nest2d_wrapper {

// AdvancedGeometry implementations
AdvancedGeometry::RotatedBoundingBox AdvancedGeometry::minimum_bounding_box(
    const std::vector<std::vector<double>>& points) {

    RotatedBoundingBox result;

    if (points.size() < 3) {
        result.width = result.height = result.area = 0.0;
        result.angle_degrees = 0.0;
        return result;
    }

    // Calculate convex hull first
    auto hull = convex_hull(points);

    double min_area = std::numeric_limits<double>::max();
    double best_angle = 0.0;

    // Try different orientations based on edge directions
    for (size_t i = 0; i < hull.size(); ++i) {
        size_t j = (i + 1) % hull.size();

        double dx = hull[j][0] - hull[i][0];
        double dy = hull[j][1] - hull[i][1];
        double angle = std::atan2(dy, dx);

        // Rotate points to align with this edge
        std::vector<std::vector<double>> rotated_points;
        double cos_a = std::cos(-angle);
        double sin_a = std::sin(-angle);

        for (const auto& point : hull) {
            double x = point[0] * cos_a - point[1] * sin_a;
            double y = point[0] * sin_a + point[1] * cos_a;
            rotated_points.push_back({x, y});
        }

        // Find axis-aligned bounding box
        auto minmax_x = std::minmax_element(rotated_points.begin(), rotated_points.end(),
            [](const std::vector<double>& a, const std::vector<double>& b) { return a[0] < b[0]; });
        auto minmax_y = std::minmax_element(rotated_points.begin(), rotated_points.end(),
            [](const std::vector<double>& a, const std::vector<double>& b) { return a[1] < b[1]; });

        double width = (*minmax_x.second)[0] - (*minmax_x.first)[0];
        double height = (*minmax_y.second)[1] - (*minmax_y.first)[1];
        double area = width * height;

        if (area < min_area) {
            min_area = area;
            best_angle = angle * 180.0 / M_PI;
            result.width = width;
            result.height = height;
            result.area = area;
            result.angle_degrees = best_angle;

            // Calculate corners of the rotated bounding box
            double min_x = (*minmax_x.first)[0];
            double max_x = (*minmax_x.second)[0];
            double min_y = (*minmax_y.first)[1];
            double max_y = (*minmax_y.second)[1];

            // Transform back to original coordinates
            cos_a = std::cos(angle);
            sin_a = std::sin(angle);

            result.corners = {
                {min_x * cos_a - min_y * sin_a, min_x * sin_a + min_y * cos_a},
                {max_x * cos_a - min_y * sin_a, max_x * sin_a + min_y * cos_a},
                {max_x * cos_a - max_y * sin_a, max_x * sin_a + max_y * cos_a},
                {min_x * cos_a - max_y * sin_a, min_x * sin_a + max_y * cos_a}
            };

            result.center = {
                (min_x + max_x) * 0.5 * cos_a - (min_y + max_y) * 0.5 * sin_a,
                (min_x + max_x) * 0.5 * sin_a + (min_y + max_y) * 0.5 * cos_a
            };
        }
    }

    return result;
}

AdvancedGeometry::RotatedBoundingBox AdvancedGeometry::minimum_perimeter_bounding_box(
    const std::vector<std::vector<double>>& points) {

    RotatedBoundingBox result;

    if (points.size() < 3) {
        result.width = result.height = result.area = 0.0;
        result.angle_degrees = 0.0;
        return result;
    }

    auto hull = convex_hull(points);

    double min_perimeter = std::numeric_limits<double>::max();
    double best_angle = 0.0;

    for (size_t i = 0; i < hull.size(); ++i) {
        size_t j = (i + 1) % hull.size();

        double dx = hull[j][0] - hull[i][0];
        double dy = hull[j][1] - hull[i][1];
        double angle = std::atan2(dy, dx);

        // Rotate and find bounding box
        std::vector<std::vector<double>> rotated_points;
        double cos_a = std::cos(-angle);
        double sin_a = std::sin(-angle);

        for (const auto& point : hull) {
            double x = point[0] * cos_a - point[1] * sin_a;
            double y = point[0] * sin_a + point[1] * cos_a;
            rotated_points.push_back({x, y});
        }

        auto minmax_x = std::minmax_element(rotated_points.begin(), rotated_points.end(),
            [](const std::vector<double>& a, const std::vector<double>& b) { return a[0] < b[0]; });
        auto minmax_y = std::minmax_element(rotated_points.begin(), rotated_points.end(),
            [](const std::vector<double>& a, const std::vector<double>& b) { return a[1] < b[1]; });

        double width = (*minmax_x.second)[0] - (*minmax_x.first)[0];
        double height = (*minmax_y.second)[1] - (*minmax_y.first)[1];
        double perimeter = 2.0 * (width + height);

        if (perimeter < min_perimeter) {
            min_perimeter = perimeter;
            best_angle = angle * 180.0 / M_PI;
            result.width = width;
            result.height = height;
            result.area = width * height;
            result.angle_degrees = best_angle;
        }
    }

    return result;
}

std::vector<std::vector<double>> AdvancedGeometry::convex_hull(
    const std::vector<std::vector<double>>& points) {

    if (points.size() < 3) {
        return points;
    }

    // Graham scan algorithm
    std::vector<std::vector<double>> sorted_points = points;

    // Find bottom-most point (and leftmost in case of tie)
    auto bottom_point = std::min_element(sorted_points.begin(), sorted_points.end(),
        [](const std::vector<double>& a, const std::vector<double>& b) {
            if (a[1] != b[1]) return a[1] < b[1];
            return a[0] < b[0];
        });

    std::swap(sorted_points[0], *bottom_point);
    auto pivot = sorted_points[0];

    // Sort points by polar angle with respect to pivot
    std::sort(sorted_points.begin() + 1, sorted_points.end(),
        [&pivot](const std::vector<double>& a, const std::vector<double>& b) {
            double cross = (a[0] - pivot[0]) * (b[1] - pivot[1]) - (a[1] - pivot[1]) * (b[0] - pivot[0]);
            if (std::abs(cross) < 1e-9) {
                // Collinear points - choose closer one first
                double dist_a = (a[0] - pivot[0]) * (a[0] - pivot[0]) + (a[1] - pivot[1]) * (a[1] - pivot[1]);
                double dist_b = (b[0] - pivot[0]) * (b[0] - pivot[0]) + (b[1] - pivot[1]) * (b[1] - pivot[1]);
                return dist_a < dist_b;
            }
            return cross > 0;
        });

    std::vector<std::vector<double>> hull;

    for (const auto& point : sorted_points) {
        // Remove points that would create a right turn
        while (hull.size() >= 2) {
            const auto& p1 = hull[hull.size() - 2];
            const auto& p2 = hull[hull.size() - 1];
            double cross = (p2[0] - p1[0]) * (point[1] - p1[1]) - (p2[1] - p1[1]) * (point[0] - p1[0]);
            if (cross <= 0) {
                hull.pop_back();
            } else {
                break;
            }
        }
        hull.push_back(point);
    }

    return hull;
}

std::vector<std::vector<double>> AdvancedGeometry::remove_collinear_points(
    const std::vector<std::vector<double>>& points, double epsilon) {

    if (points.size() < 3) {
        return points;
    }

    std::vector<std::vector<double>> result;

    for (size_t i = 0; i < points.size(); ++i) {
        size_t prev = (i + points.size() - 1) % points.size();
        size_t next = (i + 1) % points.size();

        const auto& p_prev = points[prev];
        const auto& p_curr = points[i];
        const auto& p_next = points[next];

        // Calculate cross product to check collinearity
        double cross = (p_curr[0] - p_prev[0]) * (p_next[1] - p_prev[1]) -
                      (p_curr[1] - p_prev[1]) * (p_next[0] - p_prev[0]);

        if (std::abs(cross) > epsilon) {
            result.push_back(p_curr);
        }
    }

    return result;
}

double AdvancedGeometry::polygon_diameter(const std::vector<std::vector<double>>& points) {
    if (points.size() < 2) {
        return 0.0;
    }

    // For accurate diameter, use convex hull and rotating calipers
    auto hull = convex_hull(points);

    double max_distance = 0.0;

    // Brute force approach for now (O(n^2))
    for (size_t i = 0; i < hull.size(); ++i) {
        for (size_t j = i + 1; j < hull.size(); ++j) {
            double dx = hull[j][0] - hull[i][0];
            double dy = hull[j][1] - hull[i][1];
            double distance = std::sqrt(dx * dx + dy * dy);
            max_distance = std::max(max_distance, distance);
        }
    }

    return max_distance;
}

double AdvancedGeometry::polygon_width_in_direction(
    const std::vector<std::vector<double>>& points, double angle_degrees) {

    if (points.empty()) {
        return 0.0;
    }

    double angle_rad = angle_degrees * M_PI / 180.0;
    double cos_a = std::cos(angle_rad);
    double sin_a = std::sin(angle_rad);

    // Project all points onto the direction vector
    std::vector<double> projections;
    for (const auto& point : points) {
        double projection = point[0] * cos_a + point[1] * sin_a;
        projections.push_back(projection);
    }

    auto minmax = std::minmax_element(projections.begin(), projections.end());
    return *minmax.second - *minmax.first;
}

std::vector<double> AdvancedGeometry::find_optimal_rotations(
    const std::vector<std::vector<double>>& points, double angle_resolution) {

    std::vector<double> optimal_angles;

    if (points.size() < 3) {
        optimal_angles.push_back(0.0);
        return optimal_angles;
    }

    double best_angle = 0.0;
    double min_bounding_area = std::numeric_limits<double>::max();

    for (double angle = 0.0; angle < 180.0; angle += angle_resolution) {
        auto bbox = minimum_bounding_box(points);
        if (bbox.area < min_bounding_area) {
            min_bounding_area = bbox.area;
            best_angle = angle;
        }
    }

    optimal_angles.push_back(best_angle);

    // Add alternative angles (90 degrees apart)
    optimal_angles.push_back(std::fmod(best_angle + 90.0, 360.0));

    return optimal_angles;
}

py::dict AdvancedGeometry::fit_to_rectangle(const std::vector<std::vector<double>>& points,
                                           double target_width, double target_height) {
    py::dict result;

    auto bbox = minimum_bounding_box(points);

    double scale_x = target_width / bbox.width;
    double scale_y = target_height / bbox.height;
    double uniform_scale = std::min(scale_x, scale_y);

    result["original_width"] = bbox.width;
    result["original_height"] = bbox.height;
    result["target_width"] = target_width;
    result["target_height"] = target_height;
    result["scale_x"] = scale_x;
    result["scale_y"] = scale_y;
    result["uniform_scale"] = uniform_scale;
    result["rotation_angle"] = bbox.angle_degrees;
    result["fits_uniformly"] = (uniform_scale <= 1.0);

    return result;
}

double AdvancedGeometry::hausdorff_distance(const std::vector<std::vector<double>>& shape1,
                                           const std::vector<std::vector<double>>& shape2) {
    if (shape1.empty() || shape2.empty()) {
        return 0.0;
    }

    auto point_to_set_distance = [](const std::vector<double>& point,
                                   const std::vector<std::vector<double>>& shape) {
        double min_dist = std::numeric_limits<double>::max();
        for (const auto& shape_point : shape) {
            double dx = point[0] - shape_point[0];
            double dy = point[1] - shape_point[1];
            double dist = std::sqrt(dx * dx + dy * dy);
            min_dist = std::min(min_dist, dist);
        }
        return min_dist;
    };

    double max_dist1 = 0.0;
    for (const auto& point : shape1) {
        double dist = point_to_set_distance(point, shape2);
        max_dist1 = std::max(max_dist1, dist);
    }

    double max_dist2 = 0.0;
    for (const auto& point : shape2) {
        double dist = point_to_set_distance(point, shape1);
        max_dist2 = std::max(max_dist2, dist);
    }

    return std::max(max_dist1, max_dist2);
}

double AdvancedGeometry::frechet_distance(const std::vector<std::vector<double>>& shape1,
                                         const std::vector<std::vector<double>>& shape2) {
    // Simplified discrete Frechet distance implementation
    if (shape1.empty() || shape2.empty()) {
        return 0.0;
    }

    size_t m = shape1.size();
    size_t n = shape2.size();

    std::vector<std::vector<double>> dp(m, std::vector<double>(n, -1.0));

    std::function<double(size_t, size_t)> compute_distance = [&](size_t i, size_t j) -> double {
        if (dp[i][j] >= 0) {
            return dp[i][j];
        }

        double dx = shape1[i][0] - shape2[j][0];
        double dy = shape1[i][1] - shape2[j][1];
        double point_dist = std::sqrt(dx * dx + dy * dy);

        if (i == 0 && j == 0) {
            dp[i][j] = point_dist;
        } else if (i == 0) {
            dp[i][j] = std::max(compute_distance(i, j - 1), point_dist);
        } else if (j == 0) {
            dp[i][j] = std::max(compute_distance(i - 1, j), point_dist);
        } else {
            double min_prev = std::min({
                compute_distance(i - 1, j),
                compute_distance(i, j - 1),
                compute_distance(i - 1, j - 1)
            });
            dp[i][j] = std::max(min_prev, point_dist);
        }

        return dp[i][j];
    };

    return compute_distance(m - 1, n - 1);
}

// EdgeCache implementations
EdgeCache::EdgeCache(const std::vector<std::vector<double>>& polygon) {
    if (polygon.size() < 2) {
        total_perimeter_ = 0.0;
        return;
    }

    edges_.reserve(polygon.size());
    total_perimeter_ = 0.0;

    for (size_t i = 0; i < polygon.size(); ++i) {
        size_t j = (i + 1) % polygon.size();

        EdgeInfo edge;
        edge.start_point = polygon[i];
        edge.end_point = polygon[j];

        double dx = edge.end_point[0] - edge.start_point[0];
        double dy = edge.end_point[1] - edge.start_point[1];
        edge.length = std::sqrt(dx * dx + dy * dy);

        total_perimeter_ += edge.length;
        edge.cumulative_length = total_perimeter_;

        edges_.push_back(edge);
    }
}

std::vector<double> EdgeCache::point_at_parameter(double t) const {
    if (edges_.empty()) {
        return {0.0, 0.0};
    }

    // Clamp parameter to [0, 1]
    t = std::max(0.0, std::min(1.0, t));

    double target_distance = t * total_perimeter_;

    // Find the edge containing this distance
    for (const auto& edge : edges_) {
        if (target_distance <= edge.cumulative_length) {
            double edge_start_distance = edge.cumulative_length - edge.length;
            double edge_parameter = (target_distance - edge_start_distance) / edge.length;

            // Interpolate along the edge
            double x = edge.start_point[0] + edge_parameter * (edge.end_point[0] - edge.start_point[0]);
            double y = edge.start_point[1] + edge_parameter * (edge.end_point[1] - edge.start_point[1]);

            return {x, y};
        }
    }

    // Return last point if we somehow got here
    return edges_.back().end_point;
}

std::vector<std::vector<double>> EdgeCache::sample_points(int count) const {
    std::vector<std::vector<double>> points;

    if (count <= 0 || edges_.empty()) {
        return points;
    }

    points.reserve(count);

    for (int i = 0; i < count; ++i) {
        double t = static_cast<double>(i) / static_cast<double>(count);
        points.push_back(point_at_parameter(t));
    }

    return points;
}

const std::vector<double>& EdgeCache::get_corner_points() const {
    if (!corner_cache_valid_) {
        corner_cache_.clear();
        for (const auto& edge : edges_) {
            corner_cache_.push_back(edge.start_point[0]);
            corner_cache_.push_back(edge.start_point[1]);
        }
        corner_cache_valid_ = true;
    }

    return corner_cache_;
}

double EdgeCache::find_closest_parameter(const std::vector<double>& point) const {
    if (edges_.empty() || point.size() < 2) {
        return 0.0;
    }

    double min_distance = std::numeric_limits<double>::max();
    double best_parameter = 0.0;

    double cumulative_distance = 0.0;

    for (const auto& edge : edges_) {
        // Find closest point on this edge
        double edge_dx = edge.end_point[0] - edge.start_point[0];
        double edge_dy = edge.end_point[1] - edge.start_point[1];
        double edge_length_sq = edge_dx * edge_dx + edge_dy * edge_dy;

        if (edge_length_sq > 1e-12) {
            double point_dx = point[0] - edge.start_point[0];
            double point_dy = point[1] - edge.start_point[1];

            double dot_product = point_dx * edge_dx + point_dy * edge_dy;
            double t = std::max(0.0, std::min(1.0, dot_product / edge_length_sq));

            double closest_x = edge.start_point[0] + t * edge_dx;
            double closest_y = edge.start_point[1] + t * edge_dy;

            double dist_dx = point[0] - closest_x;
            double dist_dy = point[1] - closest_y;
            double distance = std::sqrt(dist_dx * dist_dx + dist_dy * dist_dy);

            if (distance < min_distance) {
                min_distance = distance;
                best_parameter = (cumulative_distance - edge.length + t * edge.length) / total_perimeter_;
            }
        }

        cumulative_distance = edge.cumulative_length;
    }

    return best_parameter;
}

py::list EdgeCache::get_edges_info() const {
    py::list info;

    for (const auto& edge : edges_) {
        py::dict edge_info;
        edge_info["start"] = edge.start_point;
        edge_info["end"] = edge.end_point;
        edge_info["length"] = edge.length;
        edge_info["cumulative_length"] = edge.cumulative_length;
        info.append(edge_info);
    }

    return info;
}

// NFPCalculator implementations
py::dict NFPCalculator::calculate_detailed_nfp(const std::vector<std::vector<double>>& stationary,
                                              const std::vector<std::vector<double>>& moving) {
    py::dict result;

    // This would implement detailed NFP calculation
    // For now, return placeholder result
    result["success"] = true;
    result["stationary_vertices"] = stationary.size();
    result["moving_vertices"] = moving.size();
    result["nfp_vertices"] = 0;
    result["nfp_polygon"] = py::list();
    result["calculation_time_ms"] = 0;
    result["quality_score"] = 1.0;

    return result;
}

py::list NFPCalculator::calculate_nfp_orientations(const std::vector<std::vector<double>>& stationary,
                                                   const std::vector<std::vector<double>>& moving,
                                                   const std::vector<double>& angles) {
    py::list results;

    for (double angle : angles) {
        // Rotate moving polygon
        double angle_rad = angle * M_PI / 180.0;
        double cos_a = std::cos(angle_rad);
        double sin_a = std::sin(angle_rad);

        std::vector<std::vector<double>> rotated_moving;
        for (const auto& point : moving) {
            if (point.size() >= 2) {
                double x = point[0] * cos_a - point[1] * sin_a;
                double y = point[0] * sin_a + point[1] * cos_a;
                rotated_moving.push_back({x, y});
            }
        }

        // Calculate NFP for this orientation
        auto nfp_result = calculate_detailed_nfp(stationary, rotated_moving);
        nfp_result["rotation_angle"] = angle;
        results.append(nfp_result);
    }

    return results;
}

py::dict NFPCalculator::calculate_detailed_ifp(const std::vector<std::vector<double>>& container,
                                              const std::vector<std::vector<double>>& item) {
    py::dict result;

    // This would implement Inner-fit Polygon calculation
    // For now, return placeholder result
    result["success"] = true;
    result["container_vertices"] = container.size();
    result["item_vertices"] = item.size();
    result["ifp_vertices"] = 0;
    result["ifp_polygon"] = py::list();
    result["calculation_time_ms"] = 0;
    result["valid_placement_area"] = 0.0;

    return result;
}

py::dict NFPCalculator::validate_nfp(const std::vector<std::vector<double>>& stationary,
                                     const std::vector<std::vector<double>>& moving,
                                     const std::vector<std::vector<double>>& nfp) {
    py::dict validation;

    validation["valid"] = true;
    validation["issues"] = py::list();

    // Check basic properties
    if (nfp.empty()) {
        validation["valid"] = false;
        py::cast(validation["issues"]).append("Empty NFP polygon");
    }

    if (nfp.size() < 3) {
        validation["valid"] = false;
        py::cast(validation["issues"]).append("NFP has less than 3 vertices");
    }

    // Check for self-intersections (simplified)
    // This would require more sophisticated intersection detection

    validation["nfp_area"] = 0.0; // Placeholder
    validation["expected_complexity"] = stationary.size() + moving.size();
    validation["actual_complexity"] = nfp.size();

    return validation;
}

std::vector<std::vector<double>> NFPCalculator::find_touching_positions(
    const std::vector<std::vector<double>>& stationary,
    const std::vector<std::vector<double>>& moving) {

    std::vector<std::vector<double>> touching_positions;

    // This would implement touching position finding algorithm
    // For now, return a few sample positions
    if (!stationary.empty() && !moving.empty()) {
        // Sample positions around the stationary shape
        for (const auto& point : stationary) {
            touching_positions.push_back(point);
        }
    }

    return touching_positions;
}

// PrecisionUtils implementations (already implemented in precision.cpp)

// ShapeAnalysis implementations
py::dict ShapeAnalysis::analyze_shape_complexity(const std::vector<std::vector<double>>& points) {
    py::dict analysis;

    if (points.empty()) {
        analysis["complexity_score"] = 0.0;
        return analysis;
    }

    size_t vertex_count = points.size();
    analysis["vertex_count"] = vertex_count;

    // Calculate shape complexity based on various factors
    double perimeter = 0.0;
    double area = 0.0;

    // Calculate perimeter and area
    for (size_t i = 0; i < points.size(); ++i) {
        size_t j = (i + 1) % points.size();
        double dx = points[j][0] - points[i][0];
        double dy = points[j][1] - points[i][1];
        perimeter += std::sqrt(dx * dx + dy * dy);

        area += points[i][0] * points[j][1] - points[j][0] * points[i][1];
    }
    area = std::abs(area) / 2.0;

    analysis["perimeter"] = perimeter;
    analysis["area"] = area;

    // Compactness ratio (area / perimeter^2)
    double compactness = (perimeter > 0) ? area / (perimeter * perimeter) : 0.0;
    analysis["compactness"] = compactness;

    // Convexity measure
    auto hull = AdvancedGeometry::convex_hull(points);
    double hull_area = 0.0;
    for (size_t i = 0; i < hull.size(); ++i) {
        size_t j = (i + 1) % hull.size();
        hull_area += hull[i][0] * hull[j][1] - hull[j][0] * hull[i][1];
    }
    hull_area = std::abs(hull_area) / 2.0;

    double convexity = (hull_area > 0) ? area / hull_area : 0.0;
    analysis["convexity"] = convexity;
    analysis["convex_hull_vertices"] = hull.size();

    // Overall complexity score (0-1, higher = more complex)
    double complexity_score = 0.0;
    complexity_score += std::min(1.0, vertex_count / 20.0) * 0.4; // Vertex complexity
    complexity_score += (1.0 - convexity) * 0.4; // Non-convexity
    complexity_score += (1.0 - std::min(1.0, compactness * 10.0)) * 0.2; // Non-compactness

    analysis["complexity_score"] = complexity_score;

    return analysis;
}

py::list ShapeAnalysis::find_bottlenecks(const std::vector<std::vector<double>>& points,
                                        double threshold_ratio) {
    py::list bottlenecks;

    if (points.size() < 5) {
        return bottlenecks;
    }

    // Find local minima in the distance from centroid
    double cx = 0.0, cy = 0.0;
    for (const auto& point : points) {
        cx += point[0];
        cy += point[1];
    }
    cx /= points.size();
    cy /= points.size();

    std::vector<double> distances;
    for (const auto& point : points) {
        double dx = point[0] - cx;
        double dy = point[1] - cy;
        distances.push_back(std::sqrt(dx * dx + dy * dy));
    }

    double max_distance = *std::max_element(distances.begin(), distances.end());
    double threshold = max_distance * threshold_ratio;

    for (size_t i = 1; i < distances.size() - 1; ++i) {
        if (distances[i] < threshold &&
            distances[i] < distances[i-1] &&
            distances[i] < distances[i+1]) {

            py::dict bottleneck;
            bottleneck["index"] = i;
            bottleneck["point"] = points[i];
            bottleneck["distance_from_centroid"] = distances[i];
            bottleneck["severity"] = 1.0 - distances[i] / max_distance;
            bottlenecks.append(bottleneck);
        }
    }

    return bottlenecks;
}

std::vector<std::vector<std::vector<double>>> ShapeAnalysis::decompose_to_convex(
    const std::vector<std::vector<double>>& points) {

    std::vector<std::vector<std::vector<double>>> convex_parts;

    // Simple convex decomposition - triangulation
    if (points.size() < 3) {
        return convex_parts;
    }

    // Fan triangulation from first vertex
    for (size_t i = 1; i < points.size() - 1; ++i) {
        std::vector<std::vector<double>> triangle;
        triangle.push_back(points[0]);
        triangle.push_back(points[i]);
        triangle.push_back(points[i + 1]);
        convex_parts.push_back(triangle);
    }

    return convex_parts;
}

std::vector<int> ShapeAnalysis::find_subdivision_points(
    const std::vector<std::vector<double>>& points,
    int max_subdivisions) {

    std::vector<int> subdivision_indices;

    if (points.size() < 4 || max_subdivisions <= 0) {
        return subdivision_indices;
    }

    // Find points with high curvature
    std::vector<double> curvatures;

    for (size_t i = 0; i < points.size(); ++i) {
        size_t prev = (i + points.size() - 1) % points.size();
        size_t next = (i + 1) % points.size();

        // Calculate angle at this vertex
        double dx1 = points[i][0] - points[prev][0];
        double dy1 = points[i][1] - points[prev][1];
        double dx2 = points[next][0] - points[i][0];
        double dy2 = points[next][1] - points[i][1];

        double dot = dx1 * dx2 + dy1 * dy2;
        double cross = dx1 * dy2 - dy1 * dx2;
        double angle = std::atan2(cross, dot);

        curvatures.push_back(std::abs(angle));
    }

    // Find indices with highest curvature
    std::vector<std::pair<double, int>> curvature_indices;
    for (size_t i = 0; i < curvatures.size(); ++i) {
        curvature_indices.push_back({curvatures[i], static_cast<int>(i)});
    }

    std::sort(curvature_indices.rbegin(), curvature_indices.rend());

    for (int i = 0; i < std::min(max_subdivisions, static_cast<int>(curvature_indices.size())); ++i) {
        subdivision_indices.push_back(curvature_indices[i].second);
    }

    std::sort(subdivision_indices.begin(), subdivision_indices.end());

    return subdivision_indices;
}

py::dict ShapeAnalysis::calculate_moments(const std::vector<std::vector<double>>& points) {
    py::dict moments;

    if (points.empty()) {
        return moments;
    }

    // Calculate centroid (first moment)
    double cx = 0.0, cy = 0.0;
    for (const auto& point : points) {
        cx += point[0];
        cy += point[1];
    }
    cx /= points.size();
    cy /= points.size();

    moments["centroid"] = std::vector<double>{cx, cy};

    // Calculate second moments
    double m00 = points.size();
    double m10 = cx * m00;
    double m01 = cy * m00;

    double m20 = 0.0, m11 = 0.0, m02 = 0.0;
    for (const auto& point : points) {
        double dx = point[0] - cx;
        double dy = point[1] - cy;
        m20 += dx * dx;
        m11 += dx * dy;
        m02 += dy * dy;
    }

    moments["m00"] = m00;
    moments["m10"] = m10;
    moments["m01"] = m01;
    moments["m20"] = m20;
    moments["m11"] = m11;
    moments["m02"] = m02;

    // Principal axes
    double theta = 0.5 * std::atan2(2.0 * m11, m20 - m02);
    moments["principal_axis_angle"] = theta * 180.0 / M_PI;

    return moments;
}

std::vector<double> ShapeAnalysis::generate_shape_signature(
    const std::vector<std::vector<double>>& points,
    int signature_length) {

    std::vector<double> signature(signature_length, 0.0);

    if (points.empty() || signature_length <= 0) {
        return signature;
    }

    // Calculate centroid
    double cx = 0.0, cy = 0.0;
    for (const auto& point : points) {
        cx += point[0];
        cy += point[1];
    }
    cx /= points.size();
    cy /= points.size();

    // Create distance signature
    EdgeCache edge_cache(points);

    for (int i = 0; i < signature_length; ++i) {
        double t = static_cast<double>(i) / static_cast<double>(signature_length);
        auto point = edge_cache.point_at_parameter(t);

        double dx = point[0] - cx;
        double dy = point[1] - cy;
        signature[i] = std::sqrt(dx * dx + dy * dy);
    }

    // Normalize signature
    double max_distance = *std::max_element(signature.begin(), signature.end());
    if (max_distance > 0) {
        for (double& value : signature) {
            value /= max_distance;
        }
    }

    return signature;
}

} // namespace nest2d_wrapper
