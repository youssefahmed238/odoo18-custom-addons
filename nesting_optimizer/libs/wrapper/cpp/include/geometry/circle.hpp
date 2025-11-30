#ifndef NEST2D_CIRCLE_HPP
#define NEST2D_CIRCLE_HPP

#include "../core/types.hpp"
#include <string>
#include <vector>
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace nest2d_wrapper {

/**
 * Circle represents a circular shape (approximated with polygon)
 */
class Circle {
public:
    double radius;
    int segments;

    Circle(double radius, int segments = 32) : radius(radius), segments(segments) {}

    LibNest2DCircle to_internal() const {
        return LibNest2DCircle(LibNest2DPoint(0, 0), mm_to_coord(radius));
    }

    // Convert to points for Shape creation
    std::vector<std::vector<double>> to_points() const {
        std::vector<std::vector<double>> points;
        points.reserve(segments);
        for (int i = 0; i < segments; ++i) {
            double angle = 2.0 * M_PI * i / segments;
            points.push_back({radius * std::cos(angle), radius * std::sin(angle)});
        }
        return points;
    }

    double area() const {
        return M_PI * radius * radius;
    }

    double perimeter() const {
        return 2.0 * M_PI * radius;
    }

    double circumference() const {
        return perimeter();
    }

    std::string to_string() const;
};

} // namespace nest2d_wrapper

#endif // NEST2D_CIRCLE_HPP
