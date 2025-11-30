#include "../../include/geometry/circle.hpp"
#include <sstream>
#include <cmath>

namespace nest2d_wrapper {

Circle::Circle(double radius, int segments) : radius(radius), segments(segments) {}

double Circle::area() const {
    return M_PI * radius * radius;
}

double Circle::circumference() const {
    return 2.0 * M_PI * radius;
}

std::vector<Point> Circle::to_points() const {
    std::vector<Point> points;
    points.reserve(segments);

    for (int i = 0; i < segments; ++i) {
        double angle = 2.0 * M_PI * i / segments;
        double x = radius * std::cos(angle);
        double y = radius * std::sin(angle);
        points.emplace_back(x, y);
    }

    return points;
}

LibNest2DCircle Circle::to_libnest2d() const {
    return LibNest2DCircle(static_cast<Coord>(radius * COORD_SCALE));
}

Circle Circle::from_libnest2d(const LibNest2DCircle& circle) {
    return Circle(static_cast<double>(circle.radius()) / COORD_SCALE);
}

std::string Circle::to_string() const {
    std::ostringstream oss;
    oss << "Circle(radius=" << radius << ", segments=" << segments
        << ", area=" << area() << ")";
    return oss.str();
}

} // namespace nest2d_wrapper
