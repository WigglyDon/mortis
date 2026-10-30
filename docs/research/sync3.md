# SYNC 3 and wireless Android Auto

Research started October 30, 2026.

Follow-up: the [inventory experiment](../experiments/001-apim-inventory.md) records the verified Ford download and prepared USB files. The [native implementation investigation](wireless-native.md) records source-level protocol findings and the receiver transport experiment.

## Objective

Investigate whether Mortis's SYNC 3 can run our own wireless Android Auto implementation using its existing hardware. Existing mods are useful references; technical feasibility will be decided by the hardware, software interfaces, and experiments.

## Known starting point

The owner reports SYNC 3.3 with build `19052_PRODUCT` in a 2020 Ford Transit Connect XLT. The exact APIM hardware revision has not yet been collected.

Ford's stock SYNC 3 Android Auto instructions use USB. Connecting SYNC to a phone hotspot does not enable a wireless projection receiver. See [Ford's SYNC 3 Android Auto instructions](https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1931718&Uid=G1931757&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G1733535&userMarket=USA&vFilteringEnabled=False&variantid=7031).

## Operating system and native software

SYNC 3 is based on QNX. BlackBerry's [announcement with Ford](https://www.globenewswire.com/fr/news-release/2016/10/31/1297229/0/en/blackberry-signs-agreement-with-ford-motor-company-for-expanded-use-of-blackberry-s-qnx-and-security-software.html) identifies QNX as the operating system used by SYNC 3.

QNX Neutrino uses a microkernel and process manager packaged as `procnto`. Many system services run as separate processes, and the operating system provides POSIX programming interfaces. See [QNX's architecture documentation](https://qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_sys_arch/kernel.html).

The [Quake II port for SYNC 3](https://github.com/bigunclemax/ford_s3_quake_mod) describes a QNX 6.5/6.6 target and provides a concrete example of native third-party software. It does not establish the exact QNX release or access conditions on Mortis's module.

A kernel replacement is not inherently necessary for the proposed experiment. A native service and changes to the existing receiver may be sufficient if the required driver and receiver interfaces are accessible. This is a proposed architecture, not a verified result.

## Radio evidence

Ford's [declaration of conformity](https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1982009&Uid=G2055266&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G1724568&userMarket=GBR&vFilteringEnabled=False&variantid=7786) lists the Panasonic FG-185-SG32MH among SYNC 3 variants. Panasonic's [certification filing](https://fccid.io/ACJ-FG-185-SG32MH) includes 2.4 GHz and 5 GHz operation.

This establishes that some SYNC 3 hardware has dual-band Wi-Fi. Mortis's installed module and its driver capabilities still need to be identified. Radio frequency support alone does not establish the access-point or peer-to-peer modes needed for a particular implementation.

## Direct USB inspection

During the initial inspection, the owner reported a Mac connected directly to the van's USB port. Mac USB enumeration showed a separate Pixel phone and no Ford/SYNC device. No SYNC serial console or external physical disk appeared.

The commands used were:

```sh
ioreg -p IOUSB -w 0
ioreg -r -c IOUSBHostDevice -l -w 0
diskutil list external physical
ls -l /dev/cu.* /dev/tty.*
```

This did not provide a shell, filesystem access, or a kernel version from SYNC. It does not establish that other USB access methods are impossible.

For Android USB accessory mode, the attached accessory acts as the USB host; see [Android's USB accessory documentation](https://developer.android.com/develop/connectivity/usb/accessory). The observed lack of a SYNC device on the Mac is consistent with a connection that has not established a usable host/device data relationship. The USB roles on this specific connection were not directly measured.

## Next inspection method

The [APIM Interrogator guide](https://community.cyanlabs.net/t/apim-interrogator-utility-create-interrogator-log/1856) documents a Ford information-gathering utility that writes an XML log to a USB flash drive without changing the installed SYNC software or firmware. It lists `GB5T-14G386-AB` for SYNC 3.2/3.3.

The inventory can report hardware and software part numbers, installed packages, storage information, and configuration. Review the output locally and publish only the relevant technical fields after removing identifiers. This inventory is not a shell or a complete driver/process inspection.

For a 2020 vehicle, confirm the actual hardware before using older upgrade procedures: CyanLabs [documents a reformat incompatibility with MY20 units](https://cyanlabs.net/tutorials/sync-3-manual-method-update-to-3-4/).

## Questions to answer experimentally

1. What APIM hardware, processor, QNX release, and radio are installed?
2. Can we run a compatible native diagnostic program and inspect the relevant drivers?
3. Can the Wi-Fi driver host a connection in a mode usable by the phone?
4. Can we implement the Bluetooth discovery and wireless session setup?
5. Can Ford's Android Auto receiver accept a network transport, or can we modify its USB transport boundary?
6. Can the resulting system handle audio, calls, input, startup, reconnection, and ignition cycles reliably?

## Reference implementations

- [WirelessAndroidAutoDongle](https://github.com/nisargjhaveri/WirelessAndroidAutoDongle) bridges wireless Android Auto to a wired receiver using a Linux board with USB gadget support.
- [aa-proxy-rs](https://github.com/aa-proxy/aa-proxy-rs) provides another implementation of a wireless-to-USB bridge.
- [FMods documentation](https://www.fmods.net/community/faqpage) describes the SYNC 3 community's custom software installation tools.

These establish useful approaches and examples. Their code and installation methods have not been validated on Mortis, and Linux-specific USB and driver code will require a different implementation or adaptation for QNX.
