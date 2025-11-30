#ifndef NEST2D_OPTIMIZERS_HPP
#define NEST2D_OPTIMIZERS_HPP

#include "types.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>

// Include LibNest2D optimizers if available
#ifdef LIBNEST2D_AVAILABLE
#ifdef LIBNEST2D_OPTIMIZER_nlopt
#include <libnest2d/optimizers/nlopt/genetic.hpp>
#include <libnest2d/optimizers/nlopt/subplex.hpp>
#include <libnest2d/optimizers/nlopt/simplex.hpp>
#endif
#include <libnest2d/optimizer.hpp>
#endif
#include <functional>
#include <vector>
#include <string>

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Optimization method enumeration
 */
enum class OptimizationMethod {
    GENETIC,
    SUBPLEX,
    SIMPLEX,
    NLOPT_LN_NELDERMEAD,
    NLOPT_LN_SBPLX,
    NLOPT_GN_GENETIC,
    NLOPT_GN_ESCH,
    CUSTOM
};

/**
 * Stop criteria for optimization
 */
class StopCriteria {
public:
    double relative_tolerance = 1e-6;
    double absolute_tolerance = 1e-12;
    int max_evaluations = 1000;
    double max_time_seconds = 30.0;

    StopCriteria() = default;
    StopCriteria(double rel_tol, double abs_tol, int max_evals, double max_time = 30.0)
        : relative_tolerance(rel_tol), absolute_tolerance(abs_tol),
          max_evaluations(max_evals), max_time_seconds(max_time) {}

#ifdef LIBNEST2D_OPTIMIZER_nlopt
    libnest2d::opt::StopCriteria to_internal() const {
        libnest2d::opt::StopCriteria criteria;
        criteria.relative_score_difference = relative_tolerance;
        criteria.absolute_score_difference = absolute_tolerance;
        criteria.max_iterations = max_evaluations;
        criteria.stop_score = std::numeric_limits<double>::lowest();
        return criteria;
    }
#endif

    std::string to_string() const {
        return "StopCriteria(rel_tol=" + std::to_string(relative_tolerance) +
               ", abs_tol=" + std::to_string(absolute_tolerance) +
               ", max_evals=" + std::to_string(max_evaluations) +
               ", max_time=" + std::to_string(max_time_seconds) + ")";
    }
};

/**
 * Optimization configuration
 */
class OptimizerConfig {
public:
    OptimizationMethod method = OptimizationMethod::SUBPLEX;
    StopCriteria stop_criteria;
    OptimizationMethod local_method = OptimizationMethod::SUBPLEX; // For global optimizers
    unsigned long random_seed = 0; // 0 means auto-generate
    bool use_local_optimizer = false;

    // Custom objective function (optional)
    py::function custom_objective;

    OptimizerConfig() = default;
    OptimizerConfig(OptimizationMethod m, const StopCriteria& criteria = StopCriteria())
        : method(m), stop_criteria(criteria) {}

    std::string to_string() const {
        std::string method_str = optimization_method_to_string(method);
        return "OptimizerConfig(method=" + method_str +
               ", " + stop_criteria.to_string() + ")";
    }

private:
    std::string optimization_method_to_string(OptimizationMethod method) const {
        switch (method) {
            case OptimizationMethod::GENETIC: return "GENETIC";
            case OptimizationMethod::SUBPLEX: return "SUBPLEX";
            case OptimizationMethod::SIMPLEX: return "SIMPLEX";
            case OptimizationMethod::NLOPT_LN_NELDERMEAD: return "NLOPT_LN_NELDERMEAD";
            case OptimizationMethod::NLOPT_LN_SBPLX: return "NLOPT_LN_SBPLX";
            case OptimizationMethod::NLOPT_GN_GENETIC: return "NLOPT_GN_GENETIC";
            case OptimizationMethod::NLOPT_GN_ESCH: return "NLOPT_GN_ESCH";
            case OptimizationMethod::CUSTOM: return "CUSTOM";
            default: return "UNKNOWN";
        }
    }
};

/**
 * Wrapper for LibNest2D optimizers
 */
