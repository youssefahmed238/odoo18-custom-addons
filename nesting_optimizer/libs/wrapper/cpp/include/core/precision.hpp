#ifndef NEST2D_PRECISION_HPP
#define NEST2D_PRECISION_HPP

#include "types.hpp"
#include <pybind11/pybind11.h>
#include <vector>
#include <cmath>
#include <limits>
#include <string>

// Include LibNest2D precision utilities if available
#ifdef LIBNEST2D_USE_BIGINT
#include <libnest2d/utils/bigint.hpp>
#endif

#ifdef LIBNEST2D_USE_RATIONAL
#include <libnest2d/utils/rational.hpp>
#endif

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Precision configuration for high-accuracy calculations
 */
class PrecisionConfig {
public:
    enum class PrecisionLevel {
        STANDARD,      // Standard double precision
        HIGH,          // Extended precision where available
        EXACT          // Rational arithmetic (if available)
    };

    PrecisionLevel level = PrecisionLevel::STANDARD;
    double tolerance = 1e-9;
    bool use_rational_arithmetic = false;
    int decimal_precision = 15; // For string conversions
    bool snap_to_grid = false;
    double grid_size = 1e-6;

    PrecisionConfig() = default;
    PrecisionConfig(PrecisionLevel l, double tol = 1e-9)
        : level(l), tolerance(tol) {}

    static PrecisionConfig create_standard() {
        return PrecisionConfig(PrecisionLevel::STANDARD, 1e-9);
    }

    static PrecisionConfig create_high_precision() {
        PrecisionConfig config(PrecisionLevel::HIGH, 1e-12);
        config.decimal_precision = 20;
        return config;
    }

    static PrecisionConfig create_exact() {
        PrecisionConfig config(PrecisionLevel::EXACT, 0.0);
        config.use_rational_arithmetic = true;
        config.decimal_precision = 25;
        return config;
    }

    std::string to_string() const {
        std::string level_str;
        switch (level) {
            case PrecisionLevel::STANDARD: level_str = "STANDARD"; break;
            case PrecisionLevel::HIGH: level_str = "HIGH"; break;
            case PrecisionLevel::EXACT: level_str = "EXACT"; break;
        }
        return "PrecisionConfig(level=" + level_str +
               ", tolerance=" + std::to_string(tolerance) + ")";
    }
};

/**
 * High-precision numeric type wrapper
 */
class PrecisionNumber {
private:
    double value_;
    bool is_exact_;
    std::string exact_representation_; // For rational numbers

public:
    PrecisionNumber(double val = 0.0) : value_(val), is_exact_(false) {}
    PrecisionNumber(const std::string& exact_val)
        : value_(std::stod(exact_val)), is_exact_(true), exact_representation_(exact_val) {}

    double to_double() const { return value_; }
    std::string to_string(int precision = 15) const;
    bool is_exact() const { return is_exact_; }

    // Arithmetic operations
    PrecisionNumber operator+(const PrecisionNumber& other) const;
    PrecisionNumber operator-(const PrecisionNumber& other) const;
    PrecisionNumber operator*(const PrecisionNumber& other) const;
    PrecisionNumber operator/(const PrecisionNumber& other) const;

    bool operator==(const PrecisionNumber& other) const;
    bool operator<(const PrecisionNumber& other) const;
    bool equals(const PrecisionNumber& other, double tolerance) const;
};

/**
 * High-precision geometric calculations
 */
class HighPrecisionGeometry {
public:
    /**
     * Calculate polygon area with high precision
     */
    static PrecisionNumber calculate_precise_area(const std::vector<std::vector<double>>& points,
                                                 const PrecisionConfig& config = PrecisionConfig());

    /**
     * Calculate distance between points with high precision
     */
    static PrecisionNumber calculate_precise_distance(const std::vector<double>& p1,
                                                     const std::vector<double>& p2,
                                                     const PrecisionConfig& config = PrecisionConfig());

    /**
     * Determine if point is inside polygon with high precision
     */
    static bool precise_point_in_polygon(const std::vector<std::vector<double>>& polygon,
                                        const std::vector<double>& point,
                                        const PrecisionConfig& config = PrecisionConfig());

