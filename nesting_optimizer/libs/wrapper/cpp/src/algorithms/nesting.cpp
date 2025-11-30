#include "../../include/algorithms/nesting.hpp"
#include "../../include/core/errors.hpp"
#include <libnest2d/libnest2d.hpp>
#include <libnest2d/placers/nfpplacer.hpp>
#include <libnest2d/placers/bottomleftplacer.hpp>
#include <libnest2d/selections/firstfit.hpp>
#include <libnest2d/selections/filler.hpp>
#include <libnest2d/selections/djd.hpp>
#include <sstream>
#include <chrono>
#include <stdexcept>

namespace nest2d_wrapper {

py::dict nest_shapes(std::vector<Shape>& shapes,
                     const Sheet& sheet,
                     const NestConfig& config) {

    auto start_time = std::chrono::high_resolution_clock::now();

    py::dict result;

    try {
        // Convert shapes to LibNest2D items
        std::vector<libnest2d::Item> items;
        items.reserve(shapes.size());

        for (auto& shape : shapes) {
            items.push_back(shape.get_internal());
        }

        // Create sheet
        LibNest2DRectangle sheet_rect = sheet.to_libnest2d();

        // Configure nesting based on config
        if (config.placer_type == "nfp") {
            // Use NFP placer
            using NfpPlacer = libnest2d::placers::NfpPlacer;
            using Selector = libnest2d::selections::FirstFitSelection;

            auto nfp_config = config.get_nfp_config();

            size_t bins_used = libnest2d::nest(items, sheet_rect,
                                             config.spacing * COORD_SCALE,
                                             NfpPlacer(nfp_config),
                                             Selector());

            // Collect results
            py::list bins;
            py::dict stats;

            for (size_t bin_id = 0; bin_id < bins_used; ++bin_id) {
                py::list bin_items;

                for (size_t i = 0; i < items.size(); ++i) {
                    if (items[i].sheetId() == static_cast<int>(bin_id)) {
                        py::dict item_info;
                        item_info["id"] = i;
                        item_info["x"] = static_cast<double>(getX(items[i].translation())) / COORD_SCALE;
                        item_info["y"] = static_cast<double>(getY(items[i].translation())) / COORD_SCALE;
                        item_info["rotation"] = items[i].rotation() * 180.0 / M_PI;
                        item_info["sheet_id"] = items[i].sheetId();

                        bin_items.append(item_info);
                    }
                }

                bins.append(bin_items);
            }

            result["bins"] = bins;
            result["bins_used"] = bins_used;

            // Calculate efficiency
            double total_item_area = 0.0;
            for (const auto& shape : shapes) {
                total_item_area += shape.area();
            }

            double total_sheet_area = bins_used * sheet.area();
            double efficiency = (total_sheet_area > 0) ? (total_item_area / total_sheet_area) : 0.0;

            stats["total_item_area"] = total_item_area;
            stats["total_sheet_area"] = total_sheet_area;
            stats["efficiency"] = efficiency;
            stats["utilization_percent"] = efficiency * 100.0;

            result["statistics"] = stats;

        } else if (config.placer_type == "bottom_left") {
            // Use Bottom-Left placer
            using BLPlacer = libnest2d::placers::BottomLeftPlacer;
            using Selector = libnest2d::selections::FirstFitSelection;

            auto bl_config = config.get_bottom_left_config();

            size_t bins_used = libnest2d::nest(items, sheet_rect,
                                             config.spacing * COORD_SCALE,
                                             BLPlacer(bl_config),
                                             Selector());

            // Collect results (similar to NFP)
            py::list bins;
            for (size_t bin_id = 0; bin_id < bins_used; ++bin_id) {
                py::list bin_items;

                for (size_t i = 0; i < items.size(); ++i) {
                    if (items[i].sheetId() == static_cast<int>(bin_id)) {
                        py::dict item_info;
                        item_info["id"] = i;
                        item_info["x"] = static_cast<double>(getX(items[i].translation())) / COORD_SCALE;
                        item_info["y"] = static_cast<double>(getY(items[i].translation())) / COORD_SCALE;
                        item_info["rotation"] = items[i].rotation() * 180.0 / M_PI;
                        item_info["sheet_id"] = items[i].sheetId();

                        bin_items.append(item_info);
                    }
                }

                bins.append(bin_items);
            }

            result["bins"] = bins;
            result["bins_used"] = bins_used;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

        result["execution_time_ms"] = duration.count();
        result["success"] = true;
        result["message"] = "Nesting completed successfully";

        // Update original shapes with results
        for (size_t i = 0; i < items.size() && i < shapes.size(); ++i) {
            shapes[i].get_internal() = items[i];
        }

    } catch (const std::exception& e) {
        result["success"] = false;
        result["error"] = e.what();
        result["bins"] = py::list();
        result["bins_used"] = 0;
    }

    return result;
}

py::dict nest_polygons(const std::vector<std::vector<std::vector<double>>>& polygons,
                      double sheet_width,
                      double sheet_height,
                      double spacing,
                      const std::vector<double>& rotations) {

    // Convert polygons to shapes
    std::vector<Shape> shapes;
    shapes.reserve(polygons.size());

    for (const auto& polygon : polygons) {
        shapes.emplace_back(polygon);
    }

    // Create sheet
    Sheet sheet(sheet_width, sheet_height);

    // Create config
    NestConfig config;
    config.spacing = spacing;
    config.rotations = rotations;

    // Create dummy progress control for now

    return nest_shapes(shapes, sheet, config);
}

py::dict nest_polygons_batch(const std::vector<std::vector<std::vector<double>>>& polygons,
                            double sheet_width,
                            double sheet_height,
                            int batch_size,
                            const NestConfig& config) {

    py::dict final_result;
    py::list all_bins;
    int total_bins_used = 0;

    // Process in batches
    for (size_t start = 0; start < polygons.size(); start += batch_size) {
        size_t end = std::min(start + batch_size, polygons.size());

        std::vector<std::vector<std::vector<double>>> batch_polygons(
            polygons.begin() + start, polygons.begin() + end);

        auto batch_result = nest_polygons(batch_polygons, sheet_width, sheet_height,
                                         config.spacing, config.rotations);

        if (batch_result["success"].cast<bool>()) {
            auto batch_bins = batch_result["bins"].cast<py::list>();

            // Adjust item IDs to be global
            for (auto bin : batch_bins) {
                py::list bin_list = bin.cast<py::list>();
                for (auto item : bin_list) {
                    py::dict item_dict = item.cast<py::dict>();
                    int old_id = item_dict["id"].cast<int>();
                    item_dict["id"] = old_id + start;
                    item_dict["sheet_id"] = item_dict["sheet_id"].cast<int>() + total_bins_used;
                }
                all_bins.append(bin);
            }

            total_bins_used += batch_result["bins_used"].cast<int>();
        }
    }

    final_result["bins"] = all_bins;
    final_result["bins_used"] = total_bins_used;
    final_result["success"] = true;
    final_result["message"] = "Batch nesting completed";

    return final_result;
}

// Simple implementation for multi-sheet nesting
py::dict nest_multi_sheets(std::vector<Shape>& shapes,
                          const std::vector<Sheet>& sheets,
                          const NestConfig& config) {

    py::dict result;
    py::list all_bins;
    int total_bins_used = 0;

    std::vector<Shape> remaining_shapes = shapes;

    for (size_t sheet_idx = 0; sheet_idx < sheets.size() && !remaining_shapes.empty(); ++sheet_idx) {
        auto sheet_result = nest_shapes(remaining_shapes, sheets[sheet_idx], config);

        if (sheet_result["success"].cast<bool>()) {
            auto sheet_bins = sheet_result["bins"].cast<py::list>();

            // Adjust sheet IDs
            for (auto bin : sheet_bins) {
                py::list bin_list = bin.cast<py::list>();
                for (auto item : bin_list) {
                    py::dict item_dict = item.cast<py::dict>();
                    item_dict["sheet_id"] = item_dict["sheet_id"].cast<int>() + total_bins_used;
                    item_dict["sheet_type"] = sheet_idx;
                }
                all_bins.append(bin);
            }

            total_bins_used += sheet_result["bins_used"].cast<int>();

            // Remove successfully placed shapes
            std::vector<Shape> next_remaining;
            for (auto& shape : remaining_shapes) {
                if (shape.get_sheet_id() == -1) { // Not placed
                    next_remaining.push_back(shape);
                }
            }
            remaining_shapes = next_remaining;
        }
    }

    result["bins"] = all_bins;
    result["bins_used"] = total_bins_used;
    result["success"] = true;
    result["unplaced_shapes"] = remaining_shapes.size();

    return result;
}

} // namespace nest2d_wrapper
