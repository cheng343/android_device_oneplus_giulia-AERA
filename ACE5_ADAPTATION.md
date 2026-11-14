# 一加 Ace 5 (OnePlus Ace 5 / 13R) AERA Recovery 适配说明与修改清单

本说明记录了一加 Ace 5（中国版代号 `giuliac` / 型号 `PKG110`，海外对应 OnePlus 13R 代号 `giulia` / 型号 `CPH2645`、`CPH2647`、`CPH2691`）基于一加 12（`waffle`）AERA Recovery 官方设备树进行深度适配的完整技术细节与修改清单。

---

## 一、 硬件与平台对比

| 参数项 | 一加 12 (`waffle`) | 一加 Ace 5 (`giuliac` / `giulia`) | 适配处理策略 |
| :--- | :--- | :--- | :--- |
| **SoC 芯片** | 骁龙 8 Gen 3 (`SM8650` / `pineapple`) | 骁龙 8 Gen 3 (`SM8650` / `pineapple`) | **完全复用**：CPU 调度、架构配置与 Adreno 750 用户态驱动一致 |
| **屏幕尺寸与规格** | 6.82 英寸 2K 曲面屏 (3168 × 1440) | 6.78 英寸 1.5K 直屏 (2780 × 1264) | **针对性重构**：屏幕高度按 1080 宽参考空间换算，状态栏高度与左右边距按 1440 逻辑空间给定 |
| **动态分区结构** | ColorOS A/B (Super + OPLUS 子分区) | ColorOS A/B (Super + OPLUS 子分区) | **完全复用**：`my_product`, `my_heytap`, `my_bigball` 等结构一致 |
| **加密与解密** | 高通 FBE v2 + Wrappedkey | 高通 FBE v2 + Wrappedkey | **完全复用**：沿用 SM8650 vold/crypto 密钥派生链 |
| **机型识别机制** | 单一硬编码 (`waffle`) | 动态 `libinit` 读取 `ro.boot.prjname` | **新增架构**：动态识别 `23851` (Ace 5) 与 `23867~23869` (13R) |

---

## 二、 相较于一加 12 的完整修改清单

### 1. 屏幕与 LVGL UI 参数重构
* **重命名文件**：`aera_waffle.mk` $\to$ `aera_giulia.mk`
* **修改细节**：
  * `AERA_SCREEN_H := 2376`（与一加 12 相同）：该值属于 **1080 宽参考空间**，渲染器按 ×4/3 换算，2376 → 逻辑画布 **1440 × 3168**（正好等于 AERA 的设计画布）。按面板宽高比计算：1080 × 2780 / 1264 ≈ 2375.6，或 19.8 × 120 = 2376。**不要填物理像素高度（2780）**——那会让画布变成 1440 × 3706，画面竖直方向被压扁约 14.6%。
  * 注意：`AERA_STATUS_H := 115` 与 `AERA_STATUS_INDENT_LEFT/RIGHT := 40` 都是 **1440 逻辑空间的字面量（不乘 4/3）**；比例修正后 `AERA_STATUS_H := 115` 对应约 101 设备像素（若需按设备像素对齐挖孔间距，应取约 131）。
  * `AERA_STATUS_H := 115`（原一加 12 为 `120`）：适配 Ace 5 挖孔屏顶部安全距离。
  * `AERA_STATUS_INDENT_LEFT := 40`、`AERA_STATUS_INDENT_RIGHT := 40`（原为 `50 / 30`）：针对直屏对称窄边框重新平衡顶部状态栏图标边距。

### 2. 引入底层硬件动态识别库 (`libinit`)
* **新增模块目录**：`libinit/`
* **新增文件**：
  * `libinit/Android.bp`：注册 `libinit_oplus_sm86xx` 静态库，支持 Recovery 环境加载。
  * `libinit/libinit_oplus_sm86xx.cpp`：
    * 捕获内核启动命令行参数 `oplus_region` 获取地区代码。
    * 解析引导加载程序传入的工程项目代号 `ro.boot.prjname`：
      * **`23851`**：精确匹配 **OnePlus Ace 5 (PKG110 / OP5D2BL1)**。
      * **`23867` / `23868` / `23869`**：精确匹配 **OnePlus 13R (CPH2691 / CPH2645 / CPH2647)**。
    * 在 init 阶段通过 `__system_property_update` / `__system_property_add` 强制覆写只读属性（如 `ro.product.model`、`ro.product.device`、`ro.twrp.device_version` 等），防止刷机包 Assert 脚本误判拦截。
    * 将默认 Fallback 机型指定为 OnePlus Ace 5。

### 3. 底层主板构建配置调整 (`BoardConfig.mk`)
* **修改细节**：
  * `DEVICE_PATH := device/oneplus/giulia`（原为 `device/oneplus/waffle`）。
  * 引入 `TARGET_INIT_VENDOR_LIB := //$(DEVICE_PATH):libinit_oplus_sm86xx`，在构建 Recovery Ramdisk 时将 `libinit` 链接进二进制。
  * 添加 `TARGET_RECOVERY_DEVICE_MODULES += libinit_oplus_sm86xx`。
  * `AERA_DEVICE_VERSION := OnePlus_Ace_5`。
  * 保留高通 FBE v2 解密模块、Adreno 750 用户态驱动以及动态分区参数。

