cmake_minimum_required(VERSION 3.12)
project(libnest2d_python_bindings)

# Set C++ standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11 from the virtual environment
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Use Python to find pybind11's CMake configuration
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

find_package(pybind11 REQUIRED PATHS "${pybind11_DIR}")

set(LIBS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../)
set(LIBNEST2D_DIR ${LIBS_DIR}/libnest2d)
set(CLIPPER_DIR ${LIBS_DIR}/clipper)
set(NLOPT_DIR ${LIBS_DIR}/nlopt)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${LIBNEST2D_DIR}/include)
include_directories(${CLIPPER_DIR}/cpp)
include_directories(${NLOPT_DIR}/src/api)
include_directories(${NLOPT_DIR}/build)

# Link directories
link_directories(${CLIPPER_DIR}/cpp/build)
link_directories(${NLOPT_DIR}/build)

# Set libnest2d configuration
add_definitions(-DLIBNEST2D_GEOMETRIES_clipper)
add_definitions(-DLIBNEST2D_OPTIMIZER_nlopt)

# Get all cpp files in src and headers and main file
file(GLOB SRC_FILES "src/**/*.cpp")
file(GLOB HEADER_FILES "include/*.hpp")

set(MAIN_FILE "main.cpp")

# Create the Python module
pybind11_add_module(nest2d ${MAIN_FILE} ${SRC_FILES} ${HEADER_FILES})

# Compiler-specific options
target_compile_features(nest2d PRIVATE cxx_std_14)
target_compile_definitions(nest2d PRIVATE VERSION_INFO=${PROJECT_VERSION})

# Link required libraries
target_link_libraries(nest2d PRIVATE polyclipping nlopt)

set_target_properties(nest2d PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)
