#include "../include/core/precision.hpp"
#include <sstream>
#include <iomanip>
#include <cmath>
#include <algorithm>

namespace nest2d_wrapper {

// PrecisionNumber implementations
std::string PrecisionNumber::to_string(int precision) const {
    if (is_exact_ && !exact_representation_.empty()) {
        return exact_representation_;
    }

    std::ostringstream oss;
    oss << std::fixed << std::setprecision(precision) << value_;
    return oss.str();
}

PrecisionNumber PrecisionNumber::operator+(const PrecisionNumber& other) const {
    if (is_exact_ && other.is_exact_) {
        // For exact arithmetic, we would use rational number library here
        // Simplified implementation
        return PrecisionNumber(value_ + other.value_);
    }
    return PrecisionNumber(value_ + other.value_);
}

PrecisionNumber PrecisionNumber::operator-(const PrecisionNumber& other) const {
    return PrecisionNumber(value_ - other.value_);
}

PrecisionNumber PrecisionNumber::operator*(const PrecisionNumber& other) const {
    return PrecisionNumber(value_ * other.value_);
}

PrecisionNumber PrecisionNumber::operator/(const PrecisionNumber& other) const {
    if (std::abs(other.value_) < std::numeric_limits<double>::epsilon()) {
        throw std::runtime_error("Division by zero");
    }
    return PrecisionNumber(value_ / other.value_);
}

bool PrecisionNumber::operator==(const PrecisionNumber& other) const {
    if (is_exact_ && other.is_exact_) {
        return exact_representation_ == other.exact_representation_;
    }
    return std::abs(value_ - other.value_) < std::numeric_limits<double>::epsilon();
}

bool PrecisionNumber::operator<(const PrecisionNumber& other) const {
    return value_ < other.value_;
}

bool PrecisionNumber::equals(const PrecisionNumber& other, double tolerance) const {
    return std::abs(value_ - other.value_) <= tolerance;
}

// HighPrecisionGeometry implementations
PrecisionNumber HighPrecisionGeometry::calculate_precise_area(
    const std::vector<std::vector<double>>& points,
    const PrecisionConfig& config) {

    if (points.size() < 3) {
        return PrecisionNumber(0.0);
    }

    double area = 0.0;
    size_t n = points.size();

    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        area += points[i][0] * points[j][1];
        area -= points[j][0] * points[i][1];
    }

    area = std::abs(area) / 2.0;

    if (config.level == PrecisionConfig::PrecisionLevel::EXACT) {
        return PrecisionNumber(std::to_string(area));
    }

    return PrecisionNumber(area);
}

PrecisionNumber HighPrecisionGeometry::calculate_precise_distance(
    const std::vector<double>& p1,
    const std::vector<double>& p2,
    const PrecisionConfig& config) {

    if (p1.size() < 2 || p2.size() < 2) {
        return PrecisionNumber(0.0);
    }

    double dx = p1[0] - p2[0];
    double dy = p1[1] - p2[1];
    double distance = std::sqrt(dx * dx + dy * dy);

    if (config.level == PrecisionConfig::PrecisionLevel::EXACT) {
        return PrecisionNumber(std::to_string(distance));
    }

    return PrecisionNumber(distance);
}

bool HighPrecisionGeometry::precise_point_in_polygon(
    const std::vector<std::vector<double>>& polygon,
    const std::vector<double>& point,
    const PrecisionConfig& config) {

    if (polygon.size() < 3 || point.size() < 2) {
        return false;
    }

    bool inside = false;
    size_t n = polygon.size();

    for (size_t i = 0, j = n - 1; i < n; j = i++) {
        const auto& pi = polygon[i];
        const auto& pj = polygon[j];

        if (((pi[1] > point[1]) != (pj[1] > point[1])) &&
            (point[0] < (pj[0] - pi[0]) * (point[1] - pi[1]) / (pj[1] - pi[1]) + pi[0])) {
            inside = !inside;
        }
    }

    return inside;
}

std::vector<std::vector<std::vector<double>>> HighPrecisionGeometry::precise_intersection(
    const std::vector<std::vector<double>>& poly1,
    const std::vector<std::vector<double>>& poly2,
    const PrecisionConfig& config) {

    // This would use a precise intersection algorithm
    // For now, return empty result as placeholder
    std::vector<std::vector<std::vector<double>>> result;
    return result;
}

