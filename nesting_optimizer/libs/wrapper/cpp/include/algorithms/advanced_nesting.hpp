#ifndef NEST2D_ADVANCED_NESTING_HPP
#define NEST2D_ADVANCED_NESTING_HPP

#include "../core/types.hpp"
#include "../core/config.hpp"
#include "../core/optimizers.hpp"
#include "../core/parallel.hpp"
#include "../geometry/shape.hpp"
#include "../geometry/sheet.hpp"
#include "../geometry/advanced_geometry.hpp"
#include <pybind11/pybind11.h>
#include <vector>

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Advanced nesting algorithms with full LibNest2D feature coverage
 */
class AdvancedNesting {
public:
    /**
     * High-performance parallel nesting with optimization
     */
    static py::dict nest_shapes_advanced(std::vector<Shape>& shapes,
                                        const Sheet& sheet,
                                        const NestConfig& config = NestConfig());

    /**
     * Nesting with custom objective function optimization
     */
    static py::dict nest_with_optimization(std::vector<Shape>& shapes,
                                          const Sheet& sheet,
                                          py::function objective_function,
                                          const OptimizerConfig& opt_config = OptimizerConfig(),
                                          const NestConfig& nest_config = NestConfig());

    /**
     * Multi-threaded batch nesting for large datasets
     */
    static py::dict nest_batch_parallel(const std::vector<std::vector<Shape>>& shape_batches,
                                       const std::vector<Sheet>& sheets,
                                       const ParallelConfig& parallel_config = ParallelConfig(),
                                       const NestConfig& nest_config = NestConfig());

    /**
     * Adaptive nesting that adjusts configuration based on shape analysis
     */
    static py::dict nest_adaptive(std::vector<Shape>& shapes,
                                 const Sheet& sheet,
                                 const NestConfig& base_config = NestConfig());

    /**
     * Nesting with automatic rotation optimization
     */
    static py::dict nest_with_auto_rotation(std::vector<Shape>& shapes,
                                           const Sheet& sheet,
                                           double angle_resolution = 15.0,
                                           const OptimizerConfig& opt_config = OptimizerConfig(),
                                           const NestConfig& nest_config = NestConfig());

    /**
     * High-precision nesting for critical applications
     */
    static py::dict nest_high_precision(std::vector<Shape>& shapes,
                                       const Sheet& sheet,
                                       const NestConfig& config = NestConfig());

    /**
     * Nesting with detailed quality metrics and analysis
     */
    static py::dict nest_with_analysis(std::vector<Shape>& shapes,
                                      const Sheet& sheet,
                                      const NestConfig& config = NestConfig());

    /**
     * Nesting with custom NFP calculation callbacks
     */
    static py::dict nest_with_custom_nfp(std::vector<Shape>& shapes,
                                        const Sheet& sheet,
                                        py::function nfp_calculator,
                                        const NestConfig& config = NestConfig());

    /**
     * Progressive nesting with intermediate results
     */
    static py::dict nest_progressive(std::vector<Shape>& shapes,
                                   const Sheet& sheet,
                                   py::function progress_callback,
                                   const NestConfig& config = NestConfig());

    /**
     * Nesting with shape preprocessing and optimization
     */
    static py::dict nest_with_preprocessing(std::vector<Shape>& shapes,
                                           const Sheet& sheet,
                                           bool remove_collinear = true,
                                           bool snap_to_grid = false,
                                           double grid_size = 0.001,
                                           const NestConfig& config = NestConfig());
};

/**
 * Specialized nesting algorithms for specific industries
 */
class IndustrySpecificNesting {
public:
    /**
     * Metal cutting optimization with kerf considerations
     */
    static py::dict nest_metal_cutting(std::vector<Shape>& shapes,
                                      const Sheet& sheet,
                                      double kerf_width = 2.0,
                                      double lead_in_length = 5.0,
                                      const NestConfig& config = NestConfig());

    /**
     * Fabric cutting with grain direction constraints
     */
    static py::dict nest_fabric_cutting(std::vector<Shape>& shapes,
                                       const Sheet& sheet,
                                       const std::vector<double>& grain_directions,
                                       bool respect_grain = true,
                                       const NestConfig& config = NestConfig());

    /**
     * Glass cutting with break line optimization
     */
    static py::dict nest_glass_cutting(std::vector<Shape>& shapes,
                                      const Sheet& sheet,
                                      bool minimize_breaklines = true,
                                      double min_strip_width = 50.0,
                                      const NestConfig& config = NestConfig());

    /**
     * 3D printing layout optimization
     */
    static py::dict nest_3d_printing(std::vector<Shape>& shapes,
                                    const Sheet& sheet,
                                    double support_distance = 5.0,
                                    bool group_similar_heights = true,
                                    const NestConfig& config = NestConfig());
};

/**
 * Quality assessment and optimization utilities
 */
class NestingQuality {
public:
    /**
     * Calculate comprehensive quality metrics for a nesting result
     */
    static py::dict calculate_quality_metrics(const py::dict& nesting_result,
                                             const Sheet& sheet);

    /**
     * Compare multiple nesting results and rank them
     */
    static py::list rank_nesting_results(const std::vector<py::dict>& results,
                                        const std::vector<std::string>& criteria = {"area_utilization", "waste", "part_count"});

    /**
     * Optimize existing nesting result through local improvements
     */
    static py::dict optimize_existing_nesting(const py::dict& nesting_result,
                                             const Sheet& sheet,
                                             const OptimizerConfig& opt_config = OptimizerConfig());

    /**
     * Validate nesting result for manufacturing constraints
     */
    static py::dict validate_for_manufacturing(const py::dict& nesting_result,
                                              double min_distance = 1.0,
                                              double min_feature_size = 0.5,
                                              bool check_accessibility = true);
};

/**
 * Experimental and research algorithms
 */
class ExperimentalNesting {
public:
    /**
     * AI-guided nesting using machine learning heuristics
     */
    static py::dict nest_ai_guided(std::vector<Shape>& shapes,
                                  const Sheet& sheet,
                                  py::function ml_model = py::function(),
                                  const NestConfig& config = NestConfig());

    /**
     * Genetic algorithm-based nesting optimization
     */
    static py::dict nest_genetic_algorithm(std::vector<Shape>& shapes,
                                          const Sheet& sheet,
                                          int population_size = 50,
                                          int generations = 100,
                                          double mutation_rate = 0.1,
                                          const NestConfig& config = NestConfig());

    /**
     * Simulated annealing optimization
     */
    static py::dict nest_simulated_annealing(std::vector<Shape>& shapes,
                                            const Sheet& sheet,
                                            double initial_temperature = 100.0,
                                            double cooling_rate = 0.95,
                                            int iterations = 1000,
                                            const NestConfig& config = NestConfig());

    /**
     * Multi-objective optimization balancing multiple criteria
     */
    static py::dict nest_multi_objective(std::vector<Shape>& shapes,
                                        const Sheet& sheet,
                                        const std::vector<std::string>& objectives,
                                        const std::vector<double>& weights,
                                        const OptimizerConfig& opt_config = OptimizerConfig(),
                                        const NestConfig& nest_config = NestConfig());
};

} // namespace nest2d_wrapper

#endif // NEST2D_ADVANCED_NESTING_HPP
