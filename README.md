# OnePlus Ace 5 (PKG110) / OnePlus 13R AERA Device Tree

Device tree for building AERA Recovery (LVGL interface) for OnePlus Ace 5 (PKG110) and OnePlus 13R (CPH2645 / CPH2647 / CPH2691).

## Device Specifications

| Feature | Specification |
| :--- | :--- |
| **SoC** | Qualcomm Snapdragon 8 Gen 3 (SM8650 / pineapple) |
| **CPU** | Octa-core (1x3.3 GHz Cortex-X4 & 5x3.2 GHz Cortex-A720 & 2x2.3 GHz Cortex-A520) |
| **GPU** | Adreno 750 |
| **Display** | 6.78-inch 1.5K AMOLED, 2780 x 1264 pixels, 120Hz LTPO |
| **OS** | ColorOS 15 (Android 15) |
| **Device Codename** | **PKG110** (OnePlus Ace 5, AOSP `giuliac`), CPH2645 / CPH2647 / CPH2691 (OnePlus 13R, AOSP `giulia`) |

## Features & Bring-Up Targets

- [x] LVGL Native Touch UI (1.5K 2780x1264 display profile, 120Hz refresh)
- [x] Dynamic model detection via `libinit` (`ro.boot.prjname` 23851 -> Ace 5 PKG110)
- [x] Android 15/16 FBE v2 File-based encryption with Wrappedkey support
- [x] OPLUS Dynamic Partitions (Super partition, `my_product`, `my_heytap`, etc.)
- [x] Fastbootd & USB ADB / MTP / OTG
- [x] Hardware accelerated Adreno 750 rendering
- [x] Qualcomm PAL/AGM audio integration
- [x] AIDL Haptics and RichTap motor support
- [x] Wi-Fi networking and ADB over Wi-Fi
- [x] KernelSU, KernelSU-Next, and APatch root support

## How to Build

Use **AERA Recovery 16 Builder** (`.github/workflows/build.yml`) in Actions.
It retains the proven Ubuntu 24.04 recipe: build on the root filesystem,
add a 10 GiB swapfile, verify available swap/disk space, reclaim the `.repo`
cache after sync, and monitor memory and disk throughout compilation.
Do not substitute the older `build_aera.yml` or Colab notebook for this flow.

1. Open **Actions → AERA Recovery 16 Builder → Run workflow**.
2. Use branch `aera-16.0` for both the workflow and device tree, with the
   default target `giulia-bp2a-eng` and partition `recovery`.
3. Download `AERA-Recovery-giulia` from the successful run. Releases are drafts.

The workflow applies `patches/upstream.xml` before source sync, then applies
the patch series and runs focused Wi-Fi/download tests before building.
The artifact includes `source-manifest.xml` with the resolved source revisions.
See [patches/README.md](patches/README.md) for the upstream baseline and patch notes.

For a manual Linux build, reproduce the same workflow's resource preparation,
local manifest and patch steps before `lunch twrp_giulia-bp2a-eng` and
`mka adbd recoveryimage`. A plain `mka` command alone omits these requirements.

## AVB and image variants

`recovery.img` is the normal build output. The historical `-avb-oem.img` variant
only copies stock vbmeta; it does **not** give the modified payload a valid OEM
signature. Keep the bootloader unlocked for custom recovery. Disabling AVB by
flashing a modified `vbmeta` is not an established requirement for this tree;
the current device/firmware still needs on-device validation.
