#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>

#include <libnest2d/libnest2d.hpp>

#include "../tools/printer_parts.hpp"
#include "../tools/svgtools.hpp"


namespace py = pybind11;

using Point = libnest2d::Point;
using Box = libnest2d::Box;
using Item = libnest2d::Item;
using PackGroup = libnest2d::PackGroup;
using SVGWriter = libnest2d::svg::SVGWriter<libnest2d::PolygonImpl>;

// placers

using NfpPlacer = libnest2d::NfpPlacer;
using BottomLeftPlacer = libnest2d::BottomLeftPlacer;

// selectors

using FirstFitSelection = libnest2d::FirstFitSelection;
using DJDHeuristic  = libnest2d::DJDHeuristic;

// Create custom enums since they don't exist in the library
enum class PlacerType {
    NFP,
    BottomLeft
};

enum class SelectorType {
    FirstFit,
    DJDHeuristic
};

PYBIND11_MODULE(nest2D, m)
{
    m.doc() = "2D irregular bin packaging and nesting for python";

    // make enums for placers
    py::enum_<PlacerType>(m, "PlacerType", "Type of placer algorithm")
        .value("NFP", PlacerType::NFP)
        .value("BottomLeft", PlacerType::BottomLeft)
        .export_values();

    // make enums for selectors
    py::enum_<SelectorType>(m, "SelectorType", "Type of selector algorithm")
        .value("FirstFit", SelectorType::FirstFit)
        .value("DJDHeuristic", SelectorType::DJDHeuristic)
        .export_values();

    py::class_<Point>(m, "Point", "2D Point")
        .def(py::init<int, int>(),  py::arg("x"), py::arg("y"))
        //.def_property_readonly("x", &Point::X)
        .def_property_readonly("x", [](const Point &p) { return p.X; })
        .def_property_readonly("y", [](const Point &p) { return p.Y; })
        .def("__repr__",
             [](const Point &p) {
                 std::string r("Point(");
                 r += boost::lexical_cast<std::string>(p.X);
                 r += ", ";
                 r += boost::lexical_cast<std::string>(p.Y);
                 r += ")";
                 return r;
             }
        )
        .def("__eq__",
            [](const Point &p, const Point & q) {
                return p == q;
            }
        );

    // see lib/libnest2d/include/libnest2d/geometry_traits.hpp
    py::class_<Box>(m, "Box", "2D Box point pair")
        //.def(py::init<int, int>())
        // custom constructor to define box center
        .def(py::init([](int x, int y) {
            return std::unique_ptr<Box>(new Box(x, y, {x/2, y/2}));
        }))
        ;

    // Item is a shape defined by points
    // see lib/libnest2d/include/libnest2d/nester.hpp
    py::class_<Item>(m, "Item", "An item to be placed on a bin.")
        .def(py::init<std::vector<Point>>())
        .def("__repr__",
             [](const Item &i) {
                 std::string r("Item(area: ");
                 r += boost::lexical_cast<std::string>(i.area());
                 r += ", bin_id: ";
                 r += boost::lexical_cast<std::string>(i.binId());
                 r += ", vertices: ";
                 r += boost::lexical_cast<std::string>(i.vertexCount());
                 r += ")";
                 return r;
             }
        )
        .def("get_vertices",
             [](const Item &i) {
                 std::vector<Point> vertices;
                 auto& shape = i.transformedShape();
                 auto contour = libnest2d::shapelike::contour(shape);
                 for(auto& vertex : contour) {
                     vertices.push_back(vertex);
                 }
                 return vertices;
             }
        )
        ;

    // The nest function takes parameters input, box, placer_type, selector_type, and spacing
    // see lib/libnest2d/include/libnest2d/libnest2d.hpp
    m.def("nest", [](std::vector<Item>& input, const Box& box,
                     PlacerType placer_type,
                     SelectorType selector_type,
                     double spacing) -> py::object {

        PackGroup pgrp;
        size_t bins = 0;

        // Convert spacing to library units
        auto distance = libnest2d::mm(spacing);

        // Handle different placer and selector combinations with optimized configs
        if (placer_type == PlacerType::NFP) {
            if (selector_type == SelectorType::FirstFit) {
                // NFP placer with FirstFit selector
                libnest2d::NestConfig<NfpPlacer, FirstFitSelection> config;

                // Configure rotation angles for better nesting results
                config.placer_config.rotations = {};
                for (int angle = 0; angle < 360; angle += 1) { // 1-degree precision for better results
                    config.placer_config.rotations.push_back(angle);
                }

                // Maximize accuracy for best results and reduced calculation errors
                config.placer_config.accuracy = 0.98f;
                config.placer_config.parallel = true;
                config.placer_config.explore_holes = true;

                // Set alignment to bottom left
                config.placer_config.alignment = NfpPlacer::Config::Alignment::BOTTOM_LEFT;

                bins = libnest2d::nest<NfpPlacer, FirstFitSelection>(
                    input, box, distance, config);

            } else if (selector_type == SelectorType::DJDHeuristic) {
                // NFP placer with DJD selector
                libnest2d::NestConfig<NfpPlacer, DJDHeuristic> config;

                // Configure rotation angles for better calculations
                config.placer_config.rotations = {};
                for (int angle = 0; angle < 360; angle += 1) { // More precise rotation
                    config.placer_config.rotations.push_back(angle);
                }

                // Optimize for better calculations
                config.placer_config.accuracy = 0.98f;
                config.placer_config.parallel = true;
                config.placer_config.explore_holes = true;

                // Set alignment to bottom left
                config.placer_config.alignment = NfpPlacer::Config::Alignment::BOTTOM_LEFT;

                // Optimize DJD selector for better waste calculation
                config.selector_config.try_pairs = true;
                config.selector_config.try_triplets = true;
                config.selector_config.initial_fill_proportion = 0.4;
                config.selector_config.waste_increment = 0.05;
                config.selector_config.allow_parallel = true;
                config.selector_config.force_parallel = false;

                bins = libnest2d::nest<NfpPlacer, DJDHeuristic>(
                    input, box, distance, config);
            }
        } else if (placer_type == PlacerType::BottomLeft) {
            if (selector_type == SelectorType::FirstFit) {
                // BottomLeft placer with FirstFit selector
                libnest2d::NestConfig<BottomLeftPlacer, FirstFitSelection> config;

                bins = libnest2d::nest<BottomLeftPlacer, FirstFitSelection>(
                    input, box, distance, config);

            } else if (selector_type == SelectorType::DJDHeuristic) {
                // BottomLeft placer with DJD selector
                libnest2d::NestConfig<BottomLeftPlacer, DJDHeuristic> config;

                // Optimize DJD selector for better waste calculation accuracy
                config.selector_config.try_pairs = true;
                config.selector_config.try_triplets = true;
                config.selector_config.initial_fill_proportion = 0.35;
                config.selector_config.waste_increment = 0.05;
                config.selector_config.allow_parallel = true;
                config.selector_config.force_parallel = false;

                bins = libnest2d::nest<BottomLeftPlacer, DJDHeuristic>(
                    input, box, distance, config);
            }
        }

        // Create PackGroup from results
        pgrp = PackGroup(bins);
        for (Item &itm : input) {
            if (itm.binId() >= 0) pgrp[size_t(itm.binId())].emplace_back(itm);
        }

        return py::cast(pgrp);
    },
    py::arg("input"),
    py::arg("box"),
    py::arg("placer_type") = PlacerType::NFP,
    py::arg("selector_type") = SelectorType::DJDHeuristic,
    py::arg("spacing") = 0.0,
    "Nest and pack the input items into the box bin with specified algorithms and spacing."
    )
        ;

    py::class_<SVGWriter>(m, "SVGWriter", "SVGWriter tools to write pack_group to SVG.")
        .def(py::init([]() {
            // custom constructor
            SVGWriter::Config conf;
            conf.mm_in_coord_units = libnest2d::mm();
            return std::unique_ptr<SVGWriter>(new SVGWriter(conf));
        }))
        .def("write_packgroup", [](SVGWriter & sw, const PackGroup & pgrp) {
            sw.setSize(Box(libnest2d::mm(250), libnest2d::mm(210)));  // TODO make own call
            sw.writePackGroup(pgrp);
        })
        .def("save", [](SVGWriter & sw) {
            sw.save("out");
        })
        .def("__repr__",
             [](const SVGWriter &sw) {
                 std::string r("SVGWriter(");
                 r += ")";
                 return r;
             }
        );

}
