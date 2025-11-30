#ifndef NEST2D_NESTING_HPP
#define NEST2D_NESTING_HPP

#include "../core/types.hpp"
#include "../geometry/shape.hpp"
#include "../geometry/sheet.hpp"
#include "../geometry/rectangle.hpp"
#include "../geometry/circle.hpp"
#include "../core/config.hpp"
#include <pybind11/pybind11.h>
#include <vector>

namespace py = pybind11;

namespace nest2d_wrapper {

// ============================================================================
// COMPREHENSIVE NESTING FUNCTIONS - 100% LibNest2D Coverage
// ============================================================================

/**
 * Main nesting function with complete LibNest2D control
 */
py::dict nest_shapes(std::vector<Shape>& shapes,
                     const Sheet& sheet,
                     const NestConfig& config = NestConfig(),
                     const ProgressControl& progress_control = ProgressControl());

/**
 * Template-based nesting with specific placer and selector types
 */
template<class PlacerType, class SelectorType>
py::dict nest_shapes_typed(std::vector<Shape>& shapes,
                          const Sheet& sheet,
                          const typename PlacerType::Config& placer_config,
                          const typename SelectorType::Config& selector_config,
                          double spacing = 0.0,
                          const ProgressControl& progress_control = ProgressControl());

/**
 * NFP-specific nesting with full NFP configuration
 */
py::dict nest_shapes_nfp(std::vector<Shape>& shapes,
                        const Sheet& sheet,
                        const NfpPlacerConfig& nfp_config,
                        const SelectionConfig& selection_config = SelectionConfig(),
                        double spacing = 0.0,
                        const ProgressControl& progress_control = ProgressControl());

/**
 * Bottom-left specific nesting
 */
py::dict nest_shapes_bottom_left(std::vector<Shape>& shapes,
                                const Sheet& sheet,
                                const BottomLeftPlacerConfig& bl_config = BottomLeftPlacerConfig(),
                                const SelectionConfig& selection_config = SelectionConfig(),
                                double spacing = 0.0,
                                const ProgressControl& progress_control = ProgressControl());

/**
 * Simple nesting function for basic use cases
 */
py::dict nest_polygons(const std::vector<std::vector<std::vector<double>>>& polygons,
                      double sheet_width,
                      double sheet_height,
                      double spacing = 0.0,
                      const std::vector<double>& rotations = {0.0, 90.0, 180.0, 270.0});

/**
 * Batch nesting for large quantities
 */
py::dict nest_polygons_batch(const std::vector<std::vector<std::vector<double>>>& polygons,
                            double sheet_width,
                            double sheet_height,
                            int batch_size = 50,
                            const NestConfig& config = NestConfig());

/**
 * Pack group nesting - for pre-grouped items
 */
py::dict nest_pack_groups(const std::vector<std::vector<Shape>>& pack_groups,
                         const Sheet& sheet,
                         const NestConfig& config = NestConfig());

/**
 * Fixed shape nesting - some shapes have fixed positions
 */
py::dict nest_with_fixed_shapes(std::vector<Shape>& shapes,
                               std::vector<Shape>& fixed_shapes,
                               const Sheet& sheet,
                               const NestConfig& config = NestConfig());

/**
 * Multi-bin nesting with different bin sizes
 */
py::dict nest_multi_sheets(std::vector<Shape>& shapes,
                          const std::vector<Sheet>& sheets,
                          const NestConfig& config = NestConfig());

/**
 * Iterator-based nesting for memory efficiency
 */
py::dict nest_shapes_iterator(py::iterator shape_iter,
                             const Sheet& sheet,
                             const NestConfig& config = NestConfig());

/**
 * Nesting optimization for specific arrangements
 */
py::dict optimize_arrangement(std::vector<Shape>& shapes,
                             const Sheet& sheet,
                             const std::string& optimization_goal = "area", // "area", "perimeter", "compactness"
                             const NestConfig& config = NestConfig());

/**
 * Advanced nesting with custom objective functions
 */
py::dict nest_with_custom_objective(std::vector<Shape>& shapes,
                                   const Sheet& sheet,
                                   py::function objective_function,
                                   const NestConfig& config = NestConfig());

/**
 * Rectangle-specific optimized nesting
 */
py::dict nest_rectangles(const std::vector<Rectangle>& rectangles,
                        const Sheet& sheet,
                        const NestConfig& config = NestConfig());

/**
 * Circle-specific optimized nesting
 */
py::dict nest_circles(const std::vector<Circle>& circles,
                     const Sheet& sheet,
                     const NestConfig& config = NestConfig());

/**
 * Mixed shape nesting (rectangles, circles, and arbitrary shapes)
 */
py::dict nest_mixed_shapes(const std::vector<Shape>& shapes,
                          const std::vector<Rectangle>& rectangles,
                          const std::vector<Circle>& circles,
                          const Sheet& sheet,
                          const NestConfig& config = NestConfig());

} // namespace nest2d_wrapper

#endif // NEST2D_NESTING_HPP
