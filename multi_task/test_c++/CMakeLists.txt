cmake_minimum_required(VERSION 3.12)

project(test_tasks)

set(CMAKE_CXX_STANDARD 14)


add_executable(test_tasks test_tasks.cpp)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static -static-libgcc -static-libstdc++")