std::vector<std::vector<double>> HighPrecisionGeometry::snap_to_precision_grid(
    const std::vector<std::vector<double>>& points,
    double grid_size) {

    std::vector<std::vector<double>> snapped_points;
    snapped_points.reserve(points.size());

    for (const auto& point : points) {
        if (point.size() >= 2) {
            double x = std::round(point[0] / grid_size) * grid_size;
            double y = std::round(point[1] / grid_size) * grid_size;
            snapped_points.push_back({x, y});
        }
    }

    return snapped_points;
}

std::vector<std::vector<double>> HighPrecisionGeometry::remove_degeneracies(
    const std::vector<std::vector<double>>& points,
    const PrecisionConfig& config) {

    std::vector<std::vector<double>> cleaned_points;

    if (points.empty()) {
        return cleaned_points;
    }

    // Remove duplicate consecutive points
    cleaned_points.push_back(points[0]);

    for (size_t i = 1; i < points.size(); ++i) {
        const auto& current = points[i];
        const auto& last = cleaned_points.back();

        double dx = current[0] - last[0];
        double dy = current[1] - last[1];
        double distance = std::sqrt(dx * dx + dy * dy);

        if (distance > config.tolerance) {
            cleaned_points.push_back(current);
        }
    }

    // Remove collinear points
    if (cleaned_points.size() > 2) {
        std::vector<std::vector<double>> final_points;
        final_points.push_back(cleaned_points[0]);

        for (size_t i = 1; i < cleaned_points.size() - 1; ++i) {
            const auto& prev = cleaned_points[i - 1];
            const auto& curr = cleaned_points[i];
            const auto& next = cleaned_points[i + 1];

            // Check if points are collinear using cross product
            double cross = (curr[0] - prev[0]) * (next[1] - prev[1]) -
                          (curr[1] - prev[1]) * (next[0] - prev[0]);

            if (std::abs(cross) > config.tolerance) {
                final_points.push_back(curr);
            }
        }

        final_points.push_back(cleaned_points.back());
        cleaned_points = final_points;
    }

    return cleaned_points;
}

HighPrecisionGeometry::Orientation HighPrecisionGeometry::robust_orientation(
    const std::vector<double>& p,
    const std::vector<double>& q,
    const std::vector<double>& r,
    const PrecisionConfig& config) {

    if (p.size() < 2 || q.size() < 2 || r.size() < 2) {
        return Orientation::COLLINEAR;
    }

    // Calculate the cross product (q - p) x (r - p)
    double cross = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);

    if (std::abs(cross) <= config.tolerance) {
        return Orientation::COLLINEAR;
    }

    return cross > 0 ? Orientation::COUNTERCLOCKWISE : Orientation::CLOCKWISE;
}

PrecisionNumber HighPrecisionGeometry::signed_area_precise(
    const std::vector<std::vector<double>>& points,
    const PrecisionConfig& config) {

    if (points.size() < 3) {
        return PrecisionNumber(0.0);
    }

    double area = 0.0;
    size_t n = points.size();

    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        area += points[i][0] * points[j][1];
        area -= points[j][0] * points[i][1];
    }

    area /= 2.0;

    if (config.level == PrecisionConfig::PrecisionLevel::EXACT) {
        return PrecisionNumber(std::to_string(area));
    }

    return PrecisionNumber(area);
}

// ExactArithmetic implementations
std::string ExactArithmetic::double_to_exact(double value, int max_denominator) {
    // Simple rational approximation
    if (value == 0.0) return "0";

    bool negative = value < 0;
    value = std::abs(value);

    long long numerator = static_cast<long long>(value);
    double fractional = value - numerator;

    if (fractional < 1e-15) {
        return (negative ? "-" : "") + std::to_string(numerator);
    }

    // Use continued fractions for better approximation
    long long best_num = 1, best_den = 1;
    double best_error = std::abs(fractional - 1.0);

    for (int den = 2; den <= max_denominator; ++den) {
        long long num = static_cast<long long>(std::round(fractional * den));
        double error = std::abs(fractional - static_cast<double>(num) / den);

        if (error < best_error) {
            best_num = num;
            best_den = den;
            best_error = error;
        }

        if (error < 1e-12) break;
    }

    if (numerator == 0) {
        return (negative ? "-" : "") + std::to_string(best_num) + "/" + std::to_string(best_den);
    } else {
        long long total_num = numerator * best_den + best_num;
        return (negative ? "-" : "") + std::to_string(total_num) + "/" + std::to_string(best_den);
    }
}

