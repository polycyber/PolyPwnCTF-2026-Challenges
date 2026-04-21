cmake_minimum_required(VERSION 3.16)
project(SolutionMixer VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Static linking configuration
set(CMAKE_FIND_LIBRARY_SUFFIXES .a ${CMAKE_FIND_LIBRARY_SUFFIXES})
set(BUILD_SHARED_LIBS OFF)

# Static linking flags
if(UNIX AND NOT APPLE)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libgcc -static-libstdc++")
endif()

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Try to find Qt6 static build
set(QT_FORCE_STATIC_CPP ON)
find_package(Qt6 REQUIRED COMPONENTS Core Widgets Network)

# Find OpenSSL for AES encryption
find_package(OpenSSL REQUIRED)

# Client executable (Qt GUI)
qt6_add_executable(SolutionMixer
    client.cpp
)

target_link_libraries(SolutionMixer PRIVATE
    Qt6::Core
    Qt6::Widgets
    Qt6::Network
)

# Server executable (business logic)
qt6_add_executable(SolutionMixerServer
    server.cpp
)

target_link_libraries(SolutionMixerServer PRIVATE
    Qt6::Core
    Qt6::Network
    OpenSSL::SSL
    OpenSSL::Crypto
)

# Force static linking where possible
set_target_properties(SolutionMixer PROPERTIES
    LINK_SEARCH_START_STATIC 1
    LINK_SEARCH_END_STATIC 1
)

set_target_properties(SolutionMixerServer PROPERTIES
    LINK_SEARCH_START_STATIC 1
    LINK_SEARCH_END_STATIC 1
)

# Strip symbols after linking
# Option 1: Strip unneeded symbols (safer, keeps Qt symbols)
# Option 2: Strip all symbols (more aggressive, use only if Qt is dynamically linked)
# Option 3: Remove only local symbols (keeps exported symbols like Qt's)

# Current: Strip unneeded symbols (recommended)
add_custom_command(TARGET SolutionMixerServer POST_BUILD
    COMMAND ${CMAKE_STRIP} --strip-unneeded $<TARGET_FILE:SolutionMixerServer>
    COMMENT "Stripping unneeded symbols from SolutionMixerServer"
)

add_custom_command(TARGET SolutionMixer POST_BUILD
    COMMAND ${CMAKE_STRIP} --strip-unneeded $<TARGET_FILE:SolutionMixer>
    COMMENT "Stripping unneeded symbols from SolutionMixer"
)

# Alternative: For more aggressive stripping, uncomment the lines below and comment out the above
# add_custom_command(TARGET SolutionMixerServer POST_BUILD
#     COMMAND ${CMAKE_STRIP} -s $<TARGET_FILE:SolutionMixerServer>
#     COMMENT "Stripping all symbols from SolutionMixerServer"
# )
# add_custom_command(TARGET SolutionMixer POST_BUILD
#     COMMAND ${CMAKE_STRIP} -s $<TARGET_FILE:SolutionMixer>
#     COMMENT "Stripping all symbols from SolutionMixer"
# )

# Additional static linking for C++ runtime
if(UNIX AND NOT APPLE)
    target_link_options(SolutionMixer PRIVATE 
        -static-libgcc 
        -static-libstdc++
        -Wl,-Bstatic
    )
    # Static link C++ runtime for server (Qt6 and OpenSSL remain dynamic)
    target_link_options(SolutionMixerServer PRIVATE 
        -static-libgcc 
        -static-libstdc++
    )
endif()

# Note: For fully static Qt6 binary, Qt6 must be built statically.
# If Qt6 is not statically built, you may need to bundle Qt libraries.
# To build Qt6 statically, configure Qt6 with: -static -static-runtime
# 
# For Docker deployment, ensure the binary is fully static by:
# 1. Building Qt6 statically, OR
# 2. Using linuxdeployqt to bundle Qt libraries, OR  
# 3. Including Qt runtime libraries in the Docker image

