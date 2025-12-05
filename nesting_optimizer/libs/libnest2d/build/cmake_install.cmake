# Install script for directory: /odoo18/custom/addons/nesting_optimizer/libs/libnest2d

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/libnest2d_clipper_nlopt.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D/Libnest2DTargets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D/Libnest2DTargets.cmake"
         "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/CMakeFiles/Export/d6debece1bd934a2eb9dab02f1ce6ec9/Libnest2DTargets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D/Libnest2DTargets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D/Libnest2DTargets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/CMakeFiles/Export/d6debece1bd934a2eb9dab02f1ce6ec9/Libnest2DTargets.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^()$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/CMakeFiles/Export/d6debece1bd934a2eb9dab02f1ce6ec9/Libnest2DTargets-noconfig.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/libnest2d.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/nester.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/geometry_traits.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/geometry_traits_nfp.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/common.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/parallel.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/optimizer.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/utils" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/utils/metaloop.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/utils" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/utils/rotfinder.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/utils" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/utils/rotcalipers.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/utils" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/utils/bigint.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/utils" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/utils/rational.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/utils" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/utils/boost_alg.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/placers" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/placers/placer_boilerplate.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/placers" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/placers/bottomleftplacer.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/placers" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/placers/nfpplacer.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/selections" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/selections/selection_boilerplate.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/selections" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/selections/filler.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/selections" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/selections/firstfit.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/selections" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/selections/djd_heuristic.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/backends/clipper" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/backends/clipper/geometries.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/backends/clipper" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/backends/clipper/clipper_polygon.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/optimizers/nlopt" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/optimizers/nlopt/simplex.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/optimizers/nlopt" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/optimizers/nlopt/subplex.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/optimizers/nlopt" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/optimizers/nlopt/genetic.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/libnest2d/optimizers/nlopt" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/include/libnest2d/optimizers/nlopt/nlopt_boilerplate.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D" TYPE FILE FILES
    "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/Libnest2DConfig.cmake"
    "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/Libnest2DConfigVersion.cmake"
    "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/cmake_modules/FindClipper.cmake"
    "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/cmake_modules/FindNLopt.cmake"
    "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/cmake_modules/FindTBB.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/Libnest2D" TYPE FILE FILES "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/rp_packages_build/RPPackageVersions.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/include/libnest2d/backends/clipper/cmake_install.cmake")
  include("/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/include/libnest2d/optimizers/nlopt/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/odoo18/custom/addons/nesting_optimizer/libs/libnest2d/build/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
