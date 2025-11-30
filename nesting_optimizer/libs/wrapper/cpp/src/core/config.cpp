#include "../../include/core/config.hpp"
#include <sstream>
#include <stdexcept>
#include <thread>

namespace nest2d_wrapper {

// Static factory methods for presets
NestConfig NestConfig::create_fast() {
    NestConfig config;
    config.placer_type = "bottom_left";
    config.accuracy = 0.3f;
    config.parallel = true;
    config.rotations = {0.0}; // No rotation for speed
    config.selector_type = "firstfit";
    config.fast_mode = true;
    config.parallel_config = ParallelConfig(ParallelConfig::ThreadingBackend::STD_THREAD, 2);
    return config;
}

NestConfig NestConfig::create_quality() {
    NestConfig config;
    config.placer_type = "nfp";
    config.accuracy = 0.95f;
    config.parallel = true;
    config.explore_holes = true;
    config.rotations = {0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0};
    config.selector_type = "djd";
    config.use_edge_cache = true;
    config.edge_cache_accuracy = 1.0;
    config.optimizer_config = OptimizerConfig::create_quality_config();
    return config;
}

NestConfig NestConfig::create_balanced() {
    NestConfig config;
    config.placer_type = "nfp";
    config.accuracy = 0.65f;
    config.parallel = true;
    config.rotations = {0.0, 90.0, 180.0, 270.0};
    config.selector_type = "firstfit";
    config.optimizer_config = OptimizerConfig::create_balanced_config();
    return config;
}

NestConfig NestConfig::create_custom(const std::string& placer, float accuracy, const std::vector<double>& rotations) {
    NestConfig config;
    config.placer_type = placer;
    config.accuracy = accuracy;
    config.rotations = rotations;
    return config;
}

NestConfig NestConfig::create_high_precision() {
    NestConfig config;
    config.placer_type = "nfp";
    config.accuracy = 0.99f;
    config.parallel = true;
    config.explore_holes = true;
    config.rotations = {0.0, 30.0, 45.0, 60.0, 90.0, 120.0, 135.0, 150.0, 180.0, 210.0, 225.0, 240.0, 270.0, 300.0, 315.0, 330.0};
    config.selector_type = "djd";
    config.use_edge_cache = true;
    config.edge_cache_accuracy = 1.0;
    config.high_precision_mode = true;
    config.remove_collinear_points = true;
    config.collinear_tolerance = 1e-12;
    return config;
}

NestConfig NestConfig::create_parallel_optimized(int num_threads) {
    NestConfig config = create_balanced();
    config.parallel = true;
    if (num_threads < 0) {
        num_threads = std::thread::hardware_concurrency();
    }
    config.parallel_config = ParallelConfig(ParallelConfig::ThreadingBackend::STD_THREAD, num_threads);
    config.optimizer_config.enable_parallel_optimization = true;
    return config;
}

NestConfig NestConfig::create_metal_cutting() {
    NestConfig config = create_quality();
    config.spacing = 2.0; // 2mm kerf width
    config.snap_to_grid = true;
    config.grid_size = 0.1; // 0.1mm precision
    config.remove_collinear_points = true;
    config.rotations = {0.0, 90.0}; // Typically only 90-degree rotations for metal
    return config;
}

NestConfig NestConfig::create_fabric_cutting() {
    NestConfig config = create_quality();
    config.spacing = 0.5; // Minimal spacing for fabric
    config.rotations = {0.0, 90.0, 180.0, 270.0};
    config.explore_holes = true;
    return config;
}

NestConfig NestConfig::create_glass_cutting() {
    NestConfig config = create_high_precision();
    config.spacing = 3.0; // 3mm scoring width
    config.rotations = {0.0}; // No rotation to avoid stress
    config.snap_to_grid = true;
    config.grid_size = 0.05; // High precision for glass
    return config;
}

std::string NestConfig::to_string() const {
    std::ostringstream oss;
    oss << "NestConfig("
        << "placer=" << placer_type
        << ", accuracy=" << accuracy
        << ", spacing=" << spacing
        << ", rotations=[";
    for (size_t i = 0; i < rotations.size(); ++i) {
        if (i > 0) oss << ",";
        oss << rotations[i];
    }
    oss << "], selector=" << selector_type
        << ", parallel=" << (parallel ? "true" : "false")
        << ", high_precision=" << (high_precision_mode ? "true" : "false")
        << ")";
    return oss.str();
}

NfpPlacerConfig NestConfig::get_nfp_config() const {
    NfpPlacerConfig nfp_config;
    nfp_config.accuracy = accuracy;
    nfp_config.explore_holes = explore_holes;
    nfp_config.alignment = string_to_alignment(alignment);
    nfp_config.starting_point = string_to_alignment(starting_point);
    return nfp_config;
}

BottomLeftPlacerConfig NestConfig::get_bottom_left_config() const {
    return 0; // BottomLeft placer uses int as config
}

bool NestConfig::validate() const {
    if (placer_type != "nfp" && placer_type != "bottom_left") {
        return false;
    }
    if (accuracy < 0.0f || accuracy > 1.0f) {
        return false;
    }
    if (spacing < 0.0) {
        return false;
    }
    if (rotations.empty()) {
        return false;
    }
    return true;
}

std::vector<std::string> NestConfig::get_validation_errors() const {
    std::vector<std::string> errors;

    if (placer_type != "nfp" && placer_type != "bottom_left") {
        errors.push_back("Invalid placer_type: must be 'nfp' or 'bottom_left'");
    }
    if (accuracy < 0.0f || accuracy > 1.0f) {
        errors.push_back("Invalid accuracy: must be between 0.0 and 1.0");
    }
    if (spacing < 0.0) {
        errors.push_back("Invalid spacing: must be non-negative");
    }
    if (rotations.empty()) {
        errors.push_back("rotations cannot be empty");
    }

    return errors;
}

NfpPlacerConfig::Alignment NestConfig::string_to_alignment(const std::string& align) {
    if (align == "bottom_left") return NfpPlacerConfig::Alignment::BOTTOM_LEFT;
    if (align == "bottom_right") return NfpPlacerConfig::Alignment::BOTTOM_RIGHT;
    if (align == "top_left") return NfpPlacerConfig::Alignment::TOP_LEFT;
    if (align == "top_right") return NfpPlacerConfig::Alignment::TOP_RIGHT;
    if (align == "center") return NfpPlacerConfig::Alignment::CENTER;
    return NfpPlacerConfig::Alignment::BOTTOM_LEFT;
}

OptimizerConfig OptimizerConfig::create_quality_config() {
    OptimizerConfig config;
    config.method = OptimizationMethod::GENETIC;
    config.stop_criteria = StopCriteria(1e-8, 1e-14, 2000, 60.0);
    config.enable_parallel_optimization = true;
    return config;
}

OptimizerConfig OptimizerConfig::create_balanced_config() {
    OptimizerConfig config;
    config.method = OptimizationMethod::SUBPLEX;
    config.stop_criteria = StopCriteria(1e-6, 1e-12, 1000, 30.0);
    config.enable_parallel_optimization = false;
    return config;
}

} // namespace nest2d_wrapper
