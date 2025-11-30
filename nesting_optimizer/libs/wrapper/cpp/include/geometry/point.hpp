#ifndef NEST2D_POINT_HPP
#define NEST2D_POINT_HPP

#include "../core/types.hpp"
#include <string>

namespace nest2d_wrapper {

/**
 * Python-friendly Point class
 */
class Point {
public:
    double x, y;

    Point(double x = 0.0, double y = 0.0) : x(x), y(y) {}
    Point(const libnest2d::PointImpl& pt) : x(coord_to_mm(pt.X)), y(coord_to_mm(pt.Y)) {}

    libnest2d::PointImpl to_internal() const {
        return libnest2d::PointImpl(mm_to_coord(x), mm_to_coord(y));
    }

    std::string to_string() const;
};

} // namespace nest2d_wrapper

#endif // NEST2D_POINT_HPP
