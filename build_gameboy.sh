#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}"
NDK="${ANDROID_NDK_HOME:-$SDK/ndk/28.2.13676358}"
[[ -x "$NDK/ndk-build" ]] || { echo 'Set ANDROID_NDK_HOME to Android NDK 28.2.13676358.' >&2; exit 1; }
PIN=d9d6cd06382d1ced30de34d56d3609452323dab1
WORK="${FIRESPOT_CORE_WORK:-$ROOT/.tooling/gambatte}"
OUT="$ROOT/artifacts/gameboy"
if [[ ! -d "$WORK/source/.git" ]]; then
    mkdir -p "$WORK/source"
    git -C "$WORK/source" init -q
    git -C "$WORK/source" remote add origin https://github.com/libretro/gambatte-libretro.git
fi
if ! git -C "$WORK/source" cat-file -e "$PIN^{commit}" 2>/dev/null; then
    git -C "$WORK/source" fetch --depth 1 origin "$PIN"
fi
git -C "$WORK/source" checkout --detach "$PIN"
[[ -z "$(git -C "$WORK/source" status --porcelain --untracked-files=no)" ]] || { echo 'Core source has local changes; refusing to build.' >&2; exit 1; }
"$NDK/ndk-build" -C "$WORK/source/libgambatte/libretro/jni" \
    APP_ABI='armeabi-v7a arm64-v8a x86_64' APP_PLATFORM=android-28 \
    NDK_OUT="$WORK/obj" NDK_LIBS_OUT="$WORK/libs" -j2
mkdir -p "$OUT"
for abi in armeabi-v7a arm64-v8a x86_64; do
    mkdir -p "$OUT/$abi"
    cp "$WORK/libs/$abi/libretro.so" "$OUT/$abi/libretro_gambatte.so"
    mkdir -p "$ROOT/app/src/demo/jniLibs/$abi"
    cp "$OUT/$abi/libretro_gambatte.so" "$ROOT/app/src/demo/jniLibs/$abi/"
done
cp "$WORK/source/COPYING" "$OUT/COPYING"
git -C "$WORK/source" archive --format=tar.gz --prefix=gambatte/ "$PIN" > "$OUT/gambatte-source.tar.gz"
python3 "$ROOT/scripts/verify_artifacts.py" --cores "$OUT" --write-manifest
cp "$OUT/manifest.json" "$ROOT/app/src/debug/assets/phase0-core-manifest.json"
printf 'Core artifacts and corresponding source: %s\n' "$OUT"
