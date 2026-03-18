cmake_minimum_required(VERSION 3.22)
project(Jarvis5 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Локальная vosk
set(VOSK_DIR "${CMAKE_SOURCE_DIR}/src/library")

include_directories(
    ${CMAKE_SOURCE_DIR}/src
    ${VOSK_DIR}/include
)

link_directories(${VOSK_DIR})

set(SOURCES
    main.cpp
    src/audioCapture.cpp
    src/recognizer.cpp
)

add_executable(Jarvis5 ${SOURCES})

target_link_libraries(Jarvis5
    vosk
    pthread
    dl
    rt
    m
)