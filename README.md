# FireSpot console support and homebrew catalog

Versioned Android libretro core binaries for FireSpot, matching upstream source, licenses, and original redistributable games. Downloads are hosted in [GitHub Releases](https://github.com/Nirusaki-Malaal/firespot-cores/releases).

## First release: phase1-v1

| Core | System | Runtime evidence |
|---|---|---|
| Gambatte | Game Boy / Game Boy Color | Original Game Boy games tested on a local Android emulator; Fire TV acceptance pending |
| FCEUmm | NES / Famicom | Android build; experimental until gameplay is verified |
| mGBA | Game Boy Advance | Android build; experimental until gameplay is verified |
| PCSX ReARMed | PlayStation | Android build; experimental until gameplay is verified |

All four cores have ARMv7, ARM64 and x86_64 binaries, built with NDK 28.2.13676358 for Android API 28+. This does not imply every title runs or every Fire TV has adequate performance. PSP and hardware-rendered systems are not currently released: the FireSpot bridge needs additional rendering integration and device testing.

The signed catalog maps console IDs and CPU architectures to immutable release URLs, exact sizes and SHA-256 hashes. FireSpot pins the publisher public key and verifies the catalog signature before trusting entries. Each native download is verified for size, checksum and ELF architecture before installation. Failed or cancelled installs retain any previously installed version.

`catalog.sig` is a binary RSA/SHA-256 signature over the exact bytes of `catalog.json`. The public key is in `public-key.der`; the private signing key is never published. SHA256SUMS provides independent file-integrity metadata.

## Games

Orbit Collector, Pocket Courier and Signal Runner are small original FireSpot checkpoint games dedicated under CC0-1.0, with original graphics/audio/code and no proprietary BIOS. Signal Runner is a downloadable variant that exercises cartridge battery RAM. The generator is included, so the game files can be reproduced. This catalog is not a commercial ROM mirror.

## Source and licenses

Each core's exact source archive and license are assets in the same release as the binaries. The catalog records its upstream URL and pinned commit. Gambatte and FCEUmm retain their GPL terms; mGBA retains MPL-2.0; PCSX ReARMed retains its own GPL and component notices. See the shipped LICENSE files and source trees for full terms. FireSpot repository changes and build/packaging helpers are GPL-3.0-or-later, with inherited Apache-2.0 notices retained in NOTICE and LICENSES/Apache-2.0.txt. That does not relicense third-party binaries or the CC0 games.

The release also includes the FireSpot Phase 1 application/build source snapshot. Extract it, follow README.md, set Android SDK/NDK paths, then use `scripts/build_gameboy.sh` and `scripts/build_online_cores.py` to build the pinned cores. Building the standard APK does not bundle emulator cores. Its in-app preparation flow installs compatible support from this release.

The current application, screenshots, documentation and signed APK releases are in [Nirusaki-Malaal/firespot](https://github.com/Nirusaki-Malaal/firespot).
