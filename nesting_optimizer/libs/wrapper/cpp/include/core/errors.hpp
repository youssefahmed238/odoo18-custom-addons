#ifndef NEST2D_ERRORS_HPP
#define NEST2D_ERRORS_HPP

#include <stdexcept>
#include <string>
#include <vector>

namespace nest2d_wrapper {

// Forward declaration
class NestConfig;

/**
 * Custom exception classes for better error handling
 */
class NestingException : public std::runtime_error {
public:
    explicit NestingException(const std::string& message)
        : std::runtime_error("NestingException: " + message) {}
};

class ConfigurationException : public std::runtime_error {
public:
    explicit ConfigurationException(const std::string& message)
        : std::runtime_error("ConfigurationException: " + message) {}
};

class GeometryException : public std::runtime_error {
public:
    explicit GeometryException(const std::string& message)
        : std::runtime_error("GeometryException: " + message) {}
};

class ValidationException : public std::runtime_error {
public:
    explicit ValidationException(const std::string& message)
        : std::runtime_error("ValidationException: " + message) {}
};

/**
 * Error handling utilities
 */
class ErrorHandler {
public:
    static void validate_polygon(const std::vector<std::vector<double>>& points) {
        if (points.size() < 3) {
            throw GeometryException("Polygon must have at least 3 points");
        }

        for (const auto& point : points) {
            if (point.size() != 2) {
                throw GeometryException("Each point must have exactly 2 coordinates");
            }
        }
    }

    static void validate_sheet(double width, double height) {
        if (width <= 0.0 || height <= 0.0) {
            throw ValidationException("Sheet dimensions must be positive");
        }
    }

    static void validate_spacing(double spacing) {
        if (spacing < 0.0) {
            throw ValidationException("Spacing must be non-negative");
        }
    }

    static void validate_rotations(const std::vector<double>& rotations) {
        if (rotations.empty()) {
            throw ValidationException("At least one rotation angle must be provided");
        }
    }

    static void validate_config(const NestConfig& config) {
        if (config.placer_type != "nfp" && config.placer_type != "bottom_left") {
            throw ConfigurationException("Invalid placer type: " + config.placer_type);
        }

        if (config.accuracy < 0.0f || config.accuracy > 1.0f) {
            throw ConfigurationException("Accuracy must be between 0.0 and 1.0");
        }

        validate_spacing(config.spacing);
        validate_rotations(config.rotations);
    }
};

} // namespace nest2d_wrapper

#endif // NEST2D_ERRORS_HPP
