cmake_minimum_required(VERSION 2.8)

SET(LLVM_INSTALL_DIR "/usr")
if (NOT "${LLVM_INSTALL_DIR}" STREQUAL "")
  set (CMAKE_C_COMPILER "${LLVM_INSTALL_DIR}/bin/clang")
  set (CMAKE_CXX_COMPILER "${LLVM_INSTALL_DIR}/bin/clang++")
endif()
SET(CMAKE_CXX_FLAGS "-O1 -fno-rtti -ggdb -std=c++20 -Wall")

project(nulldom)

list(APPEND CMAKE_PREFIX_PATH "${LLVM_INSTALL_DIR}/lib/cmake/llvm/")
find_package(LLVM REQUIRED CONFIG)
include_directories(${LLVM_INCLUDE_DIRS})

add_library(NullDom MODULE nulldom.cpp)

if (APPLE)
  set_target_properties(NullDom PROPERTIES LINK_FLAGS "-undefined dynamic_lookup")
endif(APPLE)
