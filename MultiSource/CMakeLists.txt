# Enable only 7zip benchmark
if(TEST_SUITE_BENCH_SAMPLE)
  add_subdirectory(Benchmarks)
  return()
endif()

add_subdirectory(Applications)
add_subdirectory(Benchmarks)
if(NOT TEST_SUITE_BENCHMARKING_ONLY)
  add_subdirectory(UnitTests)
endif()

file(COPY lit.local.cfg DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")
