#include "../include/core/parallel.hpp"
#include <algorithm>
#include <thread>

namespace nest2d_wrapper {

// Global parallel executor instance
ParallelExecutor global_parallel_executor;

/**
 * Convenience function for parallel execution with index
 */
void parallel_for_index(size_t count, std::function<void(size_t)> func,
                       const ParallelConfig& config) {
    ParallelExecutor executor(config);
    executor.parallel_for_index(count, func);
}

} // namespace nest2d_wrapper
