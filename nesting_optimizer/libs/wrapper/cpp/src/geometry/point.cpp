#include "../../include/geometry/point.hpp"
#include <sstream>
#include <cmath>

namespace nest2d_wrapper {

Point::Point(double x, double y) : x(x), y(y) {}

double Point::distance_to(const Point& other) const {
    double dx = x - other.x;
    double dy = y - other.y;
    return std::sqrt(dx * dx + dy * dy);
}

Point Point::midpoint(const Point& other) const {
    return Point((x + other.x) / 2.0, (y + other.y) / 2.0);
}

void Point::translate(double dx, double dy) {
    x += dx;
    y += dy;
}

void Point::rotate(double angle_degrees, const Point& center) {
    double angle_rad = angle_degrees * M_PI / 180.0;
    double cos_a = std::cos(angle_rad);
    double sin_a = std::sin(angle_rad);

    double dx = x - center.x;
    double dy = y - center.y;

    x = center.x + dx * cos_a - dy * sin_a;
    y = center.y + dx * sin_a + dy * cos_a;
}

LibNest2DPoint Point::to_libnest2d() const {
    return LibNest2DPoint(static_cast<Coord>(x * COORD_SCALE),
                          static_cast<Coord>(y * COORD_SCALE));
}

Point Point::from_libnest2d(const LibNest2DPoint& point) {
    return Point(static_cast<double>(getX(point)) / COORD_SCALE,
                 static_cast<double>(getY(point)) / COORD_SCALE);
}

std::string Point::to_string() const {
    std::ostringstream oss;
    oss << "Point(" << x << ", " << y << ")";
    return oss.str();
}

} // namespace nest2d_wrapper
