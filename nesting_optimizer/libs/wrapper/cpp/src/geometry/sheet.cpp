#include "../../include/geometry/sheet.hpp"
#include <sstream>

namespace nest2d_wrapper {

Sheet::Sheet(double width, double height) : width(width), height(height) {}

double Sheet::area() const {
    return width * height;
}

double Sheet::perimeter() const {
    return 2.0 * (width + height);
}

LibNest2DRectangle Sheet::to_libnest2d() const {
    return LibNest2DRectangle(static_cast<Coord>(width * COORD_SCALE),
                              static_cast<Coord>(height * COORD_SCALE));
}

Sheet Sheet::from_libnest2d(const LibNest2DRectangle& rect) {
    return Sheet(static_cast<double>(rect.width()) / COORD_SCALE,
                 static_cast<double>(rect.height()) / COORD_SCALE);
}

std::vector<Point> Sheet::to_points() const {
    return {
        Point(0, 0),
        Point(width, 0),
        Point(width, height),
        Point(0, height)
    };
}

bool Sheet::contains_point(const Point& point) const {
    return point.x >= 0 && point.x <= width &&
           point.y >= 0 && point.y <= height;
}

std::string Sheet::to_string() const {
    std::ostringstream oss;
    oss << "Sheet(" << width << "x" << height << ", area=" << area() << ")";
    return oss.str();
}

} // namespace nest2d_wrapper
