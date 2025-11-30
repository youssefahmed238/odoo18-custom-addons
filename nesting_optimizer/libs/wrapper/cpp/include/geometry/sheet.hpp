#ifndef NEST2D_SHEET_HPP
#define NEST2D_SHEET_HPP

#include "../core/types.hpp"
#include <string>

namespace nest2d_wrapper {

/**
 * Sheet represents the material that shapes will be cut from
 */
class Sheet {
public:
    double width, height;

    Sheet(double width, double height) : width(width), height(height) {}

    libnest2d::Box to_internal() const {
        return libnest2d::Box(mm_to_coord(width), mm_to_coord(height));
    }

    double area() const {
        return width * height;
    }

    double perimeter() const {
        return 2.0 * (width + height);
    }

    bool can_fit_rectangle(double rect_width, double rect_height) const {
        return rect_width <= width && rect_height <= height;
    }

    bool can_fit_circle(double radius) const {
        return 2.0 * radius <= width && 2.0 * radius <= height;
    }

    std::string to_string() const;
};

} // namespace nest2d_wrapper

#endif // NEST2D_SHEET_HPP
