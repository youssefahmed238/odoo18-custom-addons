#include "../../include/geometry/rectangle.hpp"
#include <sstream>

namespace nest2d_wrapper {

Rectangle::Rectangle(double width, double height) : width(width), height(height) {}

double Rectangle::area() const {
    return width * height;
}

double Rectangle::perimeter() const {
    return 2.0 * (width + height);
}

std::vector<Point> Rectangle::to_points() const {
    return {
        Point(0, 0),
        Point(width, 0),
        Point(width, height),
        Point(0, height)
    };
}

LibNest2DRectangle Rectangle::to_libnest2d() const {
    return LibNest2DRectangle(static_cast<Coord>(width * COORD_SCALE),
                              static_cast<Coord>(height * COORD_SCALE));
}

Rectangle Rectangle::from_libnest2d(const LibNest2DRectangle& rect) {
    return Rectangle(static_cast<double>(rect.width()) / COORD_SCALE,
                     static_cast<double>(rect.height()) / COORD_SCALE);
}

std::string Rectangle::to_string() const {
    std::ostringstream oss;
    oss << "Rectangle(" << width << "x" << height << ", area=" << area() << ")";
    return oss.str();
}

} // namespace nest2d_wrapper