    /**
     * Calculate polygon intersection with high precision
     */
    static std::vector<std::vector<std::vector<double>>> precise_intersection(
        const std::vector<std::vector<double>>& poly1,
        const std::vector<std::vector<double>>& poly2,
        const PrecisionConfig& config = PrecisionConfig());

    /**
     * Snap coordinates to precision grid
     */
    static std::vector<std::vector<double>> snap_to_precision_grid(
        const std::vector<std::vector<double>>& points,
        double grid_size);

    /**
     * Remove degeneracies with precision tolerance
     */
    static std::vector<std::vector<double>> remove_degeneracies(
        const std::vector<std::vector<double>>& points,
        const PrecisionConfig& config = PrecisionConfig());

    /**
     * Robust orientation test
     */
    enum class Orientation { CLOCKWISE, COUNTERCLOCKWISE, COLLINEAR };
    static Orientation robust_orientation(const std::vector<double>& p,
                                         const std::vector<double>& q,
                                         const std::vector<double>& r,
                                         const PrecisionConfig& config = PrecisionConfig());

    /**
     * Calculate signed area with precision control
     */
    static PrecisionNumber signed_area_precise(const std::vector<std::vector<double>>& points,
                                              const PrecisionConfig& config = PrecisionConfig());
};

/**
 * Exact arithmetic wrapper (when rational arithmetic is available)
 */
class ExactArithmetic {
public:
    /**
     * Convert double to exact representation
     */
    static std::string double_to_exact(double value, int max_denominator = 1000000);

    /**
     * Perform exact calculations on coordinates
     */
    static py::dict exact_polygon_operations(const std::vector<std::vector<double>>& points,
                                            const std::string& operation);

    /**
     * Compare two values exactly
     */
    static bool exact_equal(double a, double b, const std::string& tolerance_str = "0");

    /**
     * Exact intersection calculation
     */
    static py::dict exact_line_intersection(const std::vector<double>& line1_start,
                                           const std::vector<double>& line1_end,
                                           const std::vector<double>& line2_start,
                                           const std::vector<double>& line2_end);
};

/**
 * Numerical stability utilities
 */
class NumericalStability {
public:
    /**
     * Analyze numerical stability of polygon operations
     */
    static py::dict analyze_stability(const std::vector<std::vector<double>>& points);

    /**
     * Suggest precision improvements
     */
    static py::dict suggest_precision_improvements(const std::vector<std::vector<double>>& points);

    /**
     * Detect potential numerical issues
     */
    static py::list detect_numerical_issues(const std::vector<std::vector<double>>& points,
                                           double tolerance = 1e-12);

    /**
     * Improve polygon for better numerical stability
     */
    static std::vector<std::vector<double>> improve_numerical_stability(
        const std::vector<std::vector<double>>& points,
        const PrecisionConfig& config = PrecisionConfig());

    /**
     * Calculate condition number for geometric operation
     */
    static double calculate_condition_number(const std::vector<std::vector<double>>& points);

    /**
     * Recommend coordinate scaling for better precision
     */
    static py::dict recommend_coordinate_scaling(const std::vector<std::vector<double>>& points);
};

/**
 * Precision-aware coordinate transformations
 */
class PreciseTransforms {
public:
    /**
     * High-precision rotation
     */
    static std::vector<std::vector<double>> precise_rotate(
        const std::vector<std::vector<double>>& points,
        double angle_degrees,
        const PrecisionConfig& config = PrecisionConfig());

    /**
     * High-precision translation
     */
    static std::vector<std::vector<double>> precise_translate(
        const std::vector<std::vector<double>>& points,
        double dx, double dy,
        const PrecisionConfig& config = PrecisionConfig());

    /**
     * High-precision scaling
     */
    static std::vector<std::vector<double>> precise_scale(
        const std::vector<std::vector<double>>& points,
        double scale_x, double scale_y,
        const PrecisionConfig& config = PrecisionConfig());

    /**
     * High-precision matrix transformation
     */
    static std::vector<std::vector<double>> precise_transform_matrix(
        const std::vector<std::vector<double>>& points,
        const std::vector<std::vector<double>>& transformation_matrix,
        const PrecisionConfig& config = PrecisionConfig());
};

} // namespace nest2d_wrapper

#endif // NEST2D_PRECISION_HPP
