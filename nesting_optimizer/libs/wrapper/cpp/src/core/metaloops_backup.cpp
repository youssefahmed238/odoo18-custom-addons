#include "../include/core/metaloops.hpp"
#include <sstream>
#include <chrono>

namespace nest2d_wrapper {

// TypeDispatcher implementations
template<typename Function>
auto TypeDispatcher::dispatch_nesting(Function&& func)
    -> decltype(func(LibNest2DNfpPlacer{}, LibNest2DFirstFitSelection{})) {

    if (placer_type_ == "nfp" && selector_type_ == "firstfit") {
        return func(LibNest2DNfpPlacer{}, LibNest2DFirstFitSelection{});
    } else if (placer_type_ == "nfp" && selector_type_ == "filler") {
        return func(LibNest2DNfpPlacer{}, LibNest2DFillerSelection{});
    } else if (placer_type_ == "nfp" && selector_type_ == "djd") {
        return func(LibNest2DNfpPlacer{}, LibNest2DDJDHeuristic{});
    } else if (placer_type_ == "bottom_left" && selector_type_ == "firstfit") {
        return func(LibNest2DBottomLeftPlacer{}, LibNest2DFirstFitSelection{});
    } else if (placer_type_ == "bottom_left" && selector_type_ == "filler") {
        return func(LibNest2DBottomLeftPlacer{}, LibNest2DFillerSelection{});
    } else if (placer_type_ == "bottom_left" && selector_type_ == "djd") {
        return func(LibNest2DBottomLeftPlacer{}, LibNest2DDJDHeuristic{});
    } else {
        throw std::runtime_error("Unsupported placer/selector combination: " +
                               placer_type_ + "/" + selector_type_);
    }
}

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
py::dict AlgorithmFactory::create_algorithm_instance(const NestConfig& config) {
    py::dict instance;

    instance["placer_type"] = config.placer_type;
    instance["selector_type"] = config.selector_type;
    instance["config"] = config.to_string();

    TypeDispatcher dispatcher(config.placer_type, config.selector_type);
    instance["placer_info"] = dispatcher.get_placer_config_info();
    instance["selector_info"] = dispatcher.get_selector_config_info();

    return instance;
}

py::dict AlgorithmFactory::execute_optimal_nesting(std::vector<Shape>& shapes,
                                                  const Sheet& sheet,
                                                  const NestConfig& config) {
    py::dict result;

    try {
        TypeDispatcher dispatcher(config.placer_type, config.selector_type);

        auto nesting_func = [&shapes, &sheet, &config](auto placer, auto selector) {
            py::dict nested_result;

            // This would contain the actual nesting logic
            // For now, return placeholder result
            nested_result["success"] = true;
            nested_result["algorithm"] = AlgorithmTraits<decltype(placer), decltype(selector)>::get_algorithm_name();
            nested_result["shape_count"] = shapes.size();
            nested_result["sheet_area"] = sheet.width * sheet.height;

            return nested_result;
        };

        result = dispatcher.dispatch_nesting(nesting_func);

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AlgorithmFactory::benchmark_algorithms(std::vector<Shape>& shapes,
                                               const Sheet& sheet,
                                               const std::vector<std::string>& algorithm_names,
                                               int iterations) {
    py::dict benchmark_results;

    std::vector<std::string> algorithms_to_test = algorithm_names;
    if (algorithms_to_test.empty()) {
        // Test all available combinations
        auto placers = TypeDispatcher::get_available_placers();
        auto selectors = TypeDispatcher::get_available_selectors();

        for (const auto& placer : placers) {
            for (const auto& selector : selectors) {
                algorithms_to_test.push_back(placer + "+" + selector);
            }
        }
    }

    py::dict results;

    for (const auto& algo_name : algorithms_to_test) {
        auto pos = algo_name.find('+');
        if (pos == std::string::npos) continue;

        std::string placer = algo_name.substr(0, pos);
        std::string selector = algo_name.substr(pos + 1);

        if (!TypeDispatcher::is_valid_placer(placer) ||
            !TypeDispatcher::is_valid_selector(selector)) {
            continue;
        }

        NestConfig config;
        config.placer_type = placer;
        config.selector_type = selector;

        py::dict algo_result;
        std::vector<double> times;

        for (int i = 0; i < iterations; ++i) {
            auto start_time = std::chrono::high_resolution_clock::now();

            auto result = execute_optimal_nesting(shapes, sheet, config);

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

        results[algo_name] = algo_result;
    }

    benchmark_results["results"] = results;
    benchmark_results["shape_count"] = shapes.size();
    benchmark_results["sheet_size"] = std::vector<double>{sheet.width, sheet.height};

    return benchmark_results;
}

py::dict AlgorithmFactory::recommend_algorithm(const std::vector<Shape>& shapes,
                                              const Sheet& sheet) {
    py::dict recommendation;

    // Analyze shape characteristics
    size_t shape_count = shapes.size();
    double avg_vertices = 0.0;
    bool has_complex_shapes = false;

    for (const auto& shape : shapes) {
        size_t vertex_count = shape.vertex_count();
        avg_vertices += vertex_count;
        if (vertex_count > 20) {
            has_complex_shapes = true;
        }
    }
    avg_vertices /= shape_count;

    // Calculate shape density
    double total_shape_area = 0.0;
    for (const auto& shape : shapes) {
        total_shape_area += shape.area();
    }
    double sheet_area = sheet.width * sheet.height;
    double density = total_shape_area / sheet_area;

    // Make recommendation based on analysis
    std::string recommended_placer;
    std::string recommended_selector;
    std::string reason;

    if (shape_count < 10 && !has_complex_shapes) {
        recommended_placer = "bottom_left";
        recommended_selector = "firstfit";
        reason = "Small number of simple shapes - fast algorithm recommended";
    } else if (has_complex_shapes || density > 0.8) {
        recommended_placer = "nfp";
        recommended_selector = "djd";
        reason = "Complex shapes or high density - quality algorithm recommended";
    } else {
        recommended_placer = "nfp";
        recommended_selector = "firstfit";
        reason = "Balanced approach for moderate complexity";
    }

    recommendation["placer"] = recommended_placer;
    recommendation["selector"] = recommended_selector;
    recommendation["algorithm"] = recommended_placer + "+" + recommended_selector;
    recommendation["reason"] = reason;
    recommendation["shape_count"] = shape_count;
    recommendation["avg_vertices"] = avg_vertices;
    recommendation["density"] = density;
    recommendation["has_complex_shapes"] = has_complex_shapes;

    return recommendation;
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

    // Performance characteristics (empirical data)
    if (placer == "nfp" && selector == "firstfit") {
        profile["speed"] = "medium";
        profile["quality"] = "good";
        profile["memory_usage"] = "medium";
        profile["scalability"] = "good";
        profile["recommended_for"] = "general purpose nesting";
    } else if (placer == "nfp" && selector == "djd") {
        profile["speed"] = "slow";
        profile["quality"] = "excellent";
        profile["memory_usage"] = "high";
        profile["scalability"] = "medium";
        profile["recommended_for"] = "high-quality nesting, small to medium datasets";
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

        results[operation] = operation_stats;
    }

    return results;
}

void PerformanceProfiler::clear_profiling_data() {
    profiling_data_.clear();
}

void PerformanceProfiler::enable_profiling(bool enable) {
    profiling_enabled_ = enable;
}

// Template specializations for memory estimation
template<>
size_t estimate_memory_usage<LibNest2DNfpPlacer, LibNest2DFirstFitSelection>(
    size_t num_shapes, size_t avg_vertices_per_shape) {

    // NFP placer uses more memory due to NFP calculations
    size_t base_memory = num_shapes * sizeof(LibNest2DItem);
    size_t vertex_memory = num_shapes * avg_vertices_per_shape * sizeof(LibNest2DPoint);
    size_t nfp_memory = num_shapes * num_shapes * avg_vertices_per_shape * sizeof(LibNest2DPoint);

    return base_memory + vertex_memory + nfp_memory;
}

template<>
size_t estimate_memory_usage<LibNest2DBottomLeftPlacer, LibNest2DFirstFitSelection>(
    size_t num_shapes, size_t avg_vertices_per_shape) {

    // BottomLeft placer uses less memory
    size_t base_memory = num_shapes * sizeof(LibNest2DItem);
    size_t vertex_memory = num_shapes * avg_vertices_per_shape * sizeof(LibNest2DPoint);

    return base_memory + vertex_memory;
}

} // namespace performance

} // namespace nest2d_wrapper
