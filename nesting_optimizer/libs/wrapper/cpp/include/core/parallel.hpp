#ifndef NEST2D_PARALLEL_HPP
#define NEST2D_PARALLEL_HPP

#include "types.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#ifdef LIBNEST2D_AVAILABLE
#include <libnest2d/parallel.hpp>
#endif
#include <thread>
#include <future>
#include <vector>
#include <functional>

namespace py = pybind11;

namespace nest2d_wrapper {

/**
 * Parallel processing configuration and utilities
 */
class ParallelConfig {
public:
    enum class ThreadingBackend {
        STD_THREAD,
        TBB,
        OPENMP,
        SEQUENTIAL
    };

    ThreadingBackend backend = ThreadingBackend::STD_THREAD;
    int num_threads = -1; // -1 means use hardware concurrency
    bool force_sequential = false;

    ParallelConfig() {
        if (num_threads == -1) {
            num_threads = std::max(1u, std::thread::hardware_concurrency());
        }
    }

    ParallelConfig(ThreadingBackend b, int threads = -1)
        : backend(b), num_threads(threads) {
        if (num_threads == -1) {
            num_threads = std::max(1u, std::thread::hardware_concurrency());
        }
    }

    std::string to_string() const {
        std::string backend_str;
        switch (backend) {
            case ThreadingBackend::STD_THREAD: backend_str = "std_thread"; break;
            case ThreadingBackend::TBB: backend_str = "tbb"; break;
            case ThreadingBackend::OPENMP: backend_str = "openmp"; break;
            case ThreadingBackend::SEQUENTIAL: backend_str = "sequential"; break;
        }
        return "ParallelConfig(backend=" + backend_str + ", threads=" + std::to_string(num_threads) + ")";
    }
};

/**
 * Parallel execution wrapper for LibNest2D
 */
class ParallelExecutor {
private:
    ParallelConfig config_;

public:
    explicit ParallelExecutor(const ParallelConfig& config = ParallelConfig())
        : config_(config) {}

    /**
     * Execute a function in parallel over a range of items
     */
    template<class Iterator, class Function>
    void parallel_for(Iterator begin, Iterator end, Function&& func) {
        if (config_.force_sequential || config_.backend == ParallelConfig::ThreadingBackend::SEQUENTIAL) {
            size_t index = 0;
            for (auto it = begin; it != end; ++it, ++index) {
                func(*it, index);
            }
            return;
        }

        auto distance = std::distance(begin, end);
        if (distance <= 0) return;

        size_t num_items = static_cast<size_t>(distance);
        size_t num_threads = std::min(static_cast<size_t>(config_.num_threads), num_items);

        if (num_threads <= 1) {
            size_t index = 0;
            for (auto it = begin; it != end; ++it, ++index) {
                func(*it, index);
            }
            return;
        }

        std::vector<std::future<void>> futures;
        futures.reserve(num_threads);

        size_t chunk_size = num_items / num_threads;
        size_t remainder = num_items % num_threads;

        auto current_it = begin;
        size_t current_index = 0;

        for (size_t thread_id = 0; thread_id < num_threads; ++thread_id) {
            size_t current_chunk_size = chunk_size + (thread_id < remainder ? 1 : 0);
            auto chunk_end = current_it;
            std::advance(chunk_end, current_chunk_size);

            futures.emplace_back(
                std::async(std::launch::async,
                    [current_it, chunk_end, current_index, &func]() mutable {
                        size_t index = current_index;
                        for (auto it = current_it; it != chunk_end; ++it, ++index) {
                            func(*it, index);
                        }
                    })
            );

            current_it = chunk_end;
            current_index += current_chunk_size;
        }

        // Wait for all threads to complete
        for (auto& future : futures) {
            future.wait();
        }
    }

    /**
     * Execute a function in parallel with just indices
     */
    void parallel_for_index(size_t count, std::function<void(size_t)> func) {
        if (config_.force_sequential || config_.backend == ParallelConfig::ThreadingBackend::SEQUENTIAL || count == 0) {
            for (size_t i = 0; i < count; ++i) {
                func(i);
            }
            return;
        }

        size_t num_threads = std::min(static_cast<size_t>(config_.num_threads), count);

        if (num_threads <= 1) {
            for (size_t i = 0; i < count; ++i) {
                func(i);
            }
            return;
        }

        std::vector<std::future<void>> futures;
        futures.reserve(num_threads);

        size_t chunk_size = count / num_threads;
        size_t remainder = count % num_threads;

        size_t start_index = 0;
        for (size_t thread_id = 0; thread_id < num_threads; ++thread_id) {
            size_t current_chunk_size = chunk_size + (thread_id < remainder ? 1 : 0);
            size_t end_index = start_index + current_chunk_size;

            futures.emplace_back(
                std::async(std::launch::async,
                    [start_index, end_index, &func]() {
                        for (size_t i = start_index; i < end_index; ++i) {
                            func(i);
                        }
                    })
            );

            start_index = end_index;
        }

        // Wait for all threads to complete
        for (auto& future : futures) {
            future.wait();
        }
    }

    /**
     * Convert to LibNest2D launch policy
     */
    std::launch to_launch_policy() const {
        if (config_.force_sequential || config_.backend == ParallelConfig::ThreadingBackend::SEQUENTIAL) {
            return std::launch::deferred;
        }
        return std::launch::async | std::launch::deferred;
    }

    const ParallelConfig& get_config() const { return config_; }
    void set_config(const ParallelConfig& config) { config_ = config; }
};

/**
 * Global parallel executor instance
 */
extern ParallelExecutor global_parallel_executor;

/**
 * Convenience functions for parallel execution
 */
template<class Iterator, class Function>
void parallel_for(Iterator begin, Iterator end, Function&& func,
                 const ParallelConfig& config = ParallelConfig()) {
    ParallelExecutor executor(config);
    executor.parallel_for(begin, end, std::forward<Function>(func));
}

void parallel_for_index(size_t count, std::function<void(size_t)> func,
                       const ParallelConfig& config = ParallelConfig());

} // namespace nest2d_wrapper

#endif // NEST2D_PARALLEL_HPP
