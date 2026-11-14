# Upstream baseline (2026-11-14)

- Device reference: `AERA-Recovery/android_device_oneplus_waffle-AERA` at `5610a89a115c0aa3b1e87a6f6cdab08ce001d4eb`.
  Includes the sideload fix that leaves the ADB FunctionFS endpoint to minadbd.
- `bootable/recovery`: `e438f6de62090a79e81daf00b449b48da7377753`.
- `vendor/recovery`: `1f4b6e19882c83f95d1420872d0c31be0b97a7a6`.

`upstream.xml` pins the two patched projects. Other projects follow the AERA
manifest; the workflow exports a resolved manifest before deleting `.repo`.

Apply each project's `*.patch` files in filename order. Recovery patch numbers
intentionally skip 0005: its old total-deadline downloader is superseded by
upstream's inactivity deadline, cancellation and process-group cleanup.

The seven remaining recovery patches preserve the network-ID fix, boot credit,
first-boot language selection, device WLAN firmware staging, store mirrors,
GitHub contents API and release asset API support. The rebase keeps upstream's
hidden-network/raw-PSK support, static-IP/DHCP handling, monotonic association
deadlines, session language selection, font and keyboard preferences.
Both fresh and saved Wi-Fi connections use the ID returned by ADD_NETWORK.
Asset API requests pass the Accept header through upstream's downloader.

Validation: apply the complete series to clean baseline checkouts, then run
the workflow's Wi-Fi and plugin downloader tests and full recovery build.
Hardware behavior (touch, decryption, Wi-Fi, sideload and bootloader acceptance)
still requires on-device testing.
