#include "../../include/core/factory.hpp"
#include "../../include/core/errors.hpp"
#include <stdexcept>

namespace nest2d_wrapper {

// Shape factory implementations
std::unique_ptr<Shape> ShapeFactory::create_rectangle(double width, double height) {
    if (width <= 0 || height <= 0) {
        throw GeometryError("Rectangle dimensions must be positive");
    }
    return std::make_unique<Shape>(Shape::create_rectangle(width, height));
}

std::unique_ptr<Shape> ShapeFactory::create_circle(double radius, int segments) {
    if (radius <= 0) {
        throw GeometryError("Circle radius must be positive");
    }
    if (segments < 3) {
        throw GeometryError("Circle must have at least 3 segments");
    }
    return std::make_unique<Shape>(Shape::create_circle(radius, segments));
}

std::unique_ptr<Shape> ShapeFactory::create_polygon(const std::vector<std::vector<double>>& points) {
    throw_if_invalid_polygon(points);
    return std::make_unique<Shape>(points);
}

std::unique_ptr<Shape> ShapeFactory::create_regular_polygon(double radius, int sides) {
    if (radius <= 0) {
        throw GeometryError("Regular polygon radius must be positive");
    }
    if (sides < 3) {
        throw GeometryError("Regular polygon must have at least 3 sides");
    }

    std::vector<std::vector<double>> points;
    points.reserve(sides);

    for (int i = 0; i < sides; ++i) {
        double angle = 2.0 * M_PI * i / sides;
        double x = radius * std::cos(angle);
        double y = radius * std::sin(angle);
        points.push_back({x, y});
    }

    return std::make_unique<Shape>(points);
}

std::unique_ptr<Shape> ShapeFactory::create_star(double outer_radius, double inner_radius, int points) {
    if (outer_radius <= 0 || inner_radius <= 0) {
        throw GeometryError("Star radii must be positive");
    }
    if (inner_radius >= outer_radius) {
        throw GeometryError("Inner radius must be less than outer radius");
    }
    if (points < 3) {
        throw GeometryError("Star must have at least 3 points");
    }

    std::vector<std::vector<double>> vertices;
    vertices.reserve(points * 2);

    for (int i = 0; i < points; ++i) {
        // Outer point
        double outer_angle = 2.0 * M_PI * i / points;
        double outer_x = outer_radius * std::cos(outer_angle);
        double outer_y = outer_radius * std::sin(outer_angle);
        vertices.push_back({outer_x, outer_y});

        // Inner point
        double inner_angle = 2.0 * M_PI * (i + 0.5) / points;
        double inner_x = inner_radius * std::cos(inner_angle);
        double inner_y = inner_radius * std::sin(inner_angle);
        vertices.push_back({inner_x, inner_y});
    }

    return std::make_unique<Shape>(vertices);
}

// Sheet factory implementations
std::unique_ptr<Sheet> SheetFactory::create_standard_sheet(StandardSheetSize size) {
    switch (size) {
        case StandardSheetSize::A4:
            return std::make_unique<Sheet>(210.0, 297.0); // mm
        case StandardSheetSize::A3:
            return std::make_unique<Sheet>(297.0, 420.0);
        case StandardSheetSize::A2:
            return std::make_unique<Sheet>(420.0, 594.0);
        case StandardSheetSize::A1:
            return std::make_unique<Sheet>(594.0, 841.0);
        case StandardSheetSize::A0:
            return std::make_unique<Sheet>(841.0, 1189.0);
        case StandardSheetSize::US_LETTER:
            return std::make_unique<Sheet>(215.9, 279.4);
        case StandardSheetSize::US_LEGAL:
            return std::make_unique<Sheet>(215.9, 355.6);
        case StandardSheetSize::US_TABLOID:
            return std::make_unique<Sheet>(279.4, 431.8);
        default:
            throw ConfigurationError("Unknown standard sheet size");
    }
}

std::unique_ptr<Sheet> SheetFactory::create_custom_sheet(double width, double height) {
    throw_if_sheet_too_small(Sheet(width, height));
    return std::make_unique<Sheet>(width, height);
}

std::unique_ptr<Sheet> SheetFactory::create_square_sheet(double side) {
    if (side <= 0) {
        throw GeometryError("Square sheet side must be positive");
    }
    return std::make_unique<Sheet>(side, side);
}

// Config factory implementations
std::unique_ptr<NestConfig> ConfigFactory::create_preset_config(ConfigPreset preset) {
    switch (preset) {
        case ConfigPreset::FAST:
            return std::make_unique<NestConfig>(NestConfig::create_fast());
        case ConfigPreset::QUALITY:
            return std::make_unique<NestConfig>(NestConfig::create_quality());
        case ConfigPreset::BALANCED:
            return std::make_unique<NestConfig>(NestConfig::create_balanced());
        case ConfigPreset::HIGH_PRECISION:
            return std::make_unique<NestConfig>(NestConfig::create_high_precision());
        case ConfigPreset::METAL_CUTTING:
            return std::make_unique<NestConfig>(NestConfig::create_metal_cutting());
        case ConfigPreset::FABRIC_CUTTING:
            return std::make_unique<NestConfig>(NestConfig::create_fabric_cutting());
        case ConfigPreset::GLASS_CUTTING:
            return std::make_unique<NestConfig>(NestConfig::create_glass_cutting());
        default:
            throw ConfigurationError("Unknown config preset");
    }
}

std::unique_ptr<NestConfig> ConfigFactory::create_custom_config(
    const std::string& placer_type,
    float accuracy,
    const std::vector<double>& rotations,
    double spacing) {

    auto config = std::make_unique<NestConfig>();
    config->placer_type = placer_type;
    config->accuracy = accuracy;
    config->rotations = rotations;
    config->spacing = spacing;

    throw_if_invalid_config(*config);
    return config;
}

} // namespace nest2d_wrapper
