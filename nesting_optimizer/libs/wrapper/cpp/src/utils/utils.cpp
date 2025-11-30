#include "../../include/utils/utils.hpp"
#include <libnest2d/libnest2d.hpp>
#include <sstream>
#include <cmath>
#include <algorithm>

namespace nest2d_wrapper {

// Basic polygon operations
double polygon_area(const std::vector<std::vector<double>>& polygon) {
    if (polygon.size() < 3) return 0.0;

    double area = 0.0;
    size_t n = polygon.size();

    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        if (polygon[i].size() >= 2 && polygon[j].size() >= 2) {
            area += polygon[i][0] * polygon[j][1];
            area -= polygon[j][0] * polygon[i][1];
        }
    }

    return std::abs(area) / 2.0;
}

py::dict polygon_bounds(const std::vector<std::vector<double>>& polygon) {
    py::dict result;

    if (polygon.empty()) {
        result["min_x"] = 0.0;
        result["min_y"] = 0.0;
        result["max_x"] = 0.0;
        result["max_y"] = 0.0;
        result["width"] = 0.0;
        result["height"] = 0.0;
        return result;
    }

    double min_x = polygon[0].size() > 0 ? polygon[0][0] : 0.0;
    double max_x = min_x;
    double min_y = polygon[0].size() > 1 ? polygon[0][1] : 0.0;
    double max_y = min_y;

    for (const auto& point : polygon) {
        if (point.size() >= 2) {
            min_x = std::min(min_x, point[0]);
            max_x = std::max(max_x, point[0]);
            min_y = std::min(min_y, point[1]);
            max_y = std::max(max_y, point[1]);
        }
    }

    result["min_x"] = min_x;
    result["min_y"] = min_y;
    result["max_x"] = max_x;
    result["max_y"] = max_y;
    result["width"] = max_x - min_x;
    result["height"] = max_y - min_y;

    return result;
}

bool point_in_polygon(double x, double y, const std::vector<std::vector<double>>& polygon) {
    if (polygon.size() < 3) return false;

    bool inside = false;
    size_t n = polygon.size();

    for (size_t i = 0, j = n - 1; i < n; j = i++) {
        if (polygon[i].size() < 2 || polygon[j].size() < 2) continue;

        double xi = polygon[i][0], yi = polygon[i][1];
        double xj = polygon[j][0], yj = polygon[j][1];

        if (((yi > y) != (yj > y)) &&
            (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
            inside = !inside;
        }
    }

    return inside;
}

py::dict polygon_centroid(const std::vector<std::vector<double>>& polygon) {
    py::dict result;

    if (polygon.size() < 3) {
        result["x"] = 0.0;
        result["y"] = 0.0;
        return result;
    }

    double area = polygon_area(polygon);
    if (area == 0.0) {
        result["x"] = 0.0;
        result["y"] = 0.0;
        return result;
    }

    double cx = 0.0, cy = 0.0;
    size_t n = polygon.size();

    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        if (polygon[i].size() >= 2 && polygon[j].size() >= 2) {
            double cross = polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1];
            cx += (polygon[i][0] + polygon[j][0]) * cross;
            cy += (polygon[i][1] + polygon[j][1]) * cross;
        }
    }

    double factor = 1.0 / (6.0 * area);
    result["x"] = cx * factor;
    result["y"] = cy * factor;

    return result;
}

bool polygon_is_convex(const std::vector<std::vector<double>>& polygon) {
    if (polygon.size() < 3) return false;

    bool sign = false;
    bool first = true;
    size_t n = polygon.size();

    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        size_t k = (i + 2) % n;

        if (polygon[i].size() < 2 || polygon[j].size() < 2 || polygon[k].size() < 2)
            continue;

        double dx1 = polygon[j][0] - polygon[i][0];
        double dy1 = polygon[j][1] - polygon[i][1];
        double dx2 = polygon[k][0] - polygon[j][0];
        double dy2 = polygon[k][1] - polygon[j][1];

        double cross = dx1 * dy2 - dy1 * dx2;

        if (std::abs(cross) > 1e-10) {
            if (first) {
                sign = cross > 0;
                first = false;
            } else if ((cross > 0) != sign) {
                return false;
            }
        }
    }

    return true;
}

std::vector<std::vector<double>> polygon_rotate(const std::vector<std::vector<double>>& polygon,
                                               double angle_degrees,
                                               double center_x, double center_y) {
    std::vector<std::vector<double>> result = polygon;
    double angle_rad = angle_degrees * M_PI / 180.0;
    double cos_a = std::cos(angle_rad);
    double sin_a = std::sin(angle_rad);

    for (auto& point : result) {
        if (point.size() >= 2) {
            double x = point[0] - center_x;
            double y = point[1] - center_y;

            point[0] = center_x + x * cos_a - y * sin_a;
            point[1] = center_y + x * sin_a + y * cos_a;
        }
    }

    return result;
}

std::vector<std::vector<double>> polygon_translate(const std::vector<std::vector<double>>& polygon,
                                                  double dx, double dy) {
    std::vector<std::vector<double>> result = polygon;

    for (auto& point : result) {
        if (point.size() >= 2) {
            point[0] += dx;
            point[1] += dy;
        }
    }

    return result;
}

// Validation and cleaning
bool polygon_is_valid(const std::vector<std::vector<double>>& polygon) {
    if (polygon.size() < 3) return false;

    // Check if all points have at least 2 coordinates
    for (const auto& point : polygon) {
        if (point.size() < 2) return false;
    }

    // Check for minimum area
    return std::abs(polygon_area(polygon)) > 1e-10;
}

