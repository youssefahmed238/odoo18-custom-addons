#include "../../include/geometry/shape.hpp"
#include <sstream>
#include <algorithm>
#include <numeric>

namespace nest2d_wrapper {

Shape::Shape(const std::vector<std::vector<double>>& points) {
    // Convert Python-style points to LibNest2D polygon
    Polygon contour;
    for (const auto& point : points) {
        if (point.size() >= 2) {
            contour.emplace_back(static_cast<Coord>(point[0] * COORD_SCALE),
                               static_cast<Coord>(point[1] * COORD_SCALE));
        }
    }
    internal_item = libnest2d::Item(contour);
}

Shape Shape::create_rectangle(double width, double height) {
    Rectangle rect(width, height);
    auto points = rect.to_points();

    std::vector<std::vector<double>> point_data;
    for (const auto& point : points) {
        point_data.push_back({point.x, point.y});
    }

    return Shape(point_data);
}

Shape Shape::create_circle(double radius, int segments) {
    Circle circle(radius, segments);
    auto points = circle.to_points();

    std::vector<std::vector<double>> point_data;
    for (const auto& point : points) {
        point_data.push_back({point.x, point.y});
    }

    return Shape(point_data);
}

Shape Shape::from_rectangle(const Rectangle& rect) {
    return create_rectangle(rect.width, rect.height);
}

Shape Shape::from_circle(const Circle& circle) {
    return create_circle(circle.radius, circle.segments);
}

double Shape::area() const {
    return static_cast<double>(internal_item.area()) / (COORD_SCALE * COORD_SCALE);
}

size_t Shape::vertex_count() const {
    return internal_item.vertexCount();
}

size_t Shape::hole_count() const {
    return internal_item.holeCount();
}

bool Shape::is_convex() const {
    return internal_item.isContourConvex();
}

bool Shape::is_contour_convex() const {
    return internal_item.isContourConvex();
}

py::dict Shape::bounding_box() const {
    auto bb = internal_item.boundingBox();

    py::dict result;
    result["min_x"] = static_cast<double>(getX(bb.minCorner())) / COORD_SCALE;
    result["min_y"] = static_cast<double>(getY(bb.minCorner())) / COORD_SCALE;
    result["max_x"] = static_cast<double>(getX(bb.maxCorner())) / COORD_SCALE;
    result["max_y"] = static_cast<double>(getY(bb.maxCorner())) / COORD_SCALE;
    result["width"] = result["max_x"].cast<double>() - result["min_x"].cast<double>();
    result["height"] = result["max_y"].cast<double>() - result["min_y"].cast<double>();

    return result;
}

Point Shape::get_vertex(size_t index) const {
    if (index >= vertex_count()) {
        throw std::out_of_range("Vertex index out of range");
    }

    auto vertex = internal_item.vertex(index);
    return Point::from_libnest2d(vertex);
}

std::vector<Point> Shape::get_vertices() const {
    std::vector<Point> vertices;
    vertices.reserve(vertex_count());

    for (size_t i = 0; i < vertex_count(); ++i) {
        vertices.push_back(get_vertex(i));
    }

    return vertices;
}

Point Shape::reference_vertex() const {
    return Point::from_libnest2d(internal_item.referenceVertex());
}

Point Shape::rightmost_top_vertex() const {
    return Point::from_libnest2d(internal_item.rightmostTopVertex());
}

Point Shape::leftmost_bottom_vertex() const {
    return Point::from_libnest2d(internal_item.leftmostBottomVertex());
}

void Shape::translate(double x, double y) {
    internal_item.translate(static_cast<Coord>(x * COORD_SCALE),
                           static_cast<Coord>(y * COORD_SCALE));
}

void Shape::translate(const Point& delta) {
    translate(delta.x, delta.y);
}

void Shape::rotate(double angle_degrees) {
    double angle_rad = angle_degrees * M_PI / 180.0;
    internal_item.rotate(angle_rad);
}

void Shape::set_inflation(double distance) {
    internal_item.setInflation(static_cast<Coord>(distance * COORD_SCALE));
}

void Shape::inflate(double distance) {
    double current_inflation = get_inflation();
    set_inflation(current_inflation + distance);
}

double Shape::get_inflation() const {
    return static_cast<double>(internal_item.inflation()) / COORD_SCALE;
}

void Shape::set_sheet_id(int id) {
    internal_item.setSheetId(id);
}

int Shape::get_sheet_id() const {
    return internal_item.sheetId();
}

void Shape::set_priority(int priority) {
    internal_item.setPriority(priority);
}

int Shape::get_priority() const {
    return internal_item.priority();
}

bool Shape::is_fixed() const {
    return internal_item.isFixed();
}

void Shape::mark_as_fixed_in_sheet(int sheet_id) {
    internal_item.markAsFixedInSheet(sheet_id);
}

std::vector<std::vector<double>> Shape::get_transformed_shape() const {
    return get_raw_shape(); // For now, return raw shape - can be enhanced later
}

std::vector<std::vector<double>> Shape::get_raw_shape() const {
    std::vector<std::vector<double>> result;

    // Get contour
    auto contour = internal_item.rawShape();
    for (size_t i = 0; i < contour.size(); ++i) {
        auto vertex = contour[i];
        result.push_back({
            static_cast<double>(getX(vertex)) / COORD_SCALE,
            static_cast<double>(getY(vertex)) / COORD_SCALE
        });
    }

    return result;
}

std::vector<std::vector<double>> Shape::get_inflated_shape() const {
    // For now, return raw shape - inflation handling can be added later
    return get_raw_shape();
}

void Shape::reset_transformation() {
    internal_item.resetTransformation();
}

Point Shape::get_translation() const {
    auto trans = internal_item.translation();
    return Point(static_cast<double>(getX(trans)) / COORD_SCALE,
                 static_cast<double>(getY(trans)) / COORD_SCALE);
}

double Shape::get_rotation_degrees() const {
    return internal_item.rotation() * 180.0 / M_PI;
}

double Shape::get_rotation_radians() const {
    return internal_item.rotation();
}

bool Shape::is_point_inside(double x, double y) const {
    LibNest2DPoint point(static_cast<Coord>(x * COORD_SCALE),
                        static_cast<Coord>(y * COORD_SCALE));
    return internal_item.isInside(point);
}

bool Shape::is_point_inside(const Point& point) const {
    return is_point_inside(point.x, point.y);
}

bool Shape::intersects(const Shape& shape1, const Shape& shape2) {
    return libnest2d::Item::intersects(shape1.internal_item, shape2.internal_item);
}

bool Shape::touches(const Shape& shape1, const Shape& shape2) {
    return libnest2d::Item::touches(shape1.internal_item, shape2.internal_item);
}

std::string Shape::to_string() const {
    std::ostringstream oss;
    auto bb = bounding_box();
    oss << "Shape(vertices=" << vertex_count()
        << ", area=" << area()
        << ", bbox=" << bb["width"].cast<double>() << "x" << bb["height"].cast<double>()
        << ", holes=" << hole_count()
        << ", convex=" << (is_convex() ? "true" : "false") << ")";
    return oss.str();
}

} // namespace nest2d_wrapper
