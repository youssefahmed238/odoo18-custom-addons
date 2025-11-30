#pragma once

#include "types.hpp"
#include <string>
#include <vector>
#include <map>
#include <chrono>

namespace nest2d_wrapper {

// Simple type aliases for C++14 compatibility
using LibNest2DNfpPlacer = int; // Simplified placeholder
using LibNest2DBottomLeftPlacer = int; // Simplified placeholder
using LibNest2DFirstFitSelection = int;
using LibNest2DFillerSelection = int;
using LibNest2DDJDHeuristic = int;

/**
 * Simple type dispatcher for algorithm selection (C++14 compatible)
 */
class TypeDispatcher {
private:
    std::string placer_type_;
    std::string selector_type_;

public:
    TypeDispatcher(const std::string& placer_type, const std::string& selector_type)
        : placer_type_(placer_type), selector_type_(selector_type) {}

    // Get placer configuration info
    py::dict get_placer_config_info() const;

    // Get selector configuration info
    py::dict get_selector_config_info() const;

    // Static utility functions
    static std::vector<std::string> get_available_placers();
    static std::vector<std::string> get_available_selectors();
    static bool is_valid_placer(const std::string& placer_type);
    static bool is_valid_selector(const std::string& selector_type);
};

/**
 * Simple algorithm factory (C++14 compatible)
 */
class AlgorithmFactory {
public:
    // Create algorithm instance
    static py::dict create_algorithm_instance(const std::string& placer_type,
                                             const std::string& selector_type);

    // Execute nesting
    static py::dict execute_nesting(const std::vector<std::vector<std::vector<double>>>& shapes,
                                   double sheet_width, double sheet_height,
                                   const std::string& placer_type = "nfp",
                                   const std::string& selector_type = "firstfit");

    // Benchmark algorithms
    static py::dict benchmark_algorithms(const std::vector<std::vector<std::vector<double>>>& shapes,
                                        double sheet_width, double sheet_height,
                                        const std::vector<std::string>& algorithm_names = {},
                                        int iterations = 3);

    // Get performance profile
    static py::dict get_algorithm_performance_profile(const std::string& algorithm_name);
};

namespace performance {

/**
 * Simple performance profiler (C++14 compatible)
 */
class PerformanceProfiler {
private:
    std::string operation_name_;
    std::chrono::steady_clock::time_point start_time_;

public:
    explicit PerformanceProfiler(const std::string& operation_name);
    ~PerformanceProfiler();

    static py::dict get_profiling_results();
    static void clear_profiling_data();
    static void enable_profiling(bool enable);
};

// Simple memory estimation
inline size_t estimate_memory_usage_simple(size_t num_shapes, size_t avg_vertices_per_shape,
                                          const std::string& algorithm) {
    size_t base = num_shapes * avg_vertices_per_shape * sizeof(double) * 2;
    if (algorithm == "nfp") {
        return base * 10; // NFP uses more memory
    }
    return base * 2;
}

} // namespace performance

} // namespace nest2d_wrapper
