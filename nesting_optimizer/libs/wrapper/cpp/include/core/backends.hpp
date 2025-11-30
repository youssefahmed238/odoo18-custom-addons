#ifndef NEST2D_BACKENDS_HPP
#define NEST2D_BACKENDS_HPP

#include "types.hpp"
#include <pybind11/pybind11.h>
#include <string>
#include <vector>

// Include backend-specific headers
#ifdef LIBNEST2D_GEOMETRIES_clipper
#include <libnest2d/backends/clipper/geometries.hpp>
#endif

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Backend configuration and management
 */
class BackendManager {
public:
    enum class GeometryBackend {
        CLIPPER,
        BOOST_GEOMETRY,
        CGAL,
        CUSTOM
    };

    enum class OptimizerBackend {
        NLOPT,
        OPTIMLIB,
        CUSTOM
    };

    /**
     * Get information about available backends
     */
    static py::dict get_available_backends();

    /**
     * Get current geometry backend
     */
    static std::string get_current_geometry_backend();

    /**
     * Get current optimizer backend
     */
    static std::string get_current_optimizer_backend();

    /**
     * Get backend capabilities
     */
    static py::dict get_backend_capabilities(const std::string& backend_name);

    /**
     * Check if specific backend feature is available
     */
    static bool is_feature_available(const std::string& feature_name);
};

/**
 * Clipper backend specific functionality
 */
#ifdef LIBNEST2D_GEOMETRIES_clipper
class ClipperBackend {
public:
    /**
     * Advanced clipping operations with Clipper-specific options
     */
    static py::dict advanced_boolean_operation(const std::vector<std::vector<double>>& subject,
                                              const std::vector<std::vector<double>>& clip,
                                              const std::string& operation,
                                              const py::dict& clipper_options = py::dict());

    /**
     * Polygon offsetting with advanced options
     */
    static std::vector<std::vector<std::vector<double>>> advanced_offset(
        const std::vector<std::vector<double>>& polygon,
        double distance,
        const std::string& join_type = "round",
        const std::string& end_type = "closed_polygon",
        double miter_limit = 2.0,
        double arc_tolerance = 0.25);

    /**
     * Minkowski sum using Clipper
     */
    static std::vector<std::vector<double>> clipper_minkowski_sum(
        const std::vector<std::vector<double>>& poly1,
        const std::vector<std::vector<double>>& poly2,
        bool use_full_range = false);

    /**
     * Clean polygon using Clipper's cleaning algorithms
     */
    static std::vector<std::vector<double>> clipper_clean_polygon(
        const std::vector<std::vector<double>>& polygon,
        double distance = 1.415);

    /**
     * Simplify polygon using Clipper's Douglas-Peucker algorithm
     */
    static std::vector<std::vector<double>> clipper_simplify_polygon(
        const std::vector<std::vector<double>>& polygon,
        double tolerance = 1.0);

    /**
     * Get Clipper library version and build information
     */
    static py::dict get_clipper_info();

    /**
     * Set Clipper-specific precision settings
     */
    static void set_clipper_precision(int coordinate_precision = 1000000);
};
#endif

/**
 * NLopt optimizer backend functionality
 */
#ifdef LIBNEST2D_OPTIMIZER_nlopt
class NloptBackend {
public:
    /**
     * Get available NLopt algorithms
     */
    static std::vector<std::string> get_available_algorithms();

    /**
     * Get algorithm information
     */
    static py::dict get_algorithm_info(const std::string& algorithm_name);

    /**
     * Set global NLopt options
     */
    static void set_global_options(const py::dict& options);

    /**
     * Custom optimization with full NLopt control
     */
    static py::dict custom_optimization(py::function objective,
                                       const std::vector<std::pair<double, double>>& bounds,
                                       const std::string& algorithm,
                                       const py::dict& options = py::dict(),
                                       const std::vector<double>& initial_guess = {});

    /**
     * Multi-objective optimization
     */
    static py::dict multi_objective_optimization(const std::vector<py::function>& objectives,
                                                const std::vector<std::pair<double, double>>& bounds,
                                                const std::vector<double>& weights,
                                                const std::string& algorithm = "NLOPT_GN_NSGA2");

