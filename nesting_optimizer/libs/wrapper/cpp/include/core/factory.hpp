#ifndef NEST2D_FACTORY_HPP
#define NEST2D_FACTORY_HPP

#include "../core/config.hpp"
#include "../geometry/shape.hpp"
#include "../geometry/sheet.hpp"
#include "../geometry/rectangle.hpp"
#include "../geometry/circle.hpp"
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace nest2d_wrapper {

/**
 * Factory class for creating pre-configured nesting setups
 */
class NestFactory {
public:
    // Preset configurations
    // Enhanced configuration presets
    static NestConfig create_fast_config() {
        NestConfig config;
        config.placer_type = "bottom_left";
        config.accuracy = 0.3f;
        config.parallel = true;
        config.rotations = {0.0}; // No rotation for speed
        config.selector_type = "firstfit";
        return config;
    }

    static NestConfig create_quality_config() {
        NestConfig config;
        config.placer_type = "nfp";
        config.accuracy = 0.95f;
        config.parallel = true;
        config.explore_holes = true;
        config.rotations = {0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0};
        config.selector_type = "djd";
        return config;
    }

    static NestConfig create_balanced_config() {
        NestConfig config;
        config.placer_type = "nfp";
        config.accuracy = 0.65f;
        config.parallel = true;
        config.rotations = {0.0, 90.0, 180.0, 270.0};
        config.selector_type = "firstfit";
        return config;
    }

    // Industry-specific configurations
    static NestConfig create_metal_cutting_config() {
        NestConfig config;
        config.placer_type = "nfp";
        config.accuracy = 0.9f;
        config.parallel = true;
        config.explore_holes = true;
        config.rotations = {0.0, 90.0, 180.0, 270.0};
        config.selector_type = "djd";
        config.spacing = 2.0; // Kerf width consideration
        return config;
    }

    static NestConfig create_custom_config(
        const std::string& placer = "nfp",
        float accuracy = 0.65f,
        const std::vector<double>& rotations = {0.0, 90.0, 180.0, 270.0},
        const std::string& selector = "firstfit",
        double spacing = 0.0) {

        NestConfig config;
        config.placer_type = placer;
        config.accuracy = accuracy;
        config.rotations = rotations;
        config.selector_type = selector;
        config.spacing = spacing;
        return config;
    }

    // Enhanced shape factory methods
    static Shape create_rectangle(double width, double height) {
        std::vector<std::vector<double>> points = {
            {0, 0}, {width, 0}, {width, height}, {0, height}
        };
        return Shape(points);
    }

    static Shape create_circle(double radius, int segments = 32) {
        std::vector<std::vector<double>> points;
        points.reserve(segments);
        for (int i = 0; i < segments; ++i) {
            double angle = 2.0 * M_PI * i / segments;
            points.push_back({radius * std::cos(angle), radius * std::sin(angle)});
        }
        return Shape(points);
    }

    static Shape create_regular_polygon(double radius, int sides) {
        std::vector<std::vector<double>> points;
        points.reserve(sides);
        for (int i = 0; i < sides; ++i) {
            double angle = 2.0 * M_PI * i / sides;
            points.push_back({radius * std::cos(angle), radius * std::sin(angle)});
        }
        return Shape(points);
    }

    static Shape create_l_shape(double width, double height, double notch_width, double notch_height) {
        std::vector<std::vector<double>> points = {
            {0, 0},
            {width, 0},
            {width, notch_height},
            {notch_width, notch_height},
            {notch_width, height},
            {0, height}
        };
        return Shape(points);
    }

    // Enhanced validation utilities
    static bool validate_config(const NestConfig& config) {
        if (config.placer_type != "nfp" && config.placer_type != "bottom_left") {
            return false;
        }
        if (config.accuracy < 0.0f || config.accuracy > 1.0f) {
            return false;
        }
        if (config.spacing < 0.0) {
            return false;
        }
        if (config.selector_type != "firstfit" &&
            config.selector_type != "filler" &&
            config.selector_type != "djd") {
            return false;
        }
        return true;
    }

    static bool validate_sheet(const Sheet& sheet) {
        return sheet.width > 0.0 && sheet.height > 0.0;
    }
};

} // namespace nest2d_wrapper

#endif // NEST2D_FACTORY_HPP
