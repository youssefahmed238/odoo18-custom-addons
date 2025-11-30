#ifndef NEST2D_METALOOPS_HPP
#define NEST2D_METALOOPS_HPP

#include "types.hpp"
#include <pybind11/pybind11.h>
#include <type_traits>
#include <tuple>
#include <functional>

// Include LibNest2D metaloop utilities if available
#ifdef LIBNEST2D_METALOOP_AVAILABLE
#include <libnest2d/utils/metaloop.hpp>
#endif

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Template metaprogramming utilities for type-safe operations
 */
namespace meta {

    /**
     * Type trait to check if a type is a placer
     */
    template<typename T>
    struct is_placer : std::false_type {};

    template<>
    struct is_placer<LibNest2DNfpPlacer> : std::true_type {};

    template<>
    struct is_placer<LibNest2DBottomLeftPlacer> : std::true_type {};

    /**
     * Type trait to check if a type is a selector
     */
    template<typename T>
    struct is_selector : std::false_type {};

    template<>
    struct is_selector<LibNest2DFirstFitSelection> : std::true_type {};

    template<>
    struct is_selector<LibNest2DFillerSelection> : std::true_type {};

    template<>
    struct is_selector<LibNest2DDJDHeuristic> : std::true_type {};

    /**
     * Compile-time type selection based on string
     */
    template<typename... Types>
    struct TypeSelector;

    template<typename First, typename... Rest>
    struct TypeSelector<First, Rest...> {
        template<typename Predicate>
        static auto select(const std::string& name, Predicate pred) {
            if (pred(name)) {
                return First{};
            } else {
                return TypeSelector<Rest...>::template select(name, pred);
            }
        }
    };

    template<>
    struct TypeSelector<> {
        template<typename Predicate>
        static auto select(const std::string& /*name*/, Predicate /*pred*/) {
            throw std::runtime_error("Type not found");
        }
    };

} // namespace meta

/**
 * Dynamic type dispatch for placer and selector combinations
 */
class TypeDispatcher {
private:
    std::string placer_type_;
    std::string selector_type_;

public:
    TypeDispatcher(const std::string& placer_type, const std::string& selector_type)
        : placer_type_(placer_type), selector_type_(selector_type) {}

    /**
     * Execute nesting with dynamically selected types
     */
    template<typename Function>
    auto dispatch_nesting(Function&& func) -> decltype(func(LibNest2DNfpPlacer{}, LibNest2DFirstFitSelection{}));

    /**
     * Get placer configuration for specific type
     */
    py::dict get_placer_config_info() const;

    /**
     * Get selector configuration for specific type
     */
    py::dict get_selector_config_info() const;

    /**
     * List all available placer types
     */
    static std::vector<std::string> get_available_placers();

    /**
     * List all available selector types
     */
    static std::vector<std::string> get_available_selectors();

    /**
     * Check if placer type is valid
     */
    static bool is_valid_placer(const std::string& placer_type);

    /**
     * Check if selector type is valid
     */
    static bool is_valid_selector(const std::string& selector_type);
};

/**
 * Compile-time algorithm selection utilities
 */
template<typename PlacerType, typename SelectorType>
class AlgorithmTraits {
public:
    using Placer = PlacerType;
    using Selector = SelectorType;
    using PlacerConfig = typename PlacerType::Config;
    using SelectorConfig = typename SelectorType::Config;

    static constexpr bool supports_holes =
        std::is_same_v<PlacerType, LibNest2DNfpPlacer>;

    static constexpr bool supports_custom_fit =
        std::is_same_v<PlacerType, LibNest2DNfpPlacer>;

    static constexpr bool is_deterministic =
        !std::is_same_v<SelectorType, LibNest2DDJDHeuristic>;

    static std::string get_algorithm_name() {
        std::string placer_name = std::is_same_v<PlacerType, LibNest2DNfpPlacer> ? "NFP" : "BottomLeft";
        std::string selector_name;
        if constexpr (std::is_same_v<SelectorType, LibNest2DFirstFitSelection>) {
            selector_name = "FirstFit";
        } else if constexpr (std::is_same_v<SelectorType, LibNest2DFillerSelection>) {
            selector_name = "Filler";
        } else if constexpr (std::is_same_v<SelectorType, LibNest2DDJDHeuristic>) {
            selector_name = "DJD";
        }
        return placer_name + "+" + selector_name;
    }

