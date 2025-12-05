#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Libnest2D::libnest2d_clipper_nlopt" for configuration ""
set_property(TARGET Libnest2D::libnest2d_clipper_nlopt APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(Libnest2D::libnest2d_clipper_nlopt PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_NOCONFIG "CXX"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libnest2d_clipper_nlopt.a"
  )

list(APPEND _cmake_import_check_targets Libnest2D::libnest2d_clipper_nlopt )
list(APPEND _cmake_import_check_files_for_Libnest2D::libnest2d_clipper_nlopt "${_IMPORT_PREFIX}/lib/libnest2d_clipper_nlopt.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
