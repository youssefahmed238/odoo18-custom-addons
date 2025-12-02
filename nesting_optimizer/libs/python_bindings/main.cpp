/*
 * LibNest2D Python Bindings - Main Module Entry Point
 * This file serves as the central registry for all Python bindings
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include <libnest2d/libnest2d.hpp>

namespace py = pybind11;

// Forward declarations for binding functions
// Each component will have its own binding function in separate files
void bind_coordinate(py::module& m);

/**
 * Main pybind11 module definition
 * This creates the Python module that users will import
 */
PYBIND11_MODULE(nest2d, m) {
    m.doc() = "LibNest2D Python Bindings - 2D Bin Packing/Nesting Library";
    m.attr("__version__") = "1.0.0";

    // Coordinate system - this must come first as everything depends on it
    bind_coordinate(m);
}