    /**
     * Get NLopt version information
     */
    static py::dict get_nlopt_info();
};
#endif

/**
 * Threading backend management
 */
class ThreadingBackend {
public:
    enum class ThreadingLibrary {
        STD_THREAD,
        TBB,
        OPENMP,
        NONE
    };

    /**
     * Get available threading backends
     */
    static std::vector<std::string> get_available_threading_backends();

    /**
     * Set active threading backend
     */
    static bool set_active_backend(const std::string& backend_name);

    /**
     * Get current threading backend information
     */
    static py::dict get_threading_info();

    /**
     * Benchmark threading performance
     */
    static py::dict benchmark_threading(int num_threads = -1, int workload_size = 10000);

#ifdef LIBNEST2D_THREADING_tbb
    /**
     * TBB-specific configuration
     */
    static void configure_tbb(int num_threads = -1, const std::string& scheduler = "auto");
    static py::dict get_tbb_info();
#endif

#ifdef LIBNEST2D_THREADING_omp
    /**
     * OpenMP-specific configuration
     */
    static void configure_openmp(int num_threads = -1, const std::string& schedule = "dynamic");
    static py::dict get_openmp_info();
#endif
};

/**
 * Memory management for large-scale operations
 */
class MemoryBackend {
public:
    /**
     * Configure memory usage limits
     */
    static void set_memory_limits(size_t max_memory_mb = 0); // 0 = unlimited

    /**
     * Get current memory usage statistics
     */
    static py::dict get_memory_usage();

    /**
     * Enable memory debugging
     */
    static void enable_memory_debugging(bool enable = true);

    /**
     * Memory-efficient operations for large datasets
     */
    static py::dict process_large_dataset_chunked(const py::list& large_dataset,
                                                 py::function processor,
                                                 size_t chunk_size = 1000);

    /**
     * Memory pool management
     */
    static void enable_memory_pool(bool enable = true);
    static py::dict get_memory_pool_stats();
};

/**
 * Cross-platform compatibility utilities
 */
class PlatformBackend {
public:
    /**
     * Get platform-specific information
     */
    static py::dict get_platform_info();

    /**
     * Get CPU capabilities
     */
    static py::dict get_cpu_capabilities();

    /**
     * Platform-specific optimizations
     */
    static void enable_platform_optimizations(bool enable = true);

    /**
     * Check for SIMD support
     */
    static py::dict get_simd_support();

    /**
     * Platform-specific file I/O
     */
    static py::dict read_file_optimized(const std::string& filename);
    static bool write_file_optimized(const std::string& filename, const py::dict& data);
};

/**
 * Backend feature detection and runtime configuration
 */
class FeatureDetector {
public:
    /**
     * Detect all available features at runtime
     */
    static py::dict detect_all_features();

    /**
     * Check specific feature availability
     */
    static bool check_feature(const std::string& feature_name);

    /**
     * Get recommended configuration for current system
     */
    static py::dict get_recommended_config();

    /**
     * Benchmark system capabilities
     */
    static py::dict benchmark_system_capabilities();

    /**
     * Get feature compatibility matrix
     */
    static py::dict get_feature_compatibility();
};

/**
 * Backend integration utilities
 */
namespace backend_utils {

    /**
     * Convert between different backend representations
     */
    py::dict convert_between_backends(const py::dict& data,
                                    const std::string& from_backend,
                                    const std::string& to_backend);

    /**
     * Validate backend compatibility
     */
    bool validate_backend_combination(const std::vector<std::string>& backends);

    /**
     * Get optimal backend configuration for specific use case
     */
    py::dict get_optimal_backend_config(const std::string& use_case,
                                       const py::dict& constraints = py::dict());

    /**
     * Backend performance profiling
     */
    py::dict profile_backend_performance(const std::string& backend_name,
                                        const py::dict& test_data);

} // namespace backend_utils

} // namespace nest2d_wrapper

#endif // NEST2D_BACKENDS_HPP
