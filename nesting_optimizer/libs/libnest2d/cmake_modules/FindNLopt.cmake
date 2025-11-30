# Find NLopt library.
# The following variables are set
#
# NLopt_FOUND
# NLopt_INCLUDE_DIRS
# NLopt_LIBRARIES
#
# It searches the environment variable $NLopt_PATH automatically.

unset(NLopt_FOUND CACHE)
unset(NLopt_INCLUDE_DIRS CACHE)
unset(NLopt_LIBRARIES CACHE)
unset(NLopt_LIBRARIES_RELEASE CACHE)
unset(NLopt_LIBRARIES_DEBUG CACHE)

if(CMAKE_BUILD_TYPE MATCHES "(Debug|DEBUG|debug)")
    set(NLopt_BUILD_TYPE DEBUG)
else()
    set(NLopt_BUILD_TYPE RELEASE)
endif()

set(NLOPT_CUSTOM_PATH "/odoo18/custom/addons/nesting_optimizer/libs/nlopt/build")

FIND_PATH(NLopt_INCLUDE_DIRS nlopt.hpp
    ${NLOPT_CUSTOM_PATH}
    ${NLOPT_CUSTOM_PATH}/include
    ${NLOPT_CUSTOM_PATH}/../include
    /usr/local/include
    /usr/include
)

set(LIB_SEARCHDIRS 
    ${NLOPT_CUSTOM_PATH}
    ${NLOPT_CUSTOM_PATH}/lib
    ${NLOPT_CUSTOM_PATH}/../lib
    /usr/local/lib
    /usr/lib
)

set(_deb_postfix "d")

FIND_LIBRARY(NLopt_LIBRARIES_RELEASE nlopt ${LIB_SEARCHDIRS})
FIND_LIBRARY(NLopt_LIBRARIES_DEBUG nlopt${_deb_postfix} ${LIB_SEARCHDIRS})

if(NLopt_LIBRARIES_${NLopt_BUILD_TYPE})
    set(NLopt_LIBRARIES "${NLopt_LIBRARIES_${NLopt_BUILD_TYPE}}")
else()
    set(NLopt_LIBRARIES "${NLopt_LIBRARIES_RELEASE}")
endif()

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(NLopt
    "NLopt library cannot be found. Consider set NLopt_PATH environment variable"
    NLopt_INCLUDE_DIRS
    NLopt_LIBRARIES)

MARK_AS_ADVANCED(
    NLopt_INCLUDE_DIRS
    NLopt_LIBRARIES)

if(NLopt_FOUND)
    add_library(NLopt::nlopt UNKNOWN IMPORTED)
    set_target_properties(NLopt::nlopt PROPERTIES IMPORTED_LOCATION ${NLopt_LIBRARIES})
    set_target_properties(NLopt::nlopt PROPERTIES INTERFACE_INCLUDE_DIRECTORIES ${NLopt_INCLUDE_DIRS})
    if(NLopt_LIBRARIES_RELEASE AND NLopt_LIBRARIES_DEBUG)
        set_target_properties(NLopt::nlopt PROPERTIES
            IMPORTED_LOCATION_DEBUG          ${NLopt_LIBRARIES_DEBUG}
            IMPORTED_LOCATION_RELWITHDEBINFO ${NLopt_LIBRARIES_RELEASE}
            IMPORTED_LOCATION_RELEASE        ${NLopt_LIBRARIES_RELEASE}
            IMPORTED_LOCATION_MINSIZEREL     ${NLopt_LIBRARIES_RELEASE}
        )
    endif()
endif()
