/*
 * Coordinate System
 * Binds the core coordinate types and unit conversion functions
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <libnest2d/libnest2d.hpp>
#include <libnest2d/backends/clipper/geometries.hpp>
#include <clipper.hpp>  // For ClipperLib::cInt type

namespace py = pybind11;

/**
 * Bind the coordinate system to Python
 * This includes:
 * - Coord type (the basic coordinate integer type)
 * - mm() function (convert millimeters to internal units)
 * - coord_to_mm() function (convert internal units back to millimeters)
 * - MM_IN_COORDS constant (scale factor)
 */
void bind_coordinate(py::module& m) {

    // =============================================================================
    // COORDINATE TYPE BINDING
    // =============================================================================

    // Since libnest2d::Coord is just a typedef for ClipperLib::cInt (which is a primitive type),
    // we cannot bind it as a class. Instead, we create a simple wrapper class.
    struct Coordinate {
        libnest2d::Coord value;

        Coordinate() : value(0) {}
        Coordinate(libnest2d::Coord v) : value(v) {}
        Coordinate(int v) : value(static_cast<libnest2d::Coord>(v)) {}

        operator libnest2d::Coord() const { return value; }
        operator double() const { return static_cast<double>(value); }

        // Arithmetic operators
        Coordinate operator+(const Coordinate& other) const { return Coordinate(value + other.value); }
        Coordinate operator-(const Coordinate& other) const { return Coordinate(value - other.value); }
        Coordinate operator*(const Coordinate& other) const { return Coordinate(value * other.value); }
        Coordinate operator/(const Coordinate& other) const { return Coordinate(value / other.value); }

        // Unary operators
        Coordinate operator-() const { return Coordinate(-value); }

        // Comparison operators
        bool operator==(const Coordinate& other) const { return value == other.value; }
        bool operator!=(const Coordinate& other) const { return value != other.value; }
        bool operator<(const Coordinate& other) const { return value < other.value; }
        bool operator<=(const Coordinate& other) const { return value <= other.value; }
        bool operator>(const Coordinate& other) const { return value > other.value; }
        bool operator>=(const Coordinate& other) const { return value >= other.value; }
    };

    py::class_<Coordinate>(m, "Coord",
        "Basic coordinate type used internally by libnest2d.\n"
        "This is a 64-bit integer that represents coordinates with high precision.\n"
        "1 millimeter = 1,000,000 coordinate units for nanometer precision.")

        // Constructors
        .def(py::init<>(), "Create coordinate with value 0")
        .def(py::init<libnest2d::Coord>(), "Create coordinate from coordinate value", py::arg("value"))
        .def(py::init<int>(), "Create coordinate from int value", py::arg("value"))

        // Make it convertible to/from Python int
        .def("__int__", [](const Coordinate& c) { return static_cast<long long>(c.value); })
        .def("__float__", [](const Coordinate& c) { return static_cast<double>(c); })

        // Basic arithmetic operations
        .def("__add__", [](const Coordinate& a, const Coordinate& b) { return a + b; })
        .def("__sub__", [](const Coordinate& a, const Coordinate& b) { return a - b; })
        .def("__mul__", [](const Coordinate& a, const Coordinate& b) { return a * b; })
        .def("__floordiv__", [](const Coordinate& a, const Coordinate& b) { return a / b; })
        .def("__neg__", [](const Coordinate& c) { return -c; })

        // Mixed-type arithmetic operations (Coord vs int/float)
        .def("__add__", [](const Coordinate& a, long long b) { return Coordinate(a.value + b); })
        .def("__sub__", [](const Coordinate& a, long long b) { return Coordinate(a.value - b); })
        .def("__mul__", [](const Coordinate& a, long long b) { return Coordinate(a.value * b); })
        .def("__floordiv__", [](const Coordinate& a, long long b) { return Coordinate(a.value / b); })

        .def("__add__", [](const Coordinate& a, double b) { return Coordinate(a.value + static_cast<libnest2d::Coord>(b)); })
        .def("__sub__", [](const Coordinate& a, double b) { return Coordinate(a.value - static_cast<libnest2d::Coord>(b)); })
        .def("__mul__", [](const Coordinate& a, double b) { return Coordinate(static_cast<libnest2d::Coord>(a.value * b)); })
        .def("__floordiv__", [](const Coordinate& a, double b) { return Coordinate(static_cast<libnest2d::Coord>(a.value / b)); })

        // Reverse operations (int/float vs Coord)
        .def("__radd__", [](const Coordinate& a, long long b) { return Coordinate(b + a.value); })
        .def("__rsub__", [](const Coordinate& a, long long b) { return Coordinate(b - a.value); })
        .def("__rmul__", [](const Coordinate& a, long long b) { return Coordinate(b * a.value); })
        .def("__rfloordiv__", [](const Coordinate& a, long long b) { return Coordinate(b / a.value); })

        // Comparison operations
        .def("__eq__", [](const Coordinate& a, const Coordinate& b) { return a == b; })
        .def("__ne__", [](const Coordinate& a, const Coordinate& b) { return a != b; })
        .def("__lt__", [](const Coordinate& a, const Coordinate& b) { return a < b; })
        .def("__le__", [](const Coordinate& a, const Coordinate& b) { return a <= b; })
        .def("__gt__", [](const Coordinate& a, const Coordinate& b) { return a > b; })
        .def("__ge__", [](const Coordinate& a, const Coordinate& b) { return a >= b; })

        // Mixed-type comparison operations (Coord vs int/float)
        .def("__eq__", [](const Coordinate& a, long long b) { return a.value == b; })
        .def("__ne__", [](const Coordinate& a, long long b) { return a.value != b; })
        .def("__lt__", [](const Coordinate& a, long long b) { return a.value < b; })
        .def("__le__", [](const Coordinate& a, long long b) { return a.value <= b; })
        .def("__gt__", [](const Coordinate& a, long long b) { return a.value > b; })
        .def("__ge__", [](const Coordinate& a, long long b) { return a.value >= b; })

        .def("__eq__", [](const Coordinate& a, double b) { return static_cast<double>(a.value) == b; })
        .def("__ne__", [](const Coordinate& a, double b) { return static_cast<double>(a.value) != b; })
        .def("__lt__", [](const Coordinate& a, double b) { return static_cast<double>(a.value) < b; })
        .def("__le__", [](const Coordinate& a, double b) { return static_cast<double>(a.value) <= b; })
        .def("__gt__", [](const Coordinate& a, double b) { return static_cast<double>(a.value) > b; })
        .def("__ge__", [](const Coordinate& a, double b) { return static_cast<double>(a.value) >= b; })

        // String representation
        .def("__repr__", [](const Coordinate& c) {
            return "Coord(" + std::to_string(c.value) + ")";
        })
        .def("__str__", [](const Coordinate& c) {
            return std::to_string(c.value);
        })

        // Access to the underlying value
        .def_readwrite("value", &Coordinate::value);

    // =============================================================================
    // UNIT CONVERSION CONSTANTS
    // =============================================================================

    // Expose the scale factor constant
    constexpr auto MM_IN_COORDS_VALUE = 1000000;
    m.attr("MM_IN_COORDS") = MM_IN_COORDS_VALUE;

    // =============================================================================
    // UNIT CONVERSION FUNCTIONS
    // =============================================================================

    // Convert millimeters to internal coordinate units
    m.def("mm", [](double value) -> Coordinate {
        return Coordinate(libnest2d::mm(value));
    },
    "Convert millimeters to internal coordinate units.\n\n"
    "Args:\n"
    "    value (float): Value in millimeters\n\n"
    "Returns:\n"
    "    Coord: Internal coordinate units (value * 1,000,000)\n\n"
    "Example:\n"
    "    >>> coord = mm(10.5)  # 10.5 millimeters\n"
    "    >>> print(coord)      # 10500000 internal units",
    py::arg("value"));

    // Also bind integer version
    m.def("mm", [](int value) -> Coordinate {
        return Coordinate(libnest2d::mm(value));
    },
    "Convert millimeters to internal coordinate units.\n\n"
    "Args:\n"
    "    value (int): Value in millimeters\n\n"
    "Returns:\n"
    "    Coord: Internal coordinate units (value * 1,000,000)",
    py::arg("value"));

    // Convert internal coordinate units back to millimeters
    m.def("coord_to_mm", [](const Coordinate& coord_value) -> double {
        return static_cast<double>(coord_value.value) / MM_IN_COORDS_VALUE;
    },
    "Convert internal coordinate units back to millimeters.\n\n"
    "Args:\n"
    "    coord_value (Coord): Internal coordinate units\n\n"
    "Returns:\n"
    "    float: Value in millimeters\n\n"
    "Example:\n"
    "    >>> coord = Coord(1000000)\n"
    "    >>> mm_val = coord_to_mm(coord)\n"
    "    >>> print(mm_val)  # 1.0",
    py::arg("coord_value"));

    // =============================================================================
    // CONVENIENCE FUNCTIONS
    // =============================================================================

    // Quick coordinate creation from common units
    m.def("from_mm", [](double mm_value) -> Coordinate {
        return Coordinate(libnest2d::mm(mm_value));
    }, "Alias for mm() function", py::arg("mm_value"));

    m.def("from_cm", [](double cm_value) -> Coordinate {
        return Coordinate(libnest2d::mm(cm_value * 10.0));
    }, "Convert centimeters to internal coordinate units", py::arg("cm_value"));

    m.def("from_inches", [](double inch_value) -> Coordinate {
        return Coordinate(libnest2d::mm(inch_value * 25.4));
    }, "Convert inches to internal coordinate units", py::arg("inch_value"));
}
