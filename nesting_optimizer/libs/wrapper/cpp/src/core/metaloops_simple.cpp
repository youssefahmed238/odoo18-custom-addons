#include "../include/core/metaloops.hpp"
#include <sstream>
#include <chrono>

namespace nest2d_wrapper {

// TypeDispatcher implementations
py::dict TypeDispatcher::get_placer_config_info() const {
    py::dict info;
    info["type"] = placer_type_;

    if (placer_type_ == "nfp") {
        info["supports_rotations"] = true;
        info["supports_holes"] = true;
        info["supports_custom_fit"] = true;
        info["config_type"] = "NfpPConfig";
    } else if (placer_type_ == "bottom_left") {
        info["supports_rotations"] = false;
        info["supports_holes"] = false;
        info["supports_custom_fit"] = false;
        info["config_type"] = "int";
    }

    return info;
}

py::dict TypeDispatcher::get_selector_config_info() const {
    py::dict info;
    info["type"] = selector_type_;

    if (selector_type_ == "firstfit") {
        info["description"] = "First-fit selection strategy";
        info["deterministic"] = true;
        info["config_type"] = "int";
    } else if (selector_type_ == "filler") {
        info["description"] = "Filler selection strategy";
        info["deterministic"] = true;
        info["config_type"] = "int";
    } else if (selector_type_ == "djd") {
        info["description"] = "DJD heuristic selection";
        info["deterministic"] = false;
        info["config_type"] = "int";
    }

    return info;
}

std::vector<std::string> TypeDispatcher::get_available_placers() {
    return {"nfp", "bottom_left"};
}

std::vector<std::string> TypeDispatcher::get_available_selectors() {
    return {"firstfit", "filler", "djd"};
}

bool TypeDispatcher::is_valid_placer(const std::string& placer_type) {
    auto available = get_available_placers();
    return std::find(available.begin(), available.end(), placer_type) != available.end();
}

bool TypeDispatcher::is_valid_selector(const std::string& selector_type) {
    auto available = get_available_selectors();
    return std::find(available.begin(), available.end(), selector_type) != available.end();
}

// AlgorithmFactory implementations
py::dict AlgorithmFactory::create_algorithm_instance(const std::string& placer_type,
                                                    const std::string& selector_type) {
    py::dict instance;

    instance["placer_type"] = placer_type;
    instance["selector_type"] = selector_type;
    instance["config"] = placer_type + "+" + selector_type;

    TypeDispatcher dispatcher(placer_type, selector_type);
    instance["placer_info"] = dispatcher.get_placer_config_info();
    instance["selector_info"] = dispatcher.get_selector_config_info();

    return instance;
}

py::dict AlgorithmFactory::execute_nesting(const std::vector<std::vector<std::vector<double>>>& shapes,
                                          double sheet_width, double sheet_height,
                                          const std::string& placer_type,
                                          const std::string& selector_type) {
    py::dict result;

    try {
        result["success"] = true;
        result["algorithm"] = placer_type + "+" + selector_type;
        result["shape_count"] = shapes.size();
        result["sheet_area"] = sheet_width * sheet_height;
        result["utilization"] = 0.75; // Placeholder

        // Create placeholder nested shapes result
        py::list nested_shapes;
        for (size_t i = 0; i < shapes.size(); ++i) {
            py::dict shape_result;
            shape_result["id"] = i;
            shape_result["x"] = (i % 5) * 20.0; // Simple grid placement
            shape_result["y"] = (i / 5) * 20.0;
            shape_result["rotation"] = 0.0;
            shape_result["sheet_id"] = 0;
            nested_shapes.append(shape_result);
        }
        result["nested_shapes"] = nested_shapes;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AlgorithmFactory::benchmark_algorithms(const std::vector<std::vector<std::vector<double>>>& shapes,
                                               double sheet_width, double sheet_height,
                                               const std::vector<std::string>& algorithm_names,
                                               int iterations) {
    py::dict benchmark_results;

    std::vector<std::string> algorithms_to_test = algorithm_names;
    if (algorithms_to_test.empty()) {
        algorithms_to_test = {"nfp+firstfit", "nfp+filler", "bottom_left+firstfit"};
    }

    py::dict results;

    for (const auto& algo_name : algorithms_to_test) {
        auto pos = algo_name.find('+');
        if (pos == std::string::npos) continue;

        std::string placer = algo_name.substr(0, pos);
        std::string selector = algo_name.substr(pos + 1);

        py::dict algo_result;
        std::vector<double> times;

        for (int i = 0; i < iterations; ++i) {
            auto start_time = std::chrono::high_resolution_clock::now();

            auto result = execute_nesting(shapes, sheet_width, sheet_height, placer, selector);

            auto end_time = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
            times.push_back(duration.count());
        }

        // Calculate statistics
        double avg_time = std::accumulate(times.begin(), times.end(), 0.0) / times.size();
        double min_time = *std::min_element(times.begin(), times.end());
        double max_time = *std::max_element(times.begin(), times.end());

        algo_result["algorithm"] = algo_name;
        algo_result["avg_time_ms"] = avg_time;
        algo_result["min_time_ms"] = min_time;
        algo_result["max_time_ms"] = max_time;
        algo_result["iterations"] = iterations;

        results[py::str(algo_name)] = algo_result;
    }

    benchmark_results["results"] = results;
    benchmark_results["shape_count"] = shapes.size();

    return benchmark_results;
}

py::dict AlgorithmFactory::get_algorithm_performance_profile(const std::string& algorithm_name) {
    py::dict profile;

    auto pos = algorithm_name.find('+');
    if (pos == std::string::npos) {
        profile["error"] = "Invalid algorithm name format";
        return profile;
    }

    std::string placer = algorithm_name.substr(0, pos);
    std::string selector = algorithm_name.substr(pos + 1);

    profile["algorithm"] = algorithm_name;
    profile["placer"] = placer;
    profile["selector"] = selector;

    // Performance characteristics (simplified)
    if (placer == "nfp" && selector == "firstfit") {
        profile["speed"] = "medium";
        profile["quality"] = "good";
        profile["memory_usage"] = "medium";
        profile["scalability"] = "good";
        profile["recommended_for"] = "general purpose nesting";
    } else if (placer == "bottom_left" && selector == "firstfit") {
        profile["speed"] = "fast";
        profile["quality"] = "fair";
        profile["memory_usage"] = "low";
        profile["scalability"] = "excellent";
        profile["recommended_for"] = "fast nesting, large datasets";
    } else {
        profile["speed"] = "unknown";
        profile["quality"] = "unknown";
        profile["memory_usage"] = "unknown";
        profile["scalability"] = "unknown";
        profile["recommended_for"] = "experimental";
    }

    return profile;
}

namespace performance {

// PerformanceProfiler implementations
thread_local std::map<std::string, std::vector<double>> profiling_data_;
thread_local bool profiling_enabled_ = false;

PerformanceProfiler::PerformanceProfiler(const std::string& operation_name)
    : operation_name_(operation_name) {
    if (profiling_enabled_) {
        start_time_ = std::chrono::steady_clock::now();
    }
}

PerformanceProfiler::~PerformanceProfiler() {
    if (profiling_enabled_) {
        auto end_time = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time_);

        profiling_data_[operation_name_].push_back(duration.count());
    }
}

py::dict PerformanceProfiler::get_profiling_results() {
    py::dict results;

    for (const auto& entry : profiling_data_) {
        const std::string& operation = entry.first;
        const std::vector<double>& times = entry.second;

        if (times.empty()) continue;

        py::dict operation_stats;
        double total = std::accumulate(times.begin(), times.end(), 0.0);
        operation_stats["total_time_us"] = total;
        operation_stats["avg_time_us"] = total / times.size();
        operation_stats["min_time_us"] = *std::min_element(times.begin(), times.end());
        operation_stats["max_time_us"] = *std::max_element(times.begin(), times.end());
        operation_stats["call_count"] = times.size();

        results[py::str(operation)] = operation_stats;
    }

    return results;
}

void PerformanceProfiler::clear_profiling_data() {
    profiling_data_.clear();
}

void PerformanceProfiler::enable_profiling(bool enable) {
    profiling_enabled_ = enable;
}

} // namespace performance

} // namespace nest2d_wrapper
