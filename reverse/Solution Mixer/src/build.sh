#!/bin/bash
# Build script for static binary
# Builds to ../build and copies binaries to ../files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
FILES_DIR="$PROJECT_ROOT/files"
SRC_DIR="$PROJECT_ROOT/src"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

### Build

cmake "$SCRIPT_DIR" -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXE_LINKER_FLAGS="-static-libgcc -static-libstdc++" -DBUILD_SHARED_LIBS=OFF

make -j$(nproc)

### Move intermediate files

cp SolutionMixer "$BUILD_DIR/appimage/usr/bin" 2>/dev/null || echo "Warning: SolutionMixer not built"

### AppImage

export NO_STRIP=1
export QMAKE=/usr/bin/qmake6
linuxdeploy --appdir $BUILD_DIR/appimage --executable $BUILD_DIR/appimage/usr/bin/SolutionMixer --desktop-file $BUILD_DIR/appimage/SolutionMixer.desktop --icon-file $BUILD_DIR/appimage/solutionmixer.png --plugin qt --output appimage
mv SolutionMixer-x86_64.AppImage SolutionMixer.AppImage

# Move challenge files
cp $BUILD_DIR/SolutionMixer.AppImage "$FILES_DIR/" 2>/dev/null || echo "Warning: SolutionMixer not built"
cp SolutionMixerServer "$FILES_DIR/" 2>/dev/null || echo "Warning: SolutionMixerServer not built"

echo "Build complete! Binaries are in: $BUILD_DIR/"
echo "Binaries copied to: $FILES_DIR/"
