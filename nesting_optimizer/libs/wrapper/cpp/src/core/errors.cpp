#include "../../include/core/errors.hpp"
#include "../../include/core/config.hpp"
#include <sstream>

namespace nest2d_wrapper {

NestingError::NestingError(const std::string& message)
    : std::runtime_error(message), error_code_(ErrorCode::UNKNOWN), message_(message) {}

NestingError::NestingError(ErrorCode code, const std::string& message)
    : std::runtime_error(message), error_code_(code), message_(message) {}

std::string NestingError::get_error_details() const {
    std::ostringstream oss;
    oss << "NestingError [Code: " << static_cast<int>(error_code_) << "] " << message_;
    return oss.str();
}

ConfigurationError::ConfigurationError(const std::string& message)
    : NestingError(ErrorCode::CONFIGURATION_ERROR, "Configuration Error: " + message) {}

GeometryError::GeometryError(const std::string& message)
    : NestingError(ErrorCode::GEOMETRY_ERROR, "Geometry Error: " + message) {}

OptimizationError::OptimizationError(const std::string& message)
    : NestingError(ErrorCode::OPTIMIZATION_ERROR, "Optimization Error: " + message) {}

MemoryError::MemoryError(const std::string& message)
    : NestingError(ErrorCode::MEMORY_ERROR, "Memory Error: " + message) {}

IOError::IOError(const std::string& message)
    : NestingError(ErrorCode::IO_ERROR, "IO Error: " + message) {}

BackendError::BackendError(const std::string& message)
    : NestingError(ErrorCode::BACKEND_ERROR, "Backend Error: " + message) {}

// Error handling utilities
void throw_if_invalid_config(const NestConfig& config) {
    if (!config.validate()) {
        auto errors = config.get_validation_errors();
        std::ostringstream oss;
        oss << "Invalid configuration: ";
        for (size_t i = 0; i < errors.size(); ++i) {
            if (i > 0) oss << "; ";
            oss << errors[i];
        }
        throw ConfigurationError(oss.str());
    }
}

void throw_if_invalid_polygon(const std::vector<std::vector<double>>& polygon) {
    if (polygon.size() < 3) {
        throw GeometryError("Polygon must have at least 3 vertices");
    }

    for (const auto& point : polygon) {
        if (point.size() < 2) {
            throw GeometryError("Each point must have at least 2 coordinates");
        }
    }

    // Check for degenerate polygon (zero area)
    double area = 0.0;
    size_t n = polygon.size();
    for (size_t i = 0; i < n; ++i) {
        size_t j = (i + 1) % n;
        area += polygon[i][0] * polygon[j][1] - polygon[j][0] * polygon[i][1];
    }

    if (std::abs(area) < 1e-10) {
        throw GeometryError("Polygon has zero or near-zero area");
    }
}

void throw_if_shapes_empty(const std::vector<Shape>& shapes) {
    if (shapes.empty()) {
        throw ConfigurationError("Cannot nest empty list of shapes");
    }
}

void throw_if_sheet_too_small(const Sheet& sheet) {
    if (sheet.width <= 0 || sheet.height <= 0) {
        throw ConfigurationError("Sheet dimensions must be positive");
    }
}

} // namespace nest2d_wrapper
