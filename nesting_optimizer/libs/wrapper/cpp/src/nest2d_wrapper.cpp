#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <libnest2d/libnest2d.hpp>

namespace py = pybind11;

using namespace libnest2d;
using Polygon = PolygonImpl;

// Simple test function (keep for backward compatibility)
int add(int a, int b) {
    return a * b;
}

// Create a polygon from a list of 2D points
Polygon create_polygon(const std::vector<std::vector<double>>& points) {
    Polygon polygon;
    auto& contour = polygon.Contour;
    for (const auto& point : points) {
        if (point.size() >= 2) {
            contour.push_back(PointImpl(
                static_cast<ClipperLib::cInt>(point[0] * 1000000),
                static_cast<ClipperLib::cInt>(point[1] * 1000000)
            ));
        }
    }
    return polygon;
}

// Convert polygon back to list of points
std::vector<std::vector<double>> polygon_to_points(const Polygon& polygon) {
    std::vector<std::vector<double>> points;
    for (const auto& pt : polygon.Contour) {
        points.push_back({
            static_cast<double>(pt.X) / 1000000.0,
            static_cast<double>(pt.Y) / 1000000.0
        });
    }
    return points;
}

// Calculate polygon area
double polygon_area(const std::vector<std::vector<double>>& points) {
    Polygon poly = create_polygon(points);
    return static_cast<double>(ClipperLib::Area(poly.Contour)) / 1000000000000.0; // Convert from scaled units
}

// Calculate polygon bounding box
py::dict polygon_bounds(const std::vector<std::vector<double>>& points) {
    Polygon poly = create_polygon(points);

    if (poly.Contour.empty()) {
        py::dict bounds;
        bounds["min_x"] = 0.0;
        bounds["min_y"] = 0.0;
        bounds["max_x"] = 0.0;
        bounds["max_y"] = 0.0;
        bounds["width"] = 0.0;
        bounds["height"] = 0.0;
        return bounds;
    }

    ClipperLib::cInt min_x = poly.Contour[0].X;
    ClipperLib::cInt max_x = poly.Contour[0].X;
    ClipperLib::cInt min_y = poly.Contour[0].Y;
    ClipperLib::cInt max_y = poly.Contour[0].Y;

    for (const auto& pt : poly.Contour) {
        if (pt.X < min_x) min_x = pt.X;
        if (pt.X > max_x) max_x = pt.X;
        if (pt.Y < min_y) min_y = pt.Y;
        if (pt.Y > max_y) max_y = pt.Y;
    }

    py::dict bounds;
    bounds["min_x"] = static_cast<double>(min_x) / 1000000.0;
    bounds["min_y"] = static_cast<double>(min_y) / 1000000.0;
    bounds["max_x"] = static_cast<double>(max_x) / 1000000.0;
    bounds["max_y"] = static_cast<double>(max_y) / 1000000.0;
    bounds["width"] = static_cast<double>(max_x - min_x) / 1000000.0;
    bounds["height"] = static_cast<double>(max_y - min_y) / 1000000.0;

    return bounds;
}

// Check if point is inside polygon (simplified version)
bool point_in_polygon(const std::vector<std::vector<double>>& polygon_points,
                     double x, double y) {
    Polygon poly = create_polygon(polygon_points);
    PointImpl point(
        static_cast<ClipperLib::cInt>(x * 1000000),
        static_cast<ClipperLib::cInt>(y * 1000000)
    );

    // Simple point-in-polygon test using ClipperLib
    return ClipperLib::PointInPolygon(point, poly.Contour) != 0;
}

// Simplified nesting function using basic placement
py::dict nest_polygons_simple(const std::vector<std::vector<std::vector<double>>>& polygon_data,
                             double sheet_width, double sheet_height,
                             double spacing = 0.0) {

    // Convert input polygons to Items
    std::vector<Item> items;
    for (const auto& poly_points : polygon_data) {
        Polygon poly = create_polygon(poly_points);
        items.emplace_back(std::move(poly));
    }

    // Create sheet
    Box sheet(static_cast<Coord>(sheet_width * 1000000), static_cast<Coord>(sheet_height * 1000000));

    // Use BottomLeftPlacer with FirstFitSelection for simplicity
    using Placer = BottomLeftPlacer;
    using Selector = FirstFitSelection;

    // Create and execute nester with proper constructor
    _Nester<Placer, Selector> nester(sheet, static_cast<Coord>(spacing * 1000000));
    size_t sheets_used = nester.execute(items.begin(), items.end());

    // Extract results
    std::vector<py::dict> nested_items;
    std::vector<std::vector<std::vector<double>>> nested_polygons;
    std::vector<std::vector<double>> positions;
    std::vector<double> rotations;

    for (size_t i = 0; i < items.size(); ++i) {
        const auto& item = items[i];

        // Get polygon points
        nested_polygons.push_back(polygon_to_points(item.rawShape()));

        // Get translation
        auto translation = item.translation();
        positions.push_back({
            static_cast<double>(translation.X) / 1000000.0,
            static_cast<double>(translation.Y) / 1000000.0
        });

        // Get rotation
        rotations.push_back(static_cast<double>(item.rotation()));

        // Create item dict
        py::dict item_dict;
        item_dict["polygon"] = polygon_to_points(item.rawShape());
        item_dict["position"] = std::vector<double>{
            static_cast<double>(translation.X) / 1000000.0,
            static_cast<double>(translation.Y) / 1000000.0
        };
        item_dict["rotation"] = static_cast<double>(item.rotation());
        item_dict["bin_id"] = item.binId(); // Keep bin_id for API compatibility

        nested_items.push_back(item_dict);
    }

    // Return result dictionary
    py::dict result;
    result["items"] = nested_items;
    result["bins_used"] = sheets_used; // Keep bins_used for API compatibility
    result["polygons"] = nested_polygons;
    result["positions"] = positions;
    result["rotations"] = rotations;
    result["success"] = true;

    return result;
}

PYBIND11_MODULE(nest2d_wrapper, m) {
    m.doc() = "LibNest2D Python Wrapper - Nesting Optimizer C++ Engine Module";

    // Expose Radians type
    py::class_<Radians>(m, "Radians")
        .def(py::init<double>())
        .def("__float__", [](const Radians& r) { return static_cast<double>(r); });

    // Legacy test function
    m.def("add", &add, "A function that multiplies two numbers (legacy test)");

    // Main nesting function
    m.def("nest_polygons", &nest_polygons_simple,
          "Nest a list of polygons on material sheets using basic bottom-left placement",
          py::arg("polygons"), py::arg("sheet_width"), py::arg("sheet_height"),
          py::arg("spacing") = 0.0);

    // Utility functions
    m.def("polygon_area", &polygon_area,
          "Calculate the area of a polygon",
          py::arg("points"));

    m.def("polygon_bounds", &polygon_bounds,
          "Get bounding box of a polygon",
          py::arg("points"));

    m.def("point_in_polygon", &point_in_polygon,
          "Check if a point is inside a polygon",
          py::arg("polygon"), py::arg("x"), py::arg("y"));
}