class OptimizerWrapper {
private:
    OptimizerConfig config_;

public:
    explicit OptimizerWrapper(const OptimizerConfig& config = OptimizerConfig())
        : config_(config) {}

#ifdef LIBNEST2D_OPTIMIZER_nlopt
    /**
     * Create a genetic optimizer
     */
    libnest2d::opt::GeneticOptimizer create_genetic_optimizer() const {
        auto optimizer = libnest2d::opt::GeneticOptimizer(config_.stop_criteria.to_internal());
        if (config_.use_local_optimizer) {
            optimizer.localMethod(nlopt_method_to_internal(config_.local_method));
        }
        if (config_.random_seed != 0) {
            optimizer.seed(config_.random_seed);
        }
        return optimizer;
    }

    /**
     * Create a subplex optimizer
     */
    auto create_subplex_optimizer() const {
        return libnest2d::opt::TOptimizer<libnest2d::opt::Method::L_SUBPLEX>(
            config_.stop_criteria.to_internal());
    }

    /**
     * Create a simplex optimizer
     */
    auto create_simplex_optimizer() const {
        return libnest2d::opt::TOptimizer<libnest2d::opt::Method::L_SIMPLEX>(
            config_.stop_criteria.to_internal());
    }

private:
    libnest2d::opt::Method nlopt_method_to_internal(OptimizationMethod method) const {
        switch (method) {
            case OptimizationMethod::GENETIC: return libnest2d::opt::Method::G_GENETIC;
            case OptimizationMethod::SUBPLEX: return libnest2d::opt::Method::L_SUBPLEX;
            case OptimizationMethod::SIMPLEX: return libnest2d::opt::Method::L_SIMPLEX;
            default: return libnest2d::opt::Method::L_SUBPLEX;
        }
    }
#endif

public:
    /**
     * Optimize a function with bounds
     */
    py::dict optimize_function(py::function objective,
                              const std::vector<std::pair<double, double>>& bounds,
                              const std::vector<double>& initial_guess = {}) const;

    /**
     * Get current configuration
     */
    const OptimizerConfig& get_config() const { return config_; }
    void set_config(const OptimizerConfig& config) { config_ = config; }

    /**
     * Factory methods for common optimizer configurations
     */
    static OptimizerConfig create_fast_config() {
        return OptimizerConfig(OptimizationMethod::SIMPLEX,
                             StopCriteria(1e-3, 1e-6, 100, 10.0));
    }

    static OptimizerConfig create_quality_config() {
        OptimizerConfig config(OptimizationMethod::GENETIC,
                             StopCriteria(1e-6, 1e-12, 2000, 120.0));
        config.use_local_optimizer = true;
        config.local_method = OptimizationMethod::SUBPLEX;
        return config;
    }

    static OptimizerConfig create_balanced_config() {
        return OptimizerConfig(OptimizationMethod::SUBPLEX,
                             StopCriteria(1e-4, 1e-9, 500, 60.0));
    }
};

/**
 * Utility functions for optimization
 */
namespace optimization_utils {

    /**
     * Convert Python bounds to LibNest2D bounds
     */
    template<typename T>
    std::vector<libnest2d::opt::Bound<T>> python_bounds_to_internal(
        const std::vector<std::pair<double, double>>& bounds) {
        std::vector<libnest2d::opt::Bound<T>> result;
        result.reserve(bounds.size());
        for (const auto& bound : bounds) {
            result.emplace_back(static_cast<T>(bound.first), static_cast<T>(bound.second));
        }
        return result;
    }

    /**
     * Optimize polygon position using LibNest2D optimizers
     */
    py::dict optimize_polygon_position(const std::vector<std::vector<double>>& polygon,
                                      const std::vector<std::vector<std::vector<double>>>& obstacles,
                                      double min_x, double max_x, double min_y, double max_y,
                                      const OptimizerConfig& config = OptimizerConfig());

    /**
     * Find optimal rotation angles for a set of shapes
     */
    std::vector<double> find_optimal_rotations(const std::vector<std::vector<std::vector<double>>>& shapes,
                                              double angle_resolution = 45.0,
                                              const OptimizerConfig& config = OptimizerConfig());

} // namespace optimization_utils

} // namespace nest2d_wrapper

#endif // NEST2D_OPTIMIZERS_HPP