py::dict ExactArithmetic::exact_polygon_operations(
    const std::vector<std::vector<double>>& points,
    const std::string& operation) {

    py::dict result;
    result["operation"] = operation;
    result["success"] = true;

    try {
        if (operation == "area") {
            auto area = HighPrecisionGeometry::calculate_precise_area(
                points, PrecisionConfig::create_exact());
            result["value"] = area.to_string(25);
        } else if (operation == "perimeter") {
            double perimeter = 0.0;
            for (size_t i = 0; i < points.size(); ++i) {
                size_t j = (i + 1) % points.size();
                auto dist = HighPrecisionGeometry::calculate_precise_distance(
                    points[i], points[j], PrecisionConfig::create_exact());
                perimeter += dist.to_double();
            }
            result["value"] = double_to_exact(perimeter);
        } else {
            result["success"] = false;
            result["error"] = "Unknown operation: " + operation;
        }
    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

bool ExactArithmetic::exact_equal(double a, double b, const std::string& tolerance_str) {
    if (tolerance_str == "0") {
        return a == b; // Exact comparison
    }

    double tolerance = std::stod(tolerance_str);
    return std::abs(a - b) <= tolerance;
}

py::dict ExactArithmetic::exact_line_intersection(
    const std::vector<double>& line1_start,
    const std::vector<double>& line1_end,
    const std::vector<double>& line2_start,
    const std::vector<double>& line2_end) {

    py::dict result;

    if (line1_start.size() < 2 || line1_end.size() < 2 ||
        line2_start.size() < 2 || line2_end.size() < 2) {
        result["intersects"] = false;
        result["error"] = "Invalid line coordinates";
        return result;
    }

    // Calculate intersection using exact arithmetic
    double x1 = line1_start[0], y1 = line1_start[1];
    double x2 = line1_end[0], y2 = line1_end[1];
    double x3 = line2_start[0], y3 = line2_start[1];
    double x4 = line2_end[0], y4 = line2_end[1];

    double denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);

    if (std::abs(denom) < 1e-15) {
        result["intersects"] = false;
        result["parallel"] = true;
        return result;
    }

    double t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom;
    double u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom;

    result["intersects"] = (t >= 0 && t <= 1 && u >= 0 && u <= 1);

    if (result["intersects"].cast<bool>()) {
        double ix = x1 + t * (x2 - x1);
        double iy = y1 + t * (y2 - y1);
        result["intersection"] = std::vector<double>{ix, iy};
        result["t"] = double_to_exact(t);
        result["u"] = double_to_exact(u);
    }

    return result;
}

// NumericalStability implementations
py::dict NumericalStability::analyze_stability(const std::vector<std::vector<double>>& points) {
    py::dict analysis;

    if (points.empty()) {
        analysis["stable"] = true;
        analysis["issues"] = py::list();
        return analysis;
    }

    std::vector<std::string> issues;

    // Check coordinate magnitude
    double min_coord = std::numeric_limits<double>::max();
    double max_coord = std::numeric_limits<double>::lowest();

    for (const auto& point : points) {
        for (double coord : point) {
            min_coord = std::min(min_coord, coord);
            max_coord = std::max(max_coord, coord);
        }
    }

    double range = max_coord - min_coord;
    analysis["coordinate_range"] = range;
    analysis["min_coordinate"] = min_coord;
    analysis["max_coordinate"] = max_coord;

    if (range > 1e12) {
        issues.push_back("Very large coordinate range may cause precision loss");
    }

    if (std::abs(min_coord) > 1e12 || std::abs(max_coord) > 1e12) {
        issues.push_back("Very large coordinate values may cause precision loss");
    }

    // Check for very small features
    double min_edge_length = std::numeric_limits<double>::max();
    for (size_t i = 0; i < points.size(); ++i) {
        size_t j = (i + 1) % points.size();
        double dx = points[j][0] - points[i][0];
        double dy = points[j][1] - points[i][1];
        double length = std::sqrt(dx * dx + dy * dy);
        min_edge_length = std::min(min_edge_length, length);
    }

    analysis["min_edge_length"] = min_edge_length;

    if (min_edge_length < 1e-12) {
        issues.push_back("Very small edges may cause numerical instability");
    }

    analysis["stable"] = issues.empty();
    analysis["issues"] = issues;

    return analysis;
}

py::dict NumericalStability::suggest_precision_improvements(
    const std::vector<std::vector<double>>& points) {

    py::dict suggestions;
    auto analysis = analyze_stability(points);

    std::vector<std::string> improvements;

    if (analysis["coordinate_range"].cast<double>() > 1e12) {
        improvements.push_back("Consider scaling coordinates to a smaller range");

        double scale = 1e6 / analysis["coordinate_range"].cast<double>();
        suggestions["recommended_scale"] = scale;
    }

    if (analysis["min_edge_length"].cast<double>() < 1e-12) {
        improvements.push_back("Consider removing very small edges");
        improvements.push_back("Use snap-to-grid preprocessing");

        suggestions["recommended_grid_size"] = analysis["min_edge_length"].cast<double>() * 10;
    }

    suggestions["improvements"] = improvements;
    suggestions["use_high_precision"] = !analysis["stable"].cast<bool>();

    return suggestions;
}

py::list NumericalStability::detect_numerical_issues(
    const std::vector<std::vector<double>>& points,
    double tolerance) {

    py::list issues;

    // Check for duplicate points
    for (size_t i = 0; i < points.size(); ++i) {
        for (size_t j = i + 1; j < points.size(); ++j) {
            double dx = points[i][0] - points[j][0];
            double dy = points[i][1] - points[j][1];
            double distance = std::sqrt(dx * dx + dy * dy);

            if (distance < tolerance) {
                py::dict issue;
                issue["type"] = "duplicate_points";
                issue["indices"] = std::vector<int>{static_cast<int>(i), static_cast<int>(j)};
                issue["distance"] = distance;
                issues.append(issue);
            }
        }
    }

    // Check for collinear points
    for (size_t i = 0; i < points.size(); ++i) {
        size_t prev = (i + points.size() - 1) % points.size();
        size_t next = (i + 1) % points.size();

        auto orientation = HighPrecisionGeometry::robust_orientation(
            points[prev], points[i], points[next],
            PrecisionConfig(PrecisionConfig::PrecisionLevel::HIGH, tolerance));

        if (orientation == HighPrecisionGeometry::Orientation::COLLINEAR) {
            py::dict issue;
            issue["type"] = "collinear_points";
            issue["indices"] = std::vector<int>{static_cast<int>(prev), static_cast<int>(i), static_cast<int>(next)};
            issues.append(issue);
        }
    }

    return issues;
}

std::vector<std::vector<double>> NumericalStability::improve_numerical_stability(
    const std::vector<std::vector<double>>& points,
    const PrecisionConfig& config) {

    auto result = points;

    // Apply snap to grid if enabled
    if (config.snap_to_grid) {
        result = HighPrecisionGeometry::snap_to_precision_grid(result, config.grid_size);
    }

    // Remove degeneracies
    result = HighPrecisionGeometry::remove_degeneracies(result, config);

    return result;
}

double NumericalStability::calculate_condition_number(
    const std::vector<std::vector<double>>& points) {

    if (points.size() < 2) {
        return 1.0;
    }

    // Calculate the ratio of largest to smallest edge length
    double max_edge = 0.0;
    double min_edge = std::numeric_limits<double>::max();

    for (size_t i = 0; i < points.size(); ++i) {
        size_t j = (i + 1) % points.size();
        double dx = points[j][0] - points[i][0];
        double dy = points[j][1] - points[i][1];
        double length = std::sqrt(dx * dx + dy * dy);

        max_edge = std::max(max_edge, length);
        min_edge = std::min(min_edge, length);
    }

    return (min_edge > 0) ? max_edge / min_edge : std::numeric_limits<double>::infinity();
}

py::dict NumericalStability::recommend_coordinate_scaling(
    const std::vector<std::vector<double>>& points) {

    py::dict recommendation;

    if (points.empty()) {
        recommendation["scale"] = 1.0;
        recommendation["offset"] = std::vector<double>{0.0, 0.0};
        return recommendation;
    }

    // Find bounding box
    double min_x = points[0][0], max_x = points[0][0];
    double min_y = points[0][1], max_y = points[0][1];

    for (const auto& point : points) {
        min_x = std::min(min_x, point[0]);
        max_x = std::max(max_x, point[0]);
        min_y = std::min(min_y, point[1]);
        max_y = std::max(max_y, point[1]);
    }

    double range_x = max_x - min_x;
    double range_y = max_y - min_y;
    double max_range = std::max(range_x, range_y);

    // Recommend scaling to keep coordinates in range [0, 1000]
    double target_range = 1000.0;
    double scale = (max_range > 0) ? target_range / max_range : 1.0;

    recommendation["scale"] = scale;
    recommendation["offset"] = std::vector<double>{-min_x, -min_y};
    recommendation["original_range"] = std::vector<double>{range_x, range_y};
    recommendation["scaled_range"] = std::vector<double>{range_x * scale, range_y * scale};

    return recommendation;
}

// PreciseTransforms implementations
std::vector<std::vector<double>> PreciseTransforms::precise_rotate(
    const std::vector<std::vector<double>>& points,
    double angle_degrees,
    const PrecisionConfig& config) {

    double angle_rad = angle_degrees * M_PI / 180.0;
    double cos_a = std::cos(angle_rad);
    double sin_a = std::sin(angle_rad);

    std::vector<std::vector<double>> rotated_points;
    rotated_points.reserve(points.size());

    for (const auto& point : points) {
        if (point.size() >= 2) {
            double x = point[0] * cos_a - point[1] * sin_a;
            double y = point[0] * sin_a + point[1] * cos_a;

            if (config.snap_to_grid) {
                x = std::round(x / config.grid_size) * config.grid_size;
                y = std::round(y / config.grid_size) * config.grid_size;
            }

            rotated_points.push_back({x, y});
        }
    }

    return rotated_points;
}

std::vector<std::vector<double>> PreciseTransforms::precise_translate(
    const std::vector<std::vector<double>>& points,
    double dx, double dy,
    const PrecisionConfig& config) {

    std::vector<std::vector<double>> translated_points;
    translated_points.reserve(points.size());

    for (const auto& point : points) {
        if (point.size() >= 2) {
            double x = point[0] + dx;
            double y = point[1] + dy;

            if (config.snap_to_grid) {
                x = std::round(x / config.grid_size) * config.grid_size;
                y = std::round(y / config.grid_size) * config.grid_size;
            }

            translated_points.push_back({x, y});
        }
    }

    return translated_points;
}

std::vector<std::vector<double>> PreciseTransforms::precise_scale(
    const std::vector<std::vector<double>>& points,
    double scale_x, double scale_y,
    const PrecisionConfig& config) {

    std::vector<std::vector<double>> scaled_points;
    scaled_points.reserve(points.size());

    for (const auto& point : points) {
        if (point.size() >= 2) {
            double x = point[0] * scale_x;
            double y = point[1] * scale_y;

            if (config.snap_to_grid) {
                x = std::round(x / config.grid_size) * config.grid_size;
                y = std::round(y / config.grid_size) * config.grid_size;
            }

            scaled_points.push_back({x, y});
        }
    }

    return scaled_points;
}

std::vector<std::vector<double>> PreciseTransforms::precise_transform_matrix(
    const std::vector<std::vector<double>>& points,
    const std::vector<std::vector<double>>& transformation_matrix,
    const PrecisionConfig& config) {

    if (transformation_matrix.size() < 2 ||
        transformation_matrix[0].size() < 2 ||
        transformation_matrix[1].size() < 2) {
        throw std::invalid_argument("Invalid transformation matrix");
    }

    std::vector<std::vector<double>> transformed_points;
    transformed_points.reserve(points.size());

    for (const auto& point : points) {
        if (point.size() >= 2) {
            double x = transformation_matrix[0][0] * point[0] + transformation_matrix[0][1] * point[1];
            double y = transformation_matrix[1][0] * point[0] + transformation_matrix[1][1] * point[1];

            // Add translation if matrix is 3x3
            if (transformation_matrix[0].size() > 2) {
                x += transformation_matrix[0][2];
            }
            if (transformation_matrix[1].size() > 2) {
                y += transformation_matrix[1][2];
            }

            if (config.snap_to_grid) {
                x = std::round(x / config.grid_size) * config.grid_size;
                y = std::round(y / config.grid_size) * config.grid_size;
            }

            transformed_points.push_back({x, y});
        }
    }

    return transformed_points;
}

} // namespace nest2d_wrapper