### 4. 产品定义与编译树入口
* **重命名文件**：`twrp_waffle.mk` $\to$ `twrp_giulia.mk`
  * 目标设备修改为 `PRODUCT_DEVICE := giulia`
  * 产品名称修改为 `PRODUCT_NAME := twrp_giulia`
  * 品牌与型号修改为 `PRODUCT_BRAND := OnePlus`、`PRODUCT_MODEL := OnePlus Ace 5`
  * 继承路径更新为 `$(call inherit-product, device/oneplus/giulia/device.mk)`
* **更新 `device.mk`**：
  * `LOCAL_PATH := device/oneplus/giulia`
  * 继承 `$(call inherit-product, $(LOCAL_PATH)/aera_giulia.mk)`
* **更新 `AndroidProducts.mk`**：
  * 导出产品描述文件 `$(LOCAL_DIR)/twrp_giulia.mk`
  * 导出 lunch 选项：`twrp_giulia-user`、`twrp_giulia-userdebug`、`twrp_giulia-eng`
* **更新 `Android.mk`**：
  * 修改判定宏为 `ifneq ($(filter giulia giuliac,$(TARGET_DEVICE)),)`，同时支持 `giulia` 与 `giuliac` 目标。

### 5. 终端环境变量与刷机白名单 (`vendorsetup.sh`)
* **修改细节**：
  * 目标设备宏修改为 `FDEVICE="giulia"`，判定逻辑兼容 `giuliac`。
  * 环境变量 `TARGET_DEVICE_ALT` 更新为：
    ```bash
    export TARGET_DEVICE_ALT="PKG110,CPH2645,CPH2647,CPH2691,OP5D2BL1,OP5D3BL1,giulia,giuliac"
    export AERA_TARGET_DEVICES="$TARGET_DEVICE_ALT"
    ```
  * 确保无论是中国版固件刷入，还是国际版 OTA 包，均能被设备识别放行。

### 6. 云端 CI 自动化工作流 (`.github/workflows/build.yml`)
* **修改细节**：
  * 默认设备路径参数更新为：`DEVICE_PATH: default: "oneplus/giulia"`
  * 默认设备名称更新为：`DEVICE_NAME: default: "giulia"`
  * 默认 Lunch 目标更新为：`LUNCH_TARGET: default: "giulia"`
  * 在 GitHub Actions 页面直接点击 **Run workflow** 即可一键自动拉取并构建 Ace 5 专属 recovery。

### 7. 说明文档 (`README.md`)
* 重写了设备规格参数表（1.5K 屏幕、Adreno 750、ColorOS 15、代号区分说明）。
* 明确了本地构建指令（`lunch twrp_giulia-eng`）与支持的 Root 方案（KernelSU / APatch / Magisk）。

---

## 三、 本地与云端构建指引

### 推荐：沿用已成功的低内存云端构建流程

使用 `.github/workflows/build.yml`，工作流名称为 **AERA Recovery 16 Builder**。
保留 Ubuntu 24.04 根分区构建、额外 10 GiB swap、同步后清理 `.repo` 缓存及内存/磁盘监控。
不要用旧 `build_aera.yml` 或 Colab 笔记本替代此流程。

1. 进入仓库 **Actions → AERA Recovery 16 Builder → Run workflow**。
2. 工作流与设备树均选 `aera-16.0`，Lunch 目标保持 `giulia-bp2a-eng`。
3. 工作流会先按 `patches/upstream.xml` 固定补丁目标版本，依序应用补丁并执行针对性测试，再编译。
4. 成功后从 Artifacts 下载 `AERA-Recovery-giulia`；Release 保持草稿状态。

本地 Linux 构建必须复现同一工作流的资源准备、local manifest 和补丁步骤，
再运行 `lunch twrp_giulia-bp2a-eng`、`mka adbd recoveryimage`。
不能只执行旧版说明中的裸 `mka` 命令。产物为 `out/target/product/giulia/recovery.img`。

---

## 四、 刷入与测试步骤

以下步骤尚需在当前固件上验证，且要求 Bootloader 已解锁。
不要因为 `-avb-oem.img` 的名称就认为镜像已获官方签名：该文件仅复制原厂 vbmeta，
其哈希描述仍对应原厂镜像，不能证明新镜像通过 AVB 校验，也不能据此重新锁定 BL。
当前仓库没有确认“必须刷修改版 vbmeta 禁用 AVB”的要求，先保留原厂 vbmeta。

对于出厂搭载 Android 15 (Virtual A/B) 的一加 Ace 5：

```bash
# 1. 进入 Fastboot / Bootloader 模式
adb reboot bootloader

# 2. 临时测试引导 (推荐先用 boot 验证触控与解密)
fastboot boot recovery.img

# 3. 永久刷入 (确认功能正常后刷入)
fastboot flash recovery recovery.img
fastboot reboot recovery
```
