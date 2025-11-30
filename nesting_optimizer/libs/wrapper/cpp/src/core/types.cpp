#include "../include/core/types.hpp"
#include <cmath>

namespace nest2d_wrapper {

/**
 * Convert degrees to radians
 */
libnest2d::Radians degrees_to_radians(double degrees) {
    return libnest2d::Radians(degrees * M_PI / 180.0);
}

/**
 * Convert radians to degrees
 */
double radians_to_degrees(const libnest2d::Radians& radians) {
    return static_cast<double>(radians) * 180.0 / M_PI;
}

/**
 * Create a polygon from a list of 2D points
 */
Polygon create_polygon(const std::vector<std::vector<double>>& points) {
    Polygon poly;
    poly.reserve(points.size());

    for (const auto& point : points) {
        if (point.size() >= 2) {
            libnest2d::PointImpl pt(
                static_cast<Coord>(point[0] * COORD_SCALE),
                static_cast<Coord>(point[1] * COORD_SCALE)
            );
            poly.push_back(pt);
        }
    }
    return poly;
}

/**
 * Convert polygon back to list of points
 */
std::vector<std::vector<double>> polygon_to_points(const Polygon& polygon) {
    std::vector<std::vector<double>> points;
    points.reserve(polygon.size());

    for (const auto& pt : polygon) {
        std::vector<double> point;
        point.push_back(static_cast<double>(pt.X) / COORD_SCALE);
        point.push_back(static_cast<double>(pt.Y) / COORD_SCALE);
        points.push_back(point);
    }
    return points;
}

} // namespace nest2d_wrapper
