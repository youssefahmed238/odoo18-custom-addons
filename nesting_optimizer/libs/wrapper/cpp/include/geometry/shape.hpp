#ifndef NEST2D_SHAPE_HPP
#define NEST2D_SHAPE_HPP

#include "../core/types.hpp"
#include "point.hpp"
#include "rectangle.hpp"
#include "circle.hpp"
#include <pybind11/pybind11.h>
#include <string>
#include <vector>

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Shape represents a 2D piece that will be cut from a sheet
 * Complete wrapper for LibNest2D Item with all functionality
 */
class Shape {
private:
    libnest2d::Item internal_item;

public:
    Shape(const std::vector<std::vector<double>>& points);
    Shape(const libnest2d::Item& item) : internal_item(item) {}

    // Factory methods
    static Shape create_rectangle(double width, double height);
    static Shape create_circle(double radius, int segments = 32);
    static Shape from_rectangle(const Rectangle& rect);
    static Shape from_circle(const Circle& circle);

    // Geometric properties
    double area() const;
    size_t vertex_count() const;
    size_t hole_count() const;
    bool is_convex() const;
    bool is_contour_convex() const;
    bool is_hole_convex(unsigned hole_idx) const;
    bool are_holes_convex() const;
    py::dict bounding_box() const;

    // Vertex access
    Point get_vertex(size_t index) const;
    void set_vertex(size_t index, const Point& vertex);
    std::vector<Point> get_vertices() const;

    // Reference points
    Point reference_vertex() const;
    Point rightmost_top_vertex() const;
    Point leftmost_bottom_vertex() const;

    // Transformations
    void translate(double x, double y);
    void translate(const Point& delta);
    void rotate(double angle_degrees);
    void set_inflation(double distance);
    void inflate(double distance); // Add to existing inflation
    double get_inflation() const;

    // Position/state management
    void set_sheet_id(int id);
    int get_sheet_id() const;
    void set_priority(int priority);
    int get_priority() const;
    bool is_fixed() const;
    void mark_as_fixed_in_sheet(int sheet_id);

    // Shape access
    std::vector<std::vector<double>> get_transformed_shape() const;
    std::vector<std::vector<double>> get_raw_shape() const;
    std::vector<std::vector<double>> get_inflated_shape() const;
    void reset_transformation();

    // Position info
    Point get_translation() const;
    double get_rotation_degrees() const;
    double get_rotation_radians() const;

    // Geometric queries
    bool is_point_inside(double x, double y) const;
    bool is_point_inside(const Point& point) const;
    bool contains_shape(const Shape& other) const;
    bool is_inside_box(const Sheet& sheet) const;
    bool is_inside_circle(double center_x, double center_y, double radius) const;

    // Static intersection methods
    static bool intersects(const Shape& shape1, const Shape& shape2);
    static bool touches(const Shape& shape1, const Shape& shape2);

    // Internal access
    libnest2d::Item& get_internal() { return internal_item; }
    const libnest2d::Item& get_internal() const { return internal_item; }

    std::string to_string() const;
};

} // namespace nest2d_wrapper

#endif // NEST2D_SHAPE_HPP
