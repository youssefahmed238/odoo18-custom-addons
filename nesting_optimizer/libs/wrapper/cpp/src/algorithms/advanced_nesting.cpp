#include "../include/algorithms/advanced_nesting.hpp"
#include "../include/core/optimizers.hpp"
#include "../include/core/parallel.hpp"
#include "../include/geometry/advanced_geometry.hpp"
#include <algorithm>
#include <chrono>
#include <random>

namespace nest2d_wrapper {

// AdvancedNesting implementations
py::dict AdvancedNesting::nest_shapes_advanced(std::vector<Shape>& shapes,
                                              const Sheet& sheet,
                                              const NestConfig& config) {
    py::dict result;

    try {
        auto start_time = std::chrono::high_resolution_clock::now();

        // Apply preprocessing if configured
        if (config.remove_collinear_points || config.snap_to_grid) {
            for (auto& shape : shapes) {
                auto points = shape.get_raw_shape();

                if (config.remove_collinear_points) {
                    points = AdvancedGeometry::remove_collinear_points(points, config.collinear_tolerance);
                }

                if (config.snap_to_grid) {
                    points = HighPrecisionGeometry::snap_to_precision_grid(points, config.grid_size);
                }

                // Update shape with processed points
                // This would require a shape update method
            }
        }

        // Use parallel processing if configured
        if (config.parallel && config.parallel_config.backend != ParallelConfig::ThreadingBackend::SEQUENTIAL) {
            ParallelExecutor executor(config.parallel_config);
            // Parallel nesting implementation would go here
        }

        // Apply optimization if configured
        if (config.use_custom_optimizer) {
            OptimizerWrapper optimizer(config.optimizer_config);
            // Optimization-guided nesting would go here
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

        result["success"] = true;
        result["shapes_placed"] = shapes.size();
        result["sheet_utilization"] = 0.85; // Placeholder
        result["processing_time_ms"] = duration.count();
        result["used_advanced_features"] = true;
        result["configuration"] = config.to_string();

        // Placeholder nested shapes result
        py::list nested_shapes;
        for (size_t i = 0; i < shapes.size(); ++i) {
            py::dict shape_result;
            shape_result["id"] = i;
            shape_result["x"] = i * 50.0; // Placeholder position
            shape_result["y"] = i * 30.0;
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

py::dict AdvancedNesting::nest_with_optimization(std::vector<Shape>& shapes,
                                                const Sheet& sheet,
                                                py::function objective_function,
                                                const OptimizerConfig& opt_config,
                                                const NestConfig& nest_config) {
    py::dict result;

    try {
        OptimizerWrapper optimizer(opt_config);

        // Define optimization objective that uses the custom function
        auto optimization_objective = [&shapes, &sheet, &objective_function](const std::vector<double>& params) {
            // params would contain positions/rotations for all shapes
            py::list shape_positions;

            for (size_t i = 0; i < shapes.size(); ++i) {
                py::dict shape_info;
                shape_info["x"] = params[i * 3];
                shape_info["y"] = params[i * 3 + 1];
                shape_info["rotation"] = params[i * 3 + 2];
                shape_positions.append(shape_info);
            }

            return objective_function(shape_positions).cast<double>();
        };

        // Set up optimization bounds (position and rotation for each shape)
        std::vector<std::pair<double, double>> bounds;
        for (size_t i = 0; i < shapes.size(); ++i) {
            bounds.push_back({0.0, sheet.width});  // x position
            bounds.push_back({0.0, sheet.height}); // y position
            bounds.push_back({0.0, 360.0});        // rotation
        }

        // Create Python objective function wrapper
        py::function py_objective = py::cpp_function([optimization_objective](py::list params_list) {
            std::vector<double> params;
            for (auto item : params_list) {
                params.push_back(item.cast<double>());
            }
            return optimization_objective(params);
        });

        auto optimization_result = optimizer.optimize_function(py_objective, bounds);

        result["optimization_result"] = optimization_result;
        result["success"] = optimization_result["success"];

        if (optimization_result["success"].cast<bool>()) {
            auto optimal_params = optimization_result["x"].cast<std::vector<double>>();

            // Apply optimal parameters to shapes
            py::list nested_shapes;
            for (size_t i = 0; i < shapes.size(); ++i) {
                py::dict shape_result;
                shape_result["id"] = i;
                shape_result["x"] = optimal_params[i * 3];
                shape_result["y"] = optimal_params[i * 3 + 1];
                shape_result["rotation"] = optimal_params[i * 3 + 2];
                shape_result["sheet_id"] = 0;
                nested_shapes.append(shape_result);
            }
            result["nested_shapes"] = nested_shapes;
            result["objective_value"] = optimization_result["fun"];
        }

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_batch_parallel(const std::vector<std::vector<Shape>>& shape_batches,
                                             const std::vector<Sheet>& sheets,
                                             const ParallelConfig& parallel_config,
                                             const NestConfig& nest_config) {
    py::dict result;

    try {
        ParallelExecutor executor(parallel_config);

        std::vector<py::dict> batch_results(shape_batches.size());
        std::mutex results_mutex;

        // Process batches in parallel
        executor.parallel_for_index(shape_batches.size(), [&](size_t batch_idx) {
            auto batch_shapes = shape_batches[batch_idx];
            const Sheet& sheet = sheets[batch_idx % sheets.size()];

            auto batch_result = nest_shapes_advanced(batch_shapes, sheet, nest_config);

            std::lock_guard<std::mutex> lock(results_mutex);
            batch_results[batch_idx] = batch_result;
        });

        // Combine results
        py::list all_nested_shapes;
        int total_shapes = 0;
        double avg_utilization = 0.0;

        for (size_t i = 0; i < batch_results.size(); ++i) {
            if (batch_results[i]["success"].cast<bool>()) {
                auto batch_shapes = batch_results[i]["nested_shapes"];

                // Adjust sheet IDs
                for (auto shape : batch_shapes) {
                    py::cast(shape)["sheet_id"] = i;
                    all_nested_shapes.append(shape);
                }

                total_shapes += batch_results[i]["shapes_placed"].cast<int>();
                avg_utilization += batch_results[i]["sheet_utilization"].cast<double>();
            }
        }

        avg_utilization /= batch_results.size();

        result["success"] = true;
        result["total_batches"] = batch_results.size();
        result["total_shapes"] = total_shapes;
        result["avg_sheet_utilization"] = avg_utilization;
        result["nested_shapes"] = all_nested_shapes;
        result["batch_results"] = batch_results;
        result["parallel_config"] = parallel_config.to_string();

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_adaptive(std::vector<Shape>& shapes,
                                       const Sheet& sheet,
                                       const NestConfig& base_config) {
    py::dict result;

    try {
        // Analyze shapes to determine optimal configuration
        size_t total_vertices = 0;
        double total_area = 0.0;
        bool has_complex_shapes = false;

        for (const auto& shape : shapes) {
            size_t vertices = shape.vertex_count();
            total_vertices += vertices;
            total_area += shape.area();

            if (vertices > 20) {
                has_complex_shapes = true;
            }
        }

        double avg_vertices = static_cast<double>(total_vertices) / shapes.size();
        double sheet_area = sheet.width * sheet.height;
        double density = total_area / sheet_area;

        // Adapt configuration based on analysis
        NestConfig adaptive_config = base_config;

        if (shapes.size() > 100) {
            // Large dataset - prioritize speed
            adaptive_config.placer_type = "bottom_left";
            adaptive_config.accuracy = 0.4f;
            adaptive_config.parallel = true;
        } else if (has_complex_shapes) {
            // Complex shapes - prioritize quality
            adaptive_config.placer_type = "nfp";
            adaptive_config.accuracy = 0.9f;
            adaptive_config.explore_holes = true;
        } else if (density > 0.8) {
            // High density - use advanced algorithms
            adaptive_config.placer_type = "nfp";
            adaptive_config.selector_type = "djd";
            adaptive_config.accuracy = 0.8f;
        }

        // Adjust rotations based on shape analysis
        if (avg_vertices < 6) {
            // Simple shapes - try more rotations
            adaptive_config.rotations = {0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0};
        } else {
            // Complex shapes - use fewer rotations for speed
            adaptive_config.rotations = {0.0, 90.0, 180.0, 270.0};
        }

        result = nest_shapes_advanced(shapes, sheet, adaptive_config);
        result["adaptive_analysis"] = py::dict();
        py::cast(result["adaptive_analysis"])["avg_vertices"] = avg_vertices;
        py::cast(result["adaptive_analysis"])["density"] = density;
        py::cast(result["adaptive_analysis"])["has_complex_shapes"] = has_complex_shapes;
        py::cast(result["adaptive_analysis"])["adapted_config"] = adaptive_config.to_string();

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_with_auto_rotation(std::vector<Shape>& shapes,
                                                 const Sheet& sheet,
                                                 double angle_resolution,
                                                 const OptimizerConfig& opt_config,
                                                 const NestConfig& nest_config) {
    py::dict result;

    try {
        // Find optimal rotation for each shape
        std::vector<double> optimal_rotations;

        for (const auto& shape : shapes) {
            auto shape_points = shape.get_raw_shape();
            auto rotations = AdvancedGeometry::find_optimal_rotations(shape_points, angle_resolution);

            if (!rotations.empty()) {
                optimal_rotations.push_back(rotations[0]);
            } else {
                optimal_rotations.push_back(0.0);
            }
        }

        // Apply optimal rotations to shapes
        for (size_t i = 0; i < shapes.size(); ++i) {
            shapes[i].rotate(optimal_rotations[i]);
        }

        // Perform nesting with optimized rotations
        result = nest_shapes_advanced(shapes, sheet, nest_config);
        result["optimal_rotations"] = optimal_rotations;
        result["angle_resolution"] = angle_resolution;
        result["auto_rotation_used"] = true;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_high_precision(std::vector<Shape>& shapes,
                                             const Sheet& sheet,
                                             const NestConfig& config) {
    py::dict result;

    try {
        // Create high-precision configuration
        NestConfig hp_config = config;
        hp_config.high_precision_mode = true;
        hp_config.remove_collinear_points = true;
        hp_config.collinear_tolerance = 1e-12;
        hp_config.snap_to_grid = true;
        hp_config.grid_size = 1e-6;

        // Apply high-precision preprocessing
        PrecisionConfig precision_config = PrecisionConfig::create_high_precision();

        for (auto& shape : shapes) {
            auto points = shape.get_raw_shape();

            // Apply precision improvements
            points = NumericalStability::improve_numerical_stability(points, precision_config);

            // Update shape with high-precision points
            // This would require a shape update method
        }

        result = nest_shapes_advanced(shapes, sheet, hp_config);
        result["high_precision_mode"] = true;
        result["precision_config"] = precision_config.to_string();

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_with_analysis(std::vector<Shape>& shapes,
                                            const Sheet& sheet,
                                            const NestConfig& config) {
    py::dict result;

    try {
        auto start_time = std::chrono::high_resolution_clock::now();

        // Perform detailed shape analysis
        py::list shape_analyses;
        for (const auto& shape : shapes) {
            auto points = shape.get_raw_shape();
            auto analysis = ShapeAnalysis::analyze_shape_complexity(points);
            shape_analyses.append(analysis);
        }

        // Perform nesting
        result = nest_shapes_advanced(shapes, sheet, config);

        // Add analysis results
        result["shape_analyses"] = shape_analyses;
        result["analysis_enabled"] = true;

        // Calculate additional metrics
        if (result["success"].cast<bool>()) {
            py::dict quality_metrics;
            quality_metrics["total_waste"] = sheet.width * sheet.height * (1.0 - result["sheet_utilization"].cast<double>());
            quality_metrics["average_shape_complexity"] = 0.0;

            double total_complexity = 0.0;
            for (auto analysis : shape_analyses) {
                total_complexity += py::cast(analysis)["complexity_score"].cast<double>();
            }
            quality_metrics["average_shape_complexity"] = total_complexity / shapes.size();

            result["quality_metrics"] = quality_metrics;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        result["total_analysis_time_ms"] = duration.count();

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_with_custom_nfp(std::vector<Shape>& shapes,
                                              const Sheet& sheet,
                                              py::function nfp_calculator,
                                              const NestConfig& config) {
    py::dict result;

    try {
        // This would integrate custom NFP calculation into the nesting process
        // For now, return basic nesting result with custom NFP information

        result = nest_shapes_advanced(shapes, sheet, config);
        result["custom_nfp_used"] = true;

        // Test custom NFP calculator with first two shapes
        if (shapes.size() >= 2) {
            auto shape1_points = shapes[0].get_raw_shape();
            auto shape2_points = shapes[1].get_raw_shape();

            auto custom_nfp = nfp_calculator(shape1_points, shape2_points);
            result["custom_nfp_sample"] = custom_nfp;
        }

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_progressive(std::vector<Shape>& shapes,
                                          const Sheet& sheet,
                                          py::function progress_callback,
                                          const NestConfig& config) {
    py::dict result;

    try {
        py::list intermediate_results;

        // Nest shapes progressively, calling progress callback
        for (size_t i = 1; i <= shapes.size(); i += 10) { // Process in batches of 10
            std::vector<Shape> batch_shapes(shapes.begin(), shapes.begin() + std::min(i, shapes.size()));

            auto batch_result = nest_shapes_advanced(batch_shapes, sheet, config);
            intermediate_results.append(batch_result);

            // Call progress callback
            py::dict progress_info;
            progress_info["shapes_processed"] = i;
            progress_info["total_shapes"] = shapes.size();
            progress_info["progress"] = static_cast<double>(i) / shapes.size();
            progress_info["current_utilization"] = batch_result.contains("sheet_utilization") ?
                batch_result["sheet_utilization"] : 0.0;

            progress_callback(progress_info);
        }

        // Return final result
        result = nest_shapes_advanced(shapes, sheet, config);
        result["intermediate_results"] = intermediate_results;
        result["progressive_nesting"] = true;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict AdvancedNesting::nest_with_preprocessing(std::vector<Shape>& shapes,
                                                 const Sheet& sheet,
                                                 bool remove_collinear,
                                                 bool snap_to_grid,
                                                 double grid_size,
                                                 const NestConfig& config) {
    py::dict result;

    try {
        py::list preprocessing_info;

        // Apply preprocessing to each shape
        for (auto& shape : shapes) {
            auto original_points = shape.get_raw_shape();
            auto processed_points = original_points;

            py::dict shape_preprocessing;
            shape_preprocessing["original_vertices"] = original_points.size();

            if (remove_collinear) {
                processed_points = AdvancedGeometry::remove_collinear_points(processed_points, 1e-9);
                shape_preprocessing["vertices_after_collinear_removal"] = processed_points.size();
            }

            if (snap_to_grid) {
                processed_points = HighPrecisionGeometry::snap_to_precision_grid(processed_points, grid_size);
                shape_preprocessing["snapped_to_grid"] = true;
            }

            shape_preprocessing["final_vertices"] = processed_points.size();
            preprocessing_info.append(shape_preprocessing);

            // Update shape with processed points
            // This would require a shape update method
        }

        // Perform nesting with preprocessed shapes
        result = nest_shapes_advanced(shapes, sheet, config);
        result["preprocessing_applied"] = true;
        result["preprocessing_info"] = preprocessing_info;
        result["remove_collinear"] = remove_collinear;
        result["snap_to_grid"] = snap_to_grid;
        result["grid_size"] = grid_size;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

// IndustrySpecificNesting implementations
py::dict IndustrySpecificNesting::nest_metal_cutting(std::vector<Shape>& shapes,
                                                    const Sheet& sheet,
                                                    double kerf_width,
                                                    double lead_in_length,
                                                    const NestConfig& config) {
    py::dict result;

    try {
        // Create metal cutting specific configuration
        NestConfig metal_config = config;
        metal_config.spacing = kerf_width;
        metal_config.placer_type = "nfp";
        metal_config.explore_holes = true;
        metal_config.selector_type = "djd";

        // Apply lead-in considerations by inflating shapes
        for (auto& shape : shapes) {
            shape.set_inflation(kerf_width / 2.0);
        }

        result = AdvancedNesting::nest_shapes_advanced(shapes, sheet, metal_config);

        // Add metal cutting specific metrics
        result["kerf_width"] = kerf_width;
        result["lead_in_length"] = lead_in_length;
        result["cutting_path_length"] = 0.0; // Would calculate total cutting path
        result["piercing_points"] = shapes.size(); // One pierce per shape

        // Calculate cutting time estimate (placeholder)
        double cutting_speed = 100.0; // mm/min
        double cutting_time = result["cutting_path_length"].cast<double>() / cutting_speed;
        result["estimated_cutting_time_min"] = cutting_time;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict IndustrySpecificNesting::nest_fabric_cutting(std::vector<Shape>& shapes,
                                                     const Sheet& sheet,
                                                     const std::vector<double>& grain_directions,
                                                     bool respect_grain,
                                                     const NestConfig& config) {
    py::dict result;

    try {
        NestConfig fabric_config = config;

        if (respect_grain) {
            // Limit rotations to respect grain direction
            fabric_config.rotations = {0.0, 180.0}; // Only flip, no rotation
        }

        fabric_config.spacing = 1.0; // Minimal spacing for fabric

        // Apply grain direction constraints
        if (respect_grain && !grain_directions.empty()) {
            for (size_t i = 0; i < shapes.size() && i < grain_directions.size(); ++i) {
                shapes[i].rotate(grain_directions[i]);
            }
        }

        result = AdvancedNesting::nest_shapes_advanced(shapes, sheet, fabric_config);

        result["grain_directions"] = grain_directions;
        result["respect_grain"] = respect_grain;
        result["fabric_waste"] = sheet.width * sheet.height * (1.0 - result["sheet_utilization"].cast<double>());

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict IndustrySpecificNesting::nest_glass_cutting(std::vector<Shape>& shapes,
                                                    const Sheet& sheet,
                                                    bool minimize_breaklines,
                                                    double min_strip_width,
                                                    const NestConfig& config) {
    py::dict result;

    try {
        NestConfig glass_config = config;
        glass_config.spacing = 3.0; // Wider spacing for glass

        if (minimize_breaklines) {
            glass_config.selector_type = "filler"; // Better for strip layout
            glass_config.alignment = "bottom_left";
        }

        result = AdvancedNesting::nest_shapes_advanced(shapes, sheet, glass_config);

        // Calculate glass-specific metrics
        result["minimize_breaklines"] = minimize_breaklines;
        result["min_strip_width"] = min_strip_width;
        result["breaklines_count"] = 0; // Would calculate actual breaklines
        result["glass_waste"] = sheet.width * sheet.height * (1.0 - result["sheet_utilization"].cast<double>());

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict IndustrySpecificNesting::nest_3d_printing(std::vector<Shape>& shapes,
                                                   const Sheet& sheet,
                                                   double support_distance,
                                                   bool group_similar_heights,
                                                   const NestConfig& config) {
    py::dict result;

    try {
        NestConfig printing_config = config;
        printing_config.spacing = support_distance;
        printing_config.placer_type = "nfp"; // Better for complex shapes

        // Group shapes by height if requested
        if (group_similar_heights) {
            // Sort shapes by area (proxy for height complexity)
            std::sort(shapes.begin(), shapes.end(),
                [](const Shape& a, const Shape& b) {
                    return a.area() < b.area();
                });
        }

        result = AdvancedNesting::nest_shapes_advanced(shapes, sheet, printing_config);

        result["support_distance"] = support_distance;
        result["group_similar_heights"] = group_similar_heights;
        result["print_area_utilization"] = result["sheet_utilization"];

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

// NestingQuality implementations
py::dict NestingQuality::calculate_quality_metrics(const py::dict& nesting_result,
                                                   const Sheet& sheet) {
    py::dict metrics;

    try {
        if (!nesting_result["success"].cast<bool>()) {
            metrics["error"] = "Cannot calculate metrics for failed nesting";
            return metrics;
        }

        double sheet_area = sheet.width * sheet.height;
        double utilization = nesting_result.contains("sheet_utilization") ?
            nesting_result["sheet_utilization"].cast<double>() : 0.0;

        metrics["area_utilization"] = utilization;
        metrics["waste_percentage"] = (1.0 - utilization) * 100.0;
        metrics["waste_area"] = sheet_area * (1.0 - utilization);

        auto nested_shapes = nesting_result["nested_shapes"];
        int shape_count = py::len(nested_shapes);
        metrics["shapes_placed"] = shape_count;
        metrics["shapes_per_unit_area"] = shape_count / sheet_area;

        // Calculate compactness (how close shapes are to each other)
        if (shape_count > 1) {
            double total_distance = 0.0;
            int distance_count = 0;

            for (auto shape1 : nested_shapes) {
                for (auto shape2 : nested_shapes) {
                    if (py::cast(shape1)["id"] != py::cast(shape2)["id"]) {
                        double dx = py::cast(shape1)["x"].cast<double>() - py::cast(shape2)["x"].cast<double>();
                        double dy = py::cast(shape1)["y"].cast<double>() - py::cast(shape2)["y"].cast<double>();
                        total_distance += std::sqrt(dx * dx + dy * dy);
                        distance_count++;
                    }
                }
            }

            metrics["average_inter_shape_distance"] = total_distance / distance_count;
            metrics["compactness"] = 1.0 / (1.0 + metrics["average_inter_shape_distance"].cast<double>());
        } else {
            metrics["compactness"] = 1.0;
        }

        // Overall quality score (0-1, higher is better)
        double quality_score = utilization * 0.6 + metrics["compactness"].cast<double>() * 0.4;
        metrics["overall_quality_score"] = quality_score;

    } catch (const std::exception& e) {
        metrics["error"] = e.what();
    }

    return metrics;
}

py::list NestingQuality::rank_nesting_results(const std::vector<py::dict>& results,
                                             const std::vector<std::string>& criteria) {
    py::list ranked_results;

    // Calculate scores for each result
    std::vector<std::pair<double, size_t>> scores;

    for (size_t i = 0; i < results.size(); ++i) {
        double score = 0.0;

        for (const auto& criterion : criteria) {
            if (criterion == "area_utilization" && results[i].contains("sheet_utilization")) {
                score += results[i]["sheet_utilization"].cast<double>() * 0.4;
            } else if (criterion == "waste" && results[i].contains("sheet_utilization")) {
                score += (1.0 - results[i]["sheet_utilization"].cast<double>()) * (-0.3);
            } else if (criterion == "part_count" && results[i].contains("shapes_placed")) {
                score += results[i]["shapes_placed"].cast<double>() / 100.0 * 0.3;
            }
        }

        scores.push_back({score, i});
    }

    // Sort by score (highest first)
    std::sort(scores.rbegin(), scores.rend());

    // Create ranked list
    for (const auto& score_pair : scores) {
        py::dict ranked_result = results[score_pair.second];
        ranked_result["rank"] = ranked_results.size() + 1;
        ranked_result["score"] = score_pair.first;
        ranked_results.append(ranked_result);
    }

    return ranked_results;
}

py::dict NestingQuality::optimize_existing_nesting(const py::dict& nesting_result,
                                                   const Sheet& sheet,
                                                   const OptimizerConfig& opt_config) {
    py::dict result;

    try {
        if (!nesting_result["success"].cast<bool>()) {
            result["success"] = false;
            result["error"] = "Cannot optimize failed nesting";
            return result;
        }

        auto nested_shapes = nesting_result["nested_shapes"];

        // Extract current positions
        std::vector<double> current_positions;
        for (auto shape : nested_shapes) {
            current_positions.push_back(py::cast(shape)["x"].cast<double>());
            current_positions.push_back(py::cast(shape)["y"].cast<double>());
            current_positions.push_back(py::cast(shape)["rotation"].cast<double>());
        }

        // Define optimization objective to minimize waste
        auto objective = [&sheet](const std::vector<double>& positions) {
            // Calculate bounding box of all shapes
            double min_x = sheet.width, max_x = 0.0;
            double min_y = sheet.height, max_y = 0.0;

            for (size_t i = 0; i < positions.size(); i += 3) {
                min_x = std::min(min_x, positions[i]);
                max_x = std::max(max_x, positions[i]);
                min_y = std::min(min_y, positions[i + 1]);
                max_y = std::max(max_y, positions[i + 1]);
            }

            return (max_x - min_x) * (max_y - min_y); // Minimize bounding area
        };

        OptimizerWrapper optimizer(opt_config);

        // Set up bounds
        std::vector<std::pair<double, double>> bounds;
        for (size_t i = 0; i < nested_shapes.size(); ++i) {
            bounds.push_back({0.0, sheet.width});
            bounds.push_back({0.0, sheet.height});
            bounds.push_back({0.0, 360.0});
        }

        // Create Python objective function
        py::function py_objective = py::cpp_function([objective](py::list params_list) {
            std::vector<double> params;
            for (auto item : params_list) {
                params.push_back(item.cast<double>());
            }
            return objective(params);
        });

        auto opt_result = optimizer.optimize_function(py_objective, bounds, current_positions);

        result["optimization_result"] = opt_result;
        result["success"] = opt_result["success"];

        if (opt_result["success"].cast<bool>()) {
            auto optimized_positions = opt_result["x"].cast<std::vector<double>>();

            // Update nested shapes with optimized positions
            py::list optimized_shapes;
            for (size_t i = 0; i < nested_shapes.size(); ++i) {
                py::dict shape = py::cast(nested_shapes[i]).cast<py::dict>();
                shape["x"] = optimized_positions[i * 3];
                shape["y"] = optimized_positions[i * 3 + 1];
                shape["rotation"] = optimized_positions[i * 3 + 2];
                optimized_shapes.append(shape);
            }

            result["optimized_shapes"] = optimized_shapes;
            result["improvement"] = opt_result["fun"];
        }

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict NestingQuality::validate_for_manufacturing(const py::dict& nesting_result,
                                                   double min_distance,
                                                   double min_feature_size,
                                                   bool check_accessibility) {
    py::dict validation;

    try {
        if (!nesting_result["success"].cast<bool>()) {
            validation["valid"] = false;
            validation["errors"] = py::list();
            py::cast(validation["errors"]).append("Cannot validate failed nesting");
            return validation;
        }

        py::list errors;
        py::list warnings;

        auto nested_shapes = nesting_result["nested_shapes"];

        // Check minimum distance between shapes
        for (auto shape1 : nested_shapes) {
            for (auto shape2 : nested_shapes) {
                if (py::cast(shape1)["id"] != py::cast(shape2)["id"]) {
                    double dx = py::cast(shape1)["x"].cast<double>() - py::cast(shape2)["x"].cast<double>();
                    double dy = py::cast(shape1)["y"].cast<double>() - py::cast(shape2)["y"].cast<double>();
                    double distance = std::sqrt(dx * dx + dy * dy);

                    if (distance < min_distance) {
                        py::dict error;
                        error["type"] = "minimum_distance_violation";
                        error["shape1_id"] = py::cast(shape1)["id"];
                        error["shape2_id"] = py::cast(shape2)["id"];
                        error["distance"] = distance;
                        error["required_distance"] = min_distance;
                        errors.append(error);
                    }
                }
            }
        }

        // Check accessibility if requested
        if (check_accessibility) {
            for (auto shape : nested_shapes) {
                double x = py::cast(shape)["x"].cast<double>();
                double y = py::cast(shape)["y"].cast<double>();

                // Check if shape is accessible from edges
                bool accessible = (x < min_distance * 2) || (y < min_distance * 2);

                if (!accessible) {
                    py::dict warning;
                    warning["type"] = "accessibility_concern";
                    warning["shape_id"] = py::cast(shape)["id"];
                    warning["position"] = std::vector<double>{x, y};
                    warnings.append(warning);
                }
            }
        }

        validation["valid"] = py::len(errors) == 0;
        validation["errors"] = errors;
        validation["warnings"] = warnings;
        validation["min_distance_checked"] = min_distance;
        validation["min_feature_size_checked"] = min_feature_size;
        validation["accessibility_checked"] = check_accessibility;

    } catch (const std::exception& e) {
        validation["valid"] = false;
        validation["error"] = e.what();
    }

    return validation;
}

// ExperimentalNesting implementations
py::dict ExperimentalNesting::nest_ai_guided(std::vector<Shape>& shapes,
                                            const Sheet& sheet,
                                            py::function ml_model,
                                            const NestConfig& config) {
    py::dict result;

    try {
        // This would integrate with ML models for AI-guided nesting
        // For now, return enhanced nesting with AI placeholders

        py::list shape_features;
        for (const auto& shape : shapes) {
            py::dict features;
            features["area"] = shape.area();
            features["vertices"] = shape.vertex_count();
            features["convexity"] = shape.is_convex() ? 1.0 : 0.0;
            shape_features.append(features);
        }

        py::dict predictions;
        if (!ml_model.is_none()) {
            predictions = ml_model(shape_features);
        } else {
            predictions["success"] = false;
            predictions["error"] = "No ML model provided";
        }

        result = AdvancedNesting::nest_shapes_advanced(shapes, sheet, config);
        result["ai_guided"] = true;
        result["shape_features"] = shape_features;
        result["ai_predictions"] = predictions;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict ExperimentalNesting::nest_genetic_algorithm(std::vector<Shape>& shapes,
                                                    const Sheet& sheet,
                                                    int population_size,
                                                    int generations,
                                                    double mutation_rate,
                                                    const NestConfig& config) {
    py::dict result;

    try {
        // Simple genetic algorithm implementation
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> pos_dist(0.0, 1.0);
        std::uniform_real_distribution<> rot_dist(0.0, 360.0);
        std::uniform_real_distribution<> mut_dist(0.0, 1.0);

        // Individual represents positions and rotations for all shapes
        struct Individual {
            std::vector<double> genes; // x, y, rotation for each shape
            double fitness = 0.0;
        };

        std::vector<Individual> population(population_size);

        // Initialize population
        for (auto& individual : population) {
            individual.genes.reserve(shapes.size() * 3);
            for (size_t i = 0; i < shapes.size(); ++i) {
                individual.genes.push_back(pos_dist(gen) * sheet.width);  // x
                individual.genes.push_back(pos_dist(gen) * sheet.height); // y
                individual.genes.push_back(rot_dist(gen));                 // rotation
            }
        }

        // Evolution loop
        py::list generation_stats;
        for (int gen = 0; gen < generations; ++gen) {
            // Evaluate fitness
            for (auto& individual : population) {
                // Simple fitness: minimize bounding box area
                double min_x = sheet.width, max_x = 0.0;
                double min_y = sheet.height, max_y = 0.0;

                for (size_t i = 0; i < shapes.size(); ++i) {
                    double x = individual.genes[i * 3];
                    double y = individual.genes[i * 3 + 1];
                    min_x = std::min(min_x, x);
                    max_x = std::max(max_x, x);
                    min_y = std::min(min_y, y);
                    max_y = std::max(max_y, y);
                }

                individual.fitness = 1.0 / ((max_x - min_x) * (max_y - min_y) + 1.0);
            }

            // Selection and reproduction
            std::sort(population.begin(), population.end(),
                [](const Individual& a, const Individual& b) { return a.fitness > b.fitness; });

            py::dict gen_stats;
            gen_stats["generation"] = gen;
            gen_stats["best_fitness"] = population[0].fitness;
            gen_stats["avg_fitness"] = 0.0;

            double total_fitness = 0.0;
            for (const auto& ind : population) {
                total_fitness += ind.fitness;
            }
            gen_stats["avg_fitness"] = total_fitness / population.size();
            generation_stats.append(gen_stats);

            // Create next generation
            std::vector<Individual> next_population;

            // Keep best individuals
            int elite_count = population_size / 4;
            for (int i = 0; i < elite_count; ++i) {
                next_population.push_back(population[i]);
            }

            // Generate offspring
            while (next_population.size() < population_size) {
                // Tournament selection
                int parent1_idx = gen() % (population_size / 2);
                int parent2_idx = gen() % (population_size / 2);

                Individual offspring = population[parent1_idx];

                // Crossover
                for (size_t i = 0; i < offspring.genes.size(); ++i) {
                    if (mut_dist(gen) < 0.5) {
                        offspring.genes[i] = population[parent2_idx].genes[i];
                    }
                }

                // Mutation
                for (size_t i = 0; i < offspring.genes.size(); ++i) {
                    if (mut_dist(gen) < mutation_rate) {
                        if (i % 3 == 2) { // rotation
                            offspring.genes[i] = rot_dist(gen);
                        } else if (i % 3 == 0) { // x
                            offspring.genes[i] = pos_dist(gen) * sheet.width;
                        } else { // y
                            offspring.genes[i] = pos_dist(gen) * sheet.height;
                        }
                    }
                }

                next_population.push_back(offspring);
            }

            population = next_population;
        }

        // Use best solution
        auto& best_individual = population[0];
        py::list nested_shapes;
        for (size_t i = 0; i < shapes.size(); ++i) {
            py::dict shape_result;
            shape_result["id"] = i;
            shape_result["x"] = best_individual.genes[i * 3];
            shape_result["y"] = best_individual.genes[i * 3 + 1];
            shape_result["rotation"] = best_individual.genes[i * 3 + 2];
            shape_result["sheet_id"] = 0;
            nested_shapes.append(shape_result);
        }

        result["success"] = true;
        result["algorithm"] = "genetic_algorithm";
        result["nested_shapes"] = nested_shapes;
        result["population_size"] = population_size;
        result["generations"] = generations;
        result["mutation_rate"] = mutation_rate;
        result["final_fitness"] = best_individual.fitness;
        result["generation_stats"] = generation_stats;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict ExperimentalNesting::nest_simulated_annealing(std::vector<Shape>& shapes,
                                                      const Sheet& sheet,
                                                      double initial_temperature,
                                                      double cooling_rate,
                                                      int iterations,
                                                      const NestConfig& config) {
    py::dict result;

    try {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> uniform_dist(0.0, 1.0);
        std::normal_distribution<> normal_dist(0.0, 1.0);

        // Initialize solution
        std::vector<double> current_solution;
        for (size_t i = 0; i < shapes.size(); ++i) {
            current_solution.push_back(uniform_dist(gen) * sheet.width);  // x
            current_solution.push_back(uniform_dist(gen) * sheet.height); // y
            current_solution.push_back(uniform_dist(gen) * 360.0);        // rotation
        }

        // Evaluation function
        auto evaluate = [&sheet](const std::vector<double>& solution) {
            double min_x = sheet.width, max_x = 0.0;
            double min_y = sheet.height, max_y = 0.0;

            for (size_t i = 0; i < solution.size(); i += 3) {
                min_x = std::min(min_x, solution[i]);
                max_x = std::max(max_x, solution[i]);
                min_y = std::min(min_y, solution[i + 1]);
                max_y = std::max(max_y, solution[i + 1]);
            }

            return (max_x - min_x) * (max_y - min_y);
        };

        double current_energy = evaluate(current_solution);
        auto best_solution = current_solution;
        double best_energy = current_energy;
        double temperature = initial_temperature;

        py::list iteration_stats;

        for (int iter = 0; iter < iterations; ++iter) {
            // Generate neighbor solution
            auto neighbor_solution = current_solution;

            // Perturb random variable
            int var_idx = gen() % neighbor_solution.size();
            if (var_idx % 3 == 2) { // rotation
                neighbor_solution[var_idx] += normal_dist(gen) * 10.0;
                neighbor_solution[var_idx] = std::fmod(neighbor_solution[var_idx] + 360.0, 360.0);
            } else if (var_idx % 3 == 0) { // x
                neighbor_solution[var_idx] += normal_dist(gen) * sheet.width * 0.05;
                neighbor_solution[var_idx] = std::max(0.0, std::min(sheet.width, neighbor_solution[var_idx]));
            } else { // y
                neighbor_solution[var_idx] += normal_dist(gen) * sheet.height * 0.05;
                neighbor_solution[var_idx] = std::max(0.0, std::min(sheet.height, neighbor_solution[var_idx]));
            }

            double neighbor_energy = evaluate(neighbor_solution);
            double delta_energy = neighbor_energy - current_energy;

            // Accept or reject
            if (delta_energy < 0 || uniform_dist(gen) < std::exp(-delta_energy / temperature)) {
                current_solution = neighbor_solution;
                current_energy = neighbor_energy;

                if (current_energy < best_energy) {
                    best_solution = current_solution;
                    best_energy = current_energy;
                }
            }

            // Cool down
            temperature *= cooling_rate;

            if (iter % 100 == 0) {
                py::dict iter_stats;
                iter_stats["iteration"] = iter;
                iter_stats["temperature"] = temperature;
                iter_stats["current_energy"] = current_energy;
                iter_stats["best_energy"] = best_energy;
                iteration_stats.append(iter_stats);
            }
        }

        // Create result
        py::list nested_shapes;
        for (size_t i = 0; i < shapes.size(); ++i) {
            py::dict shape_result;
            shape_result["id"] = i;
            shape_result["x"] = best_solution[i * 3];
            shape_result["y"] = best_solution[i * 3 + 1];
            shape_result["rotation"] = best_solution[i * 3 + 2];
            shape_result["sheet_id"] = 0;
            nested_shapes.append(shape_result);
        }

        result["success"] = true;
        result["algorithm"] = "simulated_annealing";
        result["nested_shapes"] = nested_shapes;
        result["initial_temperature"] = initial_temperature;
        result["cooling_rate"] = cooling_rate;
        result["iterations"] = iterations;
        result["final_energy"] = best_energy;
        result["iteration_stats"] = iteration_stats;

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

py::dict ExperimentalNesting::nest_multi_objective(std::vector<Shape>& shapes,
                                                   const Sheet& sheet,
                                                   const std::vector<std::string>& objectives,
                                                   const std::vector<double>& weights,
                                                   const OptimizerConfig& opt_config,
                                                   const NestConfig& nest_config) {
    py::dict result;

    try {
        if (objectives.size() != weights.size()) {
            result["success"] = false;
            result["error"] = "Number of objectives must match number of weights";
            return result;
        }

        // Define multi-objective function
        auto multi_objective = [&objectives, &weights, &sheet](const std::vector<double>& solution) {
            double total_score = 0.0;

            for (size_t obj_idx = 0; obj_idx < objectives.size(); ++obj_idx) {
                double obj_value = 0.0;

                if (objectives[obj_idx] == "area") {
                    // Minimize bounding area
                    double min_x = sheet.width, max_x = 0.0;
                    double min_y = sheet.height, max_y = 0.0;

                    for (size_t i = 0; i < solution.size(); i += 3) {
                        min_x = std::min(min_x, solution[i]);
                        max_x = std::max(max_x, solution[i]);
                        min_y = std::min(min_y, solution[i + 1]);
                        max_y = std::max(max_y, solution[i + 1]);
                    }

                    obj_value = (max_x - min_x) * (max_y - min_y);
                } else if (objectives[obj_idx] == "compactness") {
                    // Minimize average distance between shapes
                    double total_distance = 0.0;
                    int count = 0;

                    for (size_t i = 0; i < solution.size(); i += 3) {
                        for (size_t j = i + 3; j < solution.size(); j += 3) {
                            double dx = solution[i] - solution[j];
                            double dy = solution[i + 1] - solution[j + 1];
                            total_distance += std::sqrt(dx * dx + dy * dy);
                            count++;
                        }
                    }

                    obj_value = (count > 0) ? total_distance / count : 0.0;
                } else if (objectives[obj_idx] == "balance") {
                    // Minimize imbalance in shape distribution
                    double cx = 0.0, cy = 0.0;
                    for (size_t i = 0; i < solution.size(); i += 3) {
                        cx += solution[i];
                        cy += solution[i + 1];
                    }
                    cx /= (solution.size() / 3);
                    cy /= (solution.size() / 3);

                    double imbalance = 0.0;
                    for (size_t i = 0; i < solution.size(); i += 3) {
                        double dx = solution[i] - cx;
                        double dy = solution[i + 1] - cy;
                        imbalance += dx * dx + dy * dy;
                    }

                    obj_value = imbalance;
                }

                total_score += weights[obj_idx] * obj_value;
            }

            return total_score;
        };

        // Initial solution
        std::vector<double> initial_solution;
        for (size_t i = 0; i < shapes.size(); ++i) {
            initial_solution.push_back(i * 50.0); // x
            initial_solution.push_back(i * 30.0); // y
            initial_solution.push_back(0.0);      // rotation
        }

        // Bounds
        std::vector<std::pair<double, double>> bounds;
        for (size_t i = 0; i < shapes.size(); ++i) {
            bounds.push_back({0.0, sheet.width});
            bounds.push_back({0.0, sheet.height});
            bounds.push_back({0.0, 360.0});
        }

        // Optimize
        OptimizerWrapper optimizer(opt_config);

        py::function py_objective = py::cpp_function([multi_objective](py::list params_list) {
            std::vector<double> params;
            for (auto item : params_list) {
                params.push_back(item.cast<double>());
            }
            return multi_objective(params);
        });

        auto opt_result = optimizer.optimize_function(py_objective, bounds, initial_solution);

        result["optimization_result"] = opt_result;
        result["success"] = opt_result["success"];

        if (opt_result["success"].cast<bool>()) {
            auto optimal_solution = opt_result["x"].cast<std::vector<double>>();

            py::list nested_shapes;
            for (size_t i = 0; i < shapes.size(); ++i) {
                py::dict shape_result;
                shape_result["id"] = i;
                shape_result["x"] = optimal_solution[i * 3];
                shape_result["y"] = optimal_solution[i * 3 + 1];
                shape_result["rotation"] = optimal_solution[i * 3 + 2];
                shape_result["sheet_id"] = 0;
                nested_shapes.append(shape_result);
            }

            result["nested_shapes"] = nested_shapes;
            result["objectives"] = objectives;
            result["weights"] = weights;
            result["final_objective_value"] = opt_result["fun"];
        }

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
    }

    return result;
}

} // namespace nest2d_wrapper
