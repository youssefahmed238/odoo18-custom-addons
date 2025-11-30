#ifndef NEST2D_CONFIG_HPP
#define NEST2D_CONFIG_HPP

#include "types.hpp"
#include "optimizers.hpp"
#include "parallel.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
// Conditional include for libnest2d
#ifdef LIBNEST2D_AVAILABLE
#include <libnest2d/placers/nfpplacer.hpp>
#endif
#include <string>
#include <vector>
#include <functional>
#include <type_traits>

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Configuration for nesting algorithms - comprehensive wrapper with advanced features
 */
class NestConfig {
public:
    // Basic placer settings
    std::string placer_type = "nfp"; // "nfp" or "bottom_left"
    std::vector<double> rotations = {0.0, 90.0, 180.0, 270.0};
    std::string alignment = "bottom_left";
    std::string starting_point = "bottom_left";
    float accuracy = 0.65f;
    bool explore_holes = false;
    bool parallel = true;

    // Selector settings
    std::string selector_type = "firstfit"; // "firstfit", "filler", "djd"

    // General settings
    double spacing = 0.0;

    // === ADVANCED NFP CONFIGURATION ===

    // Custom fitting function for NFP placer
    py::function custom_fit_function;

    // Advanced NFP callbacks
    py::function before_packing_callback;  // Called before each item placement
    py::function on_preload_callback;      // Called on configuration preload

    // Optimization configuration
    OptimizerConfig optimizer_config;
    bool use_custom_optimizer = false;

    // Parallel processing configuration
    ParallelConfig parallel_config;

    // Edge cache configuration
    bool use_edge_cache = true;
    double edge_cache_accuracy = 1.0;

    // Advanced geometric processing
    bool remove_collinear_points = false;
    double collinear_tolerance = 1e-9;
    bool snap_to_grid = false;
    double grid_size = 0.001;

    // Quality vs speed trade-offs
    bool high_precision_mode = false;
    bool fast_mode = false;

    // Debugging and analysis
    bool enable_debug_output = false;
    bool collect_statistics = false;

    // === FACTORY METHODS ===

    static NestConfig create_fast();
    static NestConfig create_quality();
    static NestConfig create_balanced();
    static NestConfig create_custom(const std::string& placer, float accuracy, const std::vector<double>& rotations);

    // Advanced factory methods
    static NestConfig create_high_precision();
    static NestConfig create_parallel_optimized(int num_threads = -1);
    static NestConfig create_metal_cutting();
    static NestConfig create_fabric_cutting();
    static NestConfig create_glass_cutting();

    std::string to_string() const;

    // Conversion methods to LibNest2D native configs
    NfpPlacerConfig get_nfp_config() const;
    BottomLeftPlacerConfig get_bottom_left_config() const;

    // Advanced conversion methods
    libnest2d::placers::NfpPConfig<libnest2d::PolygonImpl> get_advanced_nfp_config() const;

    // Generic template conversion
    template<class PlacerConfig>
    PlacerConfig get_placer_config() const;

    // Validation
    bool validate() const;
    std::vector<std::string> get_validation_errors() const;

private:
    static NfpPlacerConfig::Alignment string_to_alignment(const std::string& align);
};

/**
 * Progress and control wrapper for LibNest2D
 */
class ProgressControl {
public:
    py::function progress_function;
    py::function stop_condition;

    ProgressControl() = default;
    ProgressControl(py::function progress_fn) : progress_function(progress_fn) {}
    ProgressControl(py::function progress_fn, py::function stop_fn)
        : progress_function(progress_fn), stop_condition(stop_fn) {}

    LibNest2DNestControl to_internal() const {
        LibNest2DNestControl control;

        if (!progress_function.is_none()) {
            control.progressfn = [this](unsigned remaining) {
                this->progress_function(remaining);
            };
        }

        if (!stop_condition.is_none()) {
            control.stopcond = [this]() -> bool {
                return this->stop_condition().cast<bool>();
            };
        }

        return control;
    }
};

/**
 * Selection strategy configuration
 */
class SelectionConfig {
public:
    std::string strategy_type = "firstfit";

    // FirstFit config (minimal)
    struct FirstFitConfig {
        int dummy = 0; // FirstFit uses int as config
    };

    // Filler config
    struct FillerConfig {
        int dummy = 0; // Filler uses int as config
    };

    // DJD config
    struct DJDConfig {
        int dummy = 0; // DJD uses int as config
    };

    FirstFitConfig firstfit_config;
    FillerConfig filler_config;
    DJDConfig djd_config;

    template<class Selector>
    auto get_selection_config() const -> typename Selector::Config;
};


} // namespace nest2d_wrapper

#endif // NEST2D_CONFIG_HPP
