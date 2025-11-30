#ifndef NEST2D_RECTANGLE_HPP
#define NEST2D_RECTANGLE_HPP

#include "../core/types.hpp"
#include <string>

namespace nest2d_wrapper {

/**
 * Rectangle represents a rectangular shape
 */
class Rectangle {
public:
    double width, height;

    Rectangle(double width, double height) : width(width), height(height) {}

    LibNest2DRectangle to_internal() const {
        return LibNest2DRectangle(mm_to_coord(width), mm_to_coord(height));
    }

    // Convert to points for Shape creation
    std::vector<std::vector<double>> to_points() const {
        return {
            {0, 0},
            {width, 0},
            {width, height},
            {0, height}
        };
    }

    double area() const {
        return width * height;
    }

    double perimeter() const {
        return 2.0 * (width + height);
    }

    std::string to_string() const;
};

} // namespace nest2d_wrapper

#endif // NEST2D_RECTANGLE_HPP