    static py::dict get_algorithm_capabilities() {
        py::dict caps;
        caps["supports_holes"] = supports_holes;
        caps["supports_custom_fit"] = supports_custom_fit;
        caps["is_deterministic"] = is_deterministic;
        caps["algorithm_name"] = get_algorithm_name();
        return caps;
    }
};

/**
 * Runtime algorithm factory
 */
class AlgorithmFactory {
public:
    /**
     * Create algorithm instance from configuration
     */
    static py::dict create_algorithm_instance(const NestConfig& config);

    /**
     * Execute nesting with optimal algorithm selection
     */
    static py::dict execute_optimal_nesting(std::vector<Shape>& shapes,
                                          const Sheet& sheet,
                                          const NestConfig& config);

    /**
     * Benchmark different algorithm combinations
     */
    static py::dict benchmark_algorithms(std::vector<Shape>& shapes,
                                        const Sheet& sheet,
                                        const std::vector<std::string>& algorithm_names = {},
                                        int iterations = 3);

    /**
     * Recommend optimal algorithm for given shapes
     */
    static py::dict recommend_algorithm(const std::vector<Shape>& shapes,
                                       const Sheet& sheet);

    /**
     * Get algorithm performance characteristics
     */
    static py::dict get_algorithm_performance_profile(const std::string& algorithm_name);
};

/**
 * Template-based performance optimization utilities
 */
namespace performance {

    /**
     * Compile-time optimization hints
     */
    template<typename PlacerType, typename SelectorType>
    struct OptimizationHints {
        static constexpr bool prefer_parallel =
            std::is_same_v<SelectorType, LibNest2DFirstFitSelection>;

        static constexpr bool benefits_from_preprocessing =
            std::is_same_v<PlacerType, LibNest2DNfpPlacer>;

        static constexpr bool supports_batch_processing = true;

        static constexpr size_t recommended_batch_size =
            std::is_same_v<PlacerType, LibNest2DNfpPlacer> ? 50 : 100;
    };

    /**
     * Memory usage estimation
     */
    template<typename PlacerType, typename SelectorType>
    size_t estimate_memory_usage(size_t num_shapes, size_t avg_vertices_per_shape);

    /**
     * Performance profiling utilities
     */
    class PerformanceProfiler {
    private:
        std::chrono::steady_clock::time_point start_time_;
        std::string operation_name_;

    public:
        explicit PerformanceProfiler(const std::string& operation_name);
        ~PerformanceProfiler();

        static py::dict get_profiling_results();
        static void clear_profiling_data();
        static void enable_profiling(bool enable = true);
    };

} // namespace performance

/**
 * Type-safe configuration builders
 */
template<typename PlacerType, typename SelectorType>
class TypedConfigBuilder {
private:
    typename PlacerType::Config placer_config_;
    typename SelectorType::Config selector_config_;

public:
    TypedConfigBuilder() = default;

    TypedConfigBuilder& set_placer_config(const typename PlacerType::Config& config) {
        placer_config_ = config;
        return *this;
    }

    TypedConfigBuilder& set_selector_config(const typename SelectorType::Config& config) {
        selector_config_ = config;
        return *this;
    }

    auto build() -> LibNest2DNestConfig<PlacerType, SelectorType> {
        return LibNest2DNestConfig<PlacerType, SelectorType>(placer_config_, selector_config_);
    }

    static TypedConfigBuilder create_optimized_for_speed() {
        TypedConfigBuilder builder;
        // Set speed-optimized configurations
        return builder;
    }

    static TypedConfigBuilder create_optimized_for_quality() {
        TypedConfigBuilder builder;
        // Set quality-optimized configurations
        return builder;
    }
};

/**
 * Convenience type aliases for common algorithm combinations
 */
using FastNestingConfig = TypedConfigBuilder<LibNest2DBottomLeftPlacer, LibNest2DFirstFitSelection>;
using QualityNestingConfig = TypedConfigBuilder<LibNest2DNfpPlacer, LibNest2DDJDHeuristic>;
using BalancedNestingConfig = TypedConfigBuilder<LibNest2DNfpPlacer, LibNest2DFirstFitSelection>;

} // namespace nest2d_wrapper

#endif // NEST2D_METALOOPS_HPP