std::vector<std::vector<double>> polygon_fix_orientation(const std::vector<std::vector<double>>& polygon) {
    std::vector<std::vector<double>> result = polygon;

    // Calculate signed area to determine orientation
    double signed_area = 0.0;
    size_t n = polygon.size();

    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        if (polygon[i].size() >= 2 && polygon[j].size() >= 2) {
            signed_area += polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1];
        }
    }

    // If clockwise (negative area), reverse the order
    if (signed_area < 0) {
        std::reverse(result.begin(), result.end());
    }

    return result;
}

std::vector<std::vector<double>> polygon_simplify(const std::vector<std::vector<double>>& polygon,
                                                 double tolerance) {
    if (polygon.size() <= 3) return polygon;

    std::vector<std::vector<double>> result;
    result.reserve(polygon.size());

    for (size_t i = 0; i < polygon.size(); ++i) {
        size_t next = (i + 1) % polygon.size();

        if (polygon[i].size() >= 2 && polygon[next].size() >= 2) {
            double dx = polygon[next][0] - polygon[i][0];
            double dy = polygon[next][1] - polygon[i][1];
            double dist = std::sqrt(dx * dx + dy * dy);

            if (dist >= tolerance) {
                result.push_back(polygon[i]);
            }
        }
    }

    return result;
}

std::vector<std::vector<double>> polygon_clean(const std::vector<std::vector<double>>& polygon) {
    auto result = polygon_fix_orientation(polygon);
    result = polygon_simplify(result, 1e-6);
    return result;
}

// Visualization
std::string polygon_to_svg(const std::vector<std::vector<double>>& polygon,
                          const std::string& fill_color,
                          const std::string& stroke_color,
                          double stroke_width) {
    std::ostringstream svg;

    if (polygon.empty()) return "";

    // Calculate bounds for viewBox
    auto bounds = polygon_bounds(polygon);
    double margin = 10.0;
    double viewbox_x = bounds["min_x"].cast<double>() - margin;
    double viewbox_y = bounds["min_y"].cast<double>() - margin;
    double viewbox_width = bounds["width"].cast<double>() + 2 * margin;
    double viewbox_height = bounds["height"].cast<double>() + 2 * margin;

    svg << "<svg viewBox=\"" << viewbox_x << " " << viewbox_y << " "
        << viewbox_width << " " << viewbox_height
        << "\" xmlns=\"http://www.w3.org/2000/svg\">";

    svg << "<polygon points=\"";
    for (size_t i = 0; i < polygon.size(); ++i) {
        if (polygon[i].size() >= 2) {
            if (i > 0) svg << " ";
            svg << polygon[i][0] << "," << polygon[i][1];
        }
    }
    svg << "\" fill=\"" << fill_color << "\" stroke=\"" << stroke_color
        << "\" stroke-width=\"" << stroke_width << "\"/>";

    svg << "</svg>";

    return svg.str();
}

std::string shapes_to_svg(const std::vector<Shape>& shapes,
                         const Sheet& sheet,
                         double scale) {
    std::ostringstream svg;

    double margin = 20.0;
    double svg_width = sheet.width * scale + 2 * margin;
    double svg_height = sheet.height * scale + 2 * margin;

    svg << "<svg width=\"" << svg_width << "\" height=\"" << svg_height
        << "\" viewBox=\"0 0 " << svg_width << " " << svg_height
        << "\" xmlns=\"http://www.w3.org/2000/svg\">";

    // Draw sheet boundary
    svg << "<rect x=\"" << margin << "\" y=\"" << margin
        << "\" width=\"" << sheet.width * scale
        << "\" height=\"" << sheet.height * scale
        << "\" fill=\"none\" stroke=\"black\" stroke-width=\"2\"/>";

    // Draw shapes
    std::vector<std::string> colors = {"red", "blue", "green", "orange", "purple", "brown"};

    for (size_t i = 0; i < shapes.size(); ++i) {
        auto raw_shape = shapes[i].get_raw_shape();
        std::string color = colors[i % colors.size()];

        svg << "<polygon points=\"";
        for (size_t j = 0; j < raw_shape.size(); ++j) {
            if (raw_shape[j].size() >= 2) {
                if (j > 0) svg << " ";
                double x = raw_shape[j][0] * scale + margin;
                double y = raw_shape[j][1] * scale + margin;
                svg << x << "," << y;
            }
        }
        svg << "\" fill=\"" << color << "\" fill-opacity=\"0.7\" stroke=\"black\" stroke-width=\"1\"/>";
    }

    svg << "</svg>";

    return svg.str();
}

py::dict polygon_statistics(const std::vector<std::vector<double>>& polygon) {
    py::dict stats;

    stats["vertex_count"] = polygon.size();
    stats["area"] = polygon_area(polygon);
    stats["is_convex"] = polygon_is_convex(polygon);
    stats["is_valid"] = polygon_is_valid(polygon);
    stats["bounds"] = polygon_bounds(polygon);
    stats["centroid"] = polygon_centroid(polygon);

    // Calculate perimeter
    double perimeter = 0.0;
    for (size_t i = 0; i < polygon.size(); ++i) {
        size_t j = (i + 1) % polygon.size();
        if (polygon[i].size() >= 2 && polygon[j].size() >= 2) {
            double dx = polygon[j][0] - polygon[i][0];
            double dy = polygon[j][1] - polygon[i][1];
            perimeter += std::sqrt(dx * dx + dy * dy);
        }
    }
    stats["perimeter"] = perimeter;

    return stats;
}

} // namespace nest2d_wrapper
