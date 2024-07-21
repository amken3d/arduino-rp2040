#!/usr/bin/env python3
import os
import sys
import json

def BuildFlashMenu(name, flashsize, fssizelist):
    for fssize in fssizelist:
        if fssize == 0:
            fssizename = "no FS"
        elif fssize < 1024 * 1024:
            fssizename = "Sketch: %dKB, FS: %dKB" % ((flashsize - fssize) / 1024, fssize / 1024)
        else:
            fssizename = "Sketch: %dMB, FS: %dMB" % ((flashsize - fssize) / (1024 * 1024), fssize / (1024 * 1024))
        mn="%d_%d" % (flashsize, fssize)
        print("%s.menu.flash.%s=%dMB (%s)" % (name, mn, flashsize / (1024 * 1024), fssizename))
        print("%s.menu.flash.%s.upload.maximum_size=%d" % (name, mn, flashsize - 4096 - fssize))
        print("%s.menu.flash.%s.build.flash_total=%d" % (name, mn, flashsize))
        print("%s.menu.flash.%s.build.flash_length=%d" % (name, mn, flashsize - 4096 - fssize))
        print("%s.menu.flash.%s.build.eeprom_start=%d" % (name, mn, int("0x10000000",0) + flashsize - 4096))
        print("%s.menu.flash.%s.build.fs_start=%d" % (name, mn, int("0x10000000",0) + flashsize - 4096 - fssize))
        print("%s.menu.flash.%s.build.fs_end=%d" % (name, mn, int("0x10000000",0) + flashsize - 4096))

def BuildDebugPort(name):
    print("%s.menu.dbgport.Disabled=Disabled" % (name))
    print("%s.menu.dbgport.Disabled.build.debug_port=" % (name))
    for p in ["Serial", "Serial1", "Serial2"]:
        print("%s.menu.dbgport.%s=%s" % (name, p, p))
        print("%s.menu.dbgport.%s.build.debug_port=-DDEBUG_RP2040_PORT=%s" % (name, p, p))

def BuildDebugLevel(name):
    for l in [ ("None", ""), ("Core", "-DDEBUG_RP2040_CORE"), ("SPI", "-DDEBUG_RP2040_SPI"), ("Wire", "-DDEBUG_RP2040_WIRE"), ("Bluetooth", "-DDEBUG_RP2040_BLUETOOTH"),
               ("All", "-DDEBUG_RP2040_WIRE -DDEBUG_RP2040_SPI -DDEBUG_RP2040_CORE -DDEBUG_RP2040_BLUETOOTH"), ("NDEBUG", "-DNDEBUG") ]:
        print("%s.menu.dbglvl.%s=%s" % (name, l[0], l[0]))
        print("%s.menu.dbglvl.%s.build.debug_level=%s" % (name, l[0], l[1]))

def BuildFreq(name):
    for f in [ 133,  50, 100, 120, 125, 128, 150, 175, 200, 225, 240, 250, 275, 300]:
        warn = ""
        if f > 133: warn = " (Overclock)"
        print("%s.menu.freq.%s=%s MHz%s" % (name, f, f, warn))
        print("%s.menu.freq.%s.build.f_cpu=%dL" % (name, f, f * 1000000))

def BuildOptimize(name):
    for l in [ ("Small", "Small", "-Os", " (standard)"), ("Optimize", "Optimize", "-O", ""), ("Optimize2", "Optimize More", "-O2", ""),
               ("Optimize3", "Optimize Even More", "-O3", ""), ("Fast", "Fast", "-Ofast", " (maybe slower)"), ("Debug", "Debug", "-Og", "") ]:
        print("%s.menu.opt.%s=%s (%s)%s" % (name, l[0], l[1], l[2], l[3]))
        print("%s.menu.opt.%s.build.flags.optimize=%s" % (name, l[0], l[2]))

def BuildRTTI(name):
    print("%s.menu.rtti.Disabled=Disabled" % (name))
    print("%s.menu.rtti.Disabled.build.flags.rtti=-fno-rtti" % (name))
    print("%s.menu.rtti.Enabled=Enabled" % (name))
    print("%s.menu.rtti.Enabled.build.flags.rtti=" % (name))

def BuildStackProtect(name):
    print("%s.menu.stackprotect.Disabled=Disabled" % (name))
    print("%s.menu.stackprotect.Disabled.build.flags.stackprotect=" % (name))
    print("%s.menu.stackprotect.Enabled=Enabled" % (name))
    print("%s.menu.stackprotect.Enabled.build.flags.stackprotect=-fstack-protector" % (name))

def BuildExceptions(name):
    print("%s.menu.exceptions.Disabled=Disabled" % (name))
    print("%s.menu.exceptions.Disabled.build.flags.exceptions=-fno-exceptions" % (name))
    print("%s.menu.exceptions.Disabled.build.flags.libstdcpp=-lstdc++" % (name))
    print("%s.menu.exceptions.Enabled=Enabled" % (name))
    print("%s.menu.exceptions.Enabled.build.flags.exceptions=-fexceptions" % (name))
    print("%s.menu.exceptions.Enabled.build.flags.libstdcpp=-lstdc++-exc" % (name))

def BuildBoot(name):
    for l in [ ("Generic SPI /2", "boot2_generic_03h_2_padded_checksum"),  ("Generic SPI /4", "boot2_generic_03h_4_padded_checksum"),
            ("IS25LP080 QSPI /2", "boot2_is25lp080_2_padded_checksum"), ("IS25LP080 QSPI /4", "boot2_is25lp080_4_padded_checksum"),
            ("W25Q080 QSPI /2", "boot2_w25q080_2_padded_checksum"), ("W25Q080 QSPI /4", "boot2_w25q080_4_padded_checksum"),
            ("W25X10CL QSPI /2", "boot2_w25x10cl_2_padded_checksum"), ("W25X10CL QSPI /4", "boot2_w25x10cl_4_padded_checksum"),
            ("W25Q64JV QSPI /4", "boot2_w25q64jv_4_padded_checksum"), ("W25Q16JVxQ QSPI /4", "boot2_w25q16jvxq_4_padded_checksum"),
            ("W25Q128JV QSPI /4", "boot2_w25q128jvxq_4_padded_checksum")]:
        print("%s.menu.boot2.%s=%s" % (name, l[1], l[0]))
        print("%s.menu.boot2.%s.build.boot2=%s" % (name, l[1], l[1]))

# Abbreviated Boot Stage 2 menu for some W25Q-equipped Adafruit boards.
# In extreme overclock situations, these may require QSPI /4 to work.
def BuildBootW25Q(name):
    for l in [ ("W25Q080 QSPI /2", "boot2_w25q080_2_padded_checksum"), ("W25Q080 QSPI /4", "boot2_w25q080_4_padded_checksum")]:
        print("%s.menu.boot2.%s=%s" % (name, l[1], l[0]))
        print("%s.menu.boot2.%s.build.boot2=%s" % (name, l[1], l[1]))

def BuildUSBStack(name):
    print("%s.menu.usbstack.picosdk=Pico SDK" % (name))
    print('%s.menu.usbstack.picosdk.build.usbstack_flags=' % (name))
    print("%s.menu.usbstack.tinyusb=Adafruit TinyUSB" % (name))
    print('%s.menu.usbstack.tinyusb.build.usbstack_flags=-DUSE_TINYUSB "-I{runtime.platform.path}/libraries/Adafruit_TinyUSB_Arduino/src/arduino"' % (name))
    print("%s.menu.usbstack.tinyusb_host=Adafruit TinyUSB Host (native)" % (name))
    print('%s.menu.usbstack.tinyusb_host.build.usbstack_flags=-DUSE_TINYUSB -DUSE_TINYUSB_HOST "-I{runtime.platform.path}/libraries/Adafruit_TinyUSB_Arduino/src/arduino"' % (name))
    print("%s.menu.usbstack.nousb=No USB" % (name))
    print('%s.menu.usbstack.nousb.build.usbstack_flags="-DNO_USB -DDISABLE_USB_SERIAL -I{runtime.platform.path}/tools/libpico"' % (name))

def BuildCountry(name):
    countries = [ "Worldwide", "Australia", "Austria", "Belgium", "Brazil", "Canada", "Chile", "China", "Colombia", "Czech Republic",
                  "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hong Kong", "Hungary", "Iceland", "India", "Israel",
                  "Italy", "Japan", "Kenya", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malaysia", "Malta", "Mexico",
                  "Netherlands", "New Zealand", "Nigeria", "Norway", "Peru", "Philippines", "Poland", "Portugal", "Singapore", "Slovakia",
                  "Slovenia", "South Africa", "South Korea", "Spain", "Sweden", "Switzerland", "Taiwan", "Thailand", "Turkey", "UK", "USA"]
    for c in countries:
        sane = c.replace(" ", "_").upper()
        print("%s.menu.wificountry.%s=%s" % (name, sane.lower(), c))
        print("%s.menu.wificountry.%s.build.wificc=-DWIFICC=CYW43_COUNTRY_%s" % (name, sane.lower(), sane))

def BuildIPBTStack(name):
    print("%s.menu.ipbtstack.ipv4only=IPv4 Only" % (name))
    print('%s.menu.ipbtstack.ipv4only.build.libpicow=libpicow-noipv6-nobtc-noble.a' % (name))
    print('%s.menu.ipbtstack.ipv4only.build.libpicowdefs=-DLWIP_IPV6=0 -DLWIP_IPV4=1' % (name))
    print("%s.menu.ipbtstack.ipv4ipv6=IPv4 + IPv6" % (name))
    print('%s.menu.ipbtstack.ipv4ipv6.build.libpicow=libpicow-ipv6-nobtc-noble.a' % (name))
    print('%s.menu.ipbtstack.ipv4ipv6.build.libpicowdefs=-DLWIP_IPV6=1 -DLWIP_IPV4=1' % (name))
    print("%s.menu.ipbtstack.ipv4btcble=IPv4 + Bluetooth" % (name))
    print('%s.menu.ipbtstack.ipv4btcble.build.libpicow=libpicow-noipv6-btc-ble.a' % (name))
    print('%s.menu.ipbtstack.ipv4btcble.build.libpicowdefs=-DLWIP_IPV6=0 -DLWIP_IPV4=1 -DENABLE_CLASSIC=1 -DENABLE_BLE=1' % (name))
    print("%s.menu.ipbtstack.ipv4ipv6btcble=IPv4 + IPv6 + Bluetooth" % (name))
    print('%s.menu.ipbtstack.ipv4ipv6btcble.build.libpicow=libpicow-ipv6-btc-ble.a' % (name))
    print('%s.menu.ipbtstack.ipv4ipv6btcble.build.libpicowdefs=-DLWIP_IPV6=1 -DLWIP_IPV4=1 -DENABLE_CLASSIC=1 -DENABLE_BLE=1' % (name))
    print("%s.menu.ipbtstack.ipv4onlybig=IPv4 Only - 32K" % (name))
    print('%s.menu.ipbtstack.ipv4onlybig.build.libpicow=libpicow-noipv6-nobtc-noble-big.a' % (name))
    print('%s.menu.ipbtstack.ipv4onlybig.build.libpicowdefs=-DLWIP_IPV6=0 -DLWIP_IPV4=1 -D__LWIP_MEMMULT=2' % (name))
    print("%s.menu.ipbtstack.ipv4ipv6big=IPv4 + IPv6 - 32K" % (name))
    print('%s.menu.ipbtstack.ipv4ipv6big.build.libpicow=libpicow-ipv6-nobtc-noble-big.a' % (name))
    print('%s.menu.ipbtstack.ipv4ipv6big.build.libpicowdefs=-DLWIP_IPV6=1 -DLWIP_IPV4=1 -D__LWIP_MEMMULT=2' % (name))
    print("%s.menu.ipbtstack.ipv4btcblebig=IPv4 + Bluetooth - 32K" % (name))
    print('%s.menu.ipbtstack.ipv4btcblebig.build.libpicow=libpicow-noipv6-btc-ble-big.a' % (name))
    print('%s.menu.ipbtstack.ipv4btcblebig.build.libpicowdefs=-DLWIP_IPV6=0 -DLWIP_IPV4=1 -DENABLE_CLASSIC=1 -DENABLE_BLE=1 -D__LWIP_MEMMULT=2' % (name))
    print("%s.menu.ipbtstack.ipv4ipv6btcblebig=IPv4 + IPv6 + Bluetooth - 32K" % (name))
    print('%s.menu.ipbtstack.ipv4ipv6btcblebig.build.libpicow=libpicow-ipv6-btc-ble-big.a' % (name))
    print('%s.menu.ipbtstack.ipv4ipv6btcblebig.build.libpicowdefs=-DLWIP_IPV6=1 -DLWIP_IPV4=1 -DENABLE_CLASSIC=1 -DENABLE_BLE=1 -D__LWIP_MEMMULT=2' % (name))


def BuildUploadMethodMenu(name):
    for a, b, c, d, e, f in [ ["default", "Default (UF2)", 256, "picoprobe_cmsis_dap.tcl", "uf2conv", "uf2conv-network"],
                              ["picotool", "Picotool", 256, "picoprobe.tcl", "picotool", None],
                              ["picoprobe_cmsis_dap", "Picoprobe (CMSIS-DAP)", 256, "picoprobe_cmsis_dap.tcl", "picoprobe_cmsis_dap", None],
                              ["picodebug", "Pico-Debug", 240, "picodebug.tcl", "picodebug", None] ]:
        print("%s.menu.uploadmethod.%s=%s" % (name, a, b))
        print("%s.menu.uploadmethod.%s.build.ram_length=%dk" % (name, a, c))
        print("%s.menu.uploadmethod.%s.build.debugscript=%s" % (name, a, d))
        # For pico-debug, need to disable USB unconditionally
        if a == "picodebug":
            print("%s.menu.uploadmethod.%s.build.picodebugflags=-UUSE_TINYUSB -DNO_USB -DDISABLE_USB_SERIAL -I{runtime.platform.path}/tools/libpico" % (name, a))
        elif a == "picotool":
            print("%s.menu.uploadmethod.%s.build.picodebugflags=-DENABLE_PICOTOOL_USB" % (name, a))
        print("%s.menu.uploadmethod.%s.upload.maximum_data_size=%d" % (name, a, c * 1024))
        print("%s.menu.uploadmethod.%s.upload.tool=%s" % (name, a, e))
        print("%s.menu.uploadmethod.%s.upload.tool.default=%s" % (name, a, e))
        if f != None:
            print("%s.menu.uploadmethod.%s.upload.tool.network=%s" % (name, a, f))

def BuildHeader(name, vendor_name, product_name, vid, pid, pwr, boarddefine, variant, flashsize, boot2, extra):
    prettyname = vendor_name + " " + product_name
    print()
    print("# -----------------------------------")
    print("# %s" % (prettyname))
    print("# -----------------------------------")
    print("%s.name=%s" % (name, prettyname))

    # USB Vendor ID / Product ID (VID/PID) pairs for board detection
    if isinstance(pid, list):
        # Explicitly specified list of PIDs (with the same VID)
        usb_pids = pid
    else:
        # When the RP2040 is used as a composite device, the PID is modified
        # (see cores/rp2040/RP2040USB.cpp) because Windows wants a different
        # VID:PID for different device configurations [citation needed?].
        # See https://github.com/earlephilhower/arduino-pico/issues/796
        #
        # TODO FIX: Some PIDs already have these bits set, and there's no
        # guarantee mangling PIDs this way won't collide with other devices.
        usb_pids = []
        for k_bit in [0, 0x8000]:
            for m_bit in [0, 0x4000]:
                for j_bit in [0, 0x0100]:
                    this_pid = "0x%04x" % (int(pid, 16) | k_bit | m_bit | j_bit)
                    if this_pid not in usb_pids:
                        usb_pids.append(this_pid)

    main_pid = usb_pids[0]

    # Old style VID/PID list for compatibility with older Arduino tools
    for i, pid in enumerate(usb_pids):
        print("%s.vid.%d=%s" % (name, i, vid))
        print("%s.pid.%d=%s" % (name, i, pid))

    # Since our platform.txt enables pluggable discovery, we are also required
    # to list VID/PID in this format
    for i, pid in enumerate(usb_pids):
        print("%s.upload_port.%d.vid=%s" % (name, i, vid))
        print("%s.upload_port.%d.pid=%s" % (name, i, pid))

    print("%s.build.usbvid=-DUSBD_VID=%s" % (name, vid))
    print("%s.build.usbpid=-DUSBD_PID=%s" % (name, main_pid))
    print("%s.build.usbpwr=-DUSBD_MAX_POWER_MA=%s" % (name, pwr))
    print("%s.build.board=%s" % (name, boarddefine))
    print("%s.build.mcu=cortex-m0plus" % (name))
    print("%s.build.variant=%s" % (name, variant))
    print("%s.upload.maximum_size=%d" % (name, flashsize))
    print("%s.upload.wait_for_upload_port=true" % (name))
    print("%s.upload.erase_cmd=" % (name))
    print("%s.serial.disableDTR=false" % (name))
    print("%s.serial.disableRTS=false" % (name))
    print("%s.build.f_cpu=125000000" % (name))
    print("%s.build.led=" % (name))
    print("%s.build.core=rp2040" % (name))
    print("%s.build.ldscript=memmap_default.ld" % (name))
    print("%s.build.boot2=%s" % (name, boot2))
    print('%s.build.usb_manufacturer="%s"' % (name, vendor_name))
    print('%s.build.usb_product="%s"' % (name, product_name))
    if extra != None:
        m_extra = ''
        for m_item in extra:
            m_extra += '-D' + m_item + ' '
        print('%s.build.extra_flags=%s' % (name, m_extra.rstrip()))

def WriteWarning():
    print("# WARNING - DO NOT EDIT THIS FILE, IT IS MACHINE GENERATED")
    print("#           To change something here, edit tools/makeboards.py and")
    print("#           run 'python3 makeboards.py > ../boards.txt' to regenerate")
    print()

def BuildGlobalMenuList():
    print("menu.BoardModel=Model")
    print("menu.flash=Flash Size")
    print("menu.freq=CPU Speed")
    print("menu.opt=Optimize")
    print("menu.rtti=RTTI")
    print("menu.stackprotect=Stack Protector")
    print("menu.exceptions=C++ Exceptions")
    print("menu.dbgport=Debug Port")
    print("menu.dbglvl=Debug Level")
    print("menu.boot2=Boot Stage 2")
    print("menu.wificountry=WiFi Region")
    print("menu.usbstack=USB Stack")
    print("menu.ipbtstack=IP/Bluetooth Stack")
    print("menu.uploadmethod=Upload Method")

def MakeBoard(name, vendor_name, product_name, vid, pid, pwr, boarddefine, flashsizemb, boot2, extra = None, board_url = None):
    fssizelist = [ 0, 64 * 1024, 128 * 1024, 256 * 1024, 512 * 1024 ]
    for i in range(1, flashsizemb):
        fssizelist.append(i * 1024 * 1024)
    BuildHeader(name, vendor_name, product_name, vid, pid, pwr, boarddefine, name, flashsizemb * 1024 * 1024, boot2, extra)
    if (name == "generic") or (name == "vccgnd_yd_rp2040"):
        BuildFlashMenu(name, 2*1024*1024, [0, 1*1024*1024])
        BuildFlashMenu(name, 4*1024*1024, [0, 3*1024*1024, 2*1024*1024])
        BuildFlashMenu(name, 8*1024*1024, [0, 7*1024*1024, 4*1024*1024, 2*1024*1024])
        BuildFlashMenu(name, 16*1024*1024, [0, 15*1024*1024, 14*1024*1024, 12*1024*1024, 8*1024*1024, 4*1024*1024, 2*1024*1024])
    elif name == "pimoroni_tiny2040":
        BuildFlashMenu(name, 2*1024*1024, fssizelist)
        BuildFlashMenu(name, 8*1024*1024, [0, 7*1024*1024, 4*1024*1024, 2*1024*1024])
    elif name == "akana_r1":
        BuildFlashMenu(name, 2*1024*1024, [0, 1*1024*1024])
        BuildFlashMenu(name, 8*1024*1024, [0, 7*1024*1024, 4*1024*1024, 2*1024*1024])
        BuildFlashMenu(name, 16*1024*1024, [0, 15*1024*1024, 14*1024*1024, 12*1024*1024, 8*1024*1024, 4*1024*1024, 2*1024*1024])
    else:
        BuildFlashMenu(name, flashsizemb * 1024 * 1024, fssizelist)
    BuildFreq(name)
    BuildOptimize(name)
    BuildRTTI(name)
    BuildStackProtect(name)
    BuildExceptions(name)
    BuildDebugPort(name)
    BuildDebugLevel(name)
    BuildUSBStack(name)
    if name == "rpipicow":
        BuildCountry(name)
    BuildIPBTStack(name)
    if name == "generic":
        BuildBoot(name)
    elif name.startswith("adafruit") and "w25q080" in boot2:
        BuildBootW25Q(name)
    BuildUploadMethodMenu(name)
    MakeBoardJSON(name, vendor_name, product_name, vid, pid, pwr, boarddefine, flashsizemb, boot2, extra, board_url)
    global pkgjson
    thisbrd = {}
    thisbrd['name'] = "%s %s" % (vendor_name, product_name)
    pkgjson['packages'][0]['platforms'][0]['boards'].append(thisbrd)

def MakeBoardJSON(name, vendor_name, product_name, vid, pid, pwr, boarddefine, flashsizemb, boot2, extra, board_url):
    # TODO FIX: Use the same expanded PID list as in BuildHeader above?
    if isinstance(pid, list):
        pid = pid[0]
    if extra != None:
        m_extra = ' '
        for m_item in extra:
            m_extra += '-D' + m_item + ' '
    else:
        m_extra = ''
    json = """{
  "build": {
    "arduino": {
      "earlephilhower": {
        "boot2_source": "BOOT2.S",
        "usb_vid": "VID",
        "usb_pid": "PID"
      }
    },
    "core": "earlephilhower",
    "cpu": "cortex-m0plus",
    "extra_flags": "-D ARDUINO_BOARDDEFINE -DARDUINO_ARCH_RP2040 -DUSBD_MAX_POWER_MA=USBPWR EXTRA_INFO",
    "f_cpu": "133000000L",
    "hwids": [
      [
        "0x2E8A",
        "0x00C0"
      ],
      [
        "VID",
        "PID"
      ]
    ],
    "mcu": "rp2040",
    "variant": "VARIANTNAME"
  },
  "debug": {
    "jlink_device": "RP2040_M0_0",
    "openocd_target": "rp2040.cfg",
    "svd_path": "rp2040.svd"
  },
  "frameworks": [
    "arduino"
  ],
  "name": "PRODUCTNAME",
  "upload": {
    "maximum_ram_size": 270336,
    "maximum_size": FLASHSIZE,
    "require_upload_port": true,
    "native_usb": true,
    "use_1200bps_touch": true,
    "wait_for_upload_port": false,
    "protocol": "picotool",
    "protocols": [
      "blackmagic",
      "cmsis-dap",
      "jlink",
      "raspberrypi-swd",
      "picotool",
      "picoprobe",
      "pico-debug"
    ]
  },
  "url": "BOARDURL",
  "vendor": "VENDORNAME"
}\n"""\
.replace('VARIANTNAME', name)\
.replace('BOARDDEFINE', boarddefine)\
.replace('BOOT2', boot2)\
.replace('VID', vid.upper().replace("X", "x"))\
.replace('PID', pid.upper().replace("X", "x"))\
.replace('BOARDURL', board_url or 'https://www.raspberrypi.org/products/raspberry-pi-pico/')\
.replace('VENDORNAME', vendor_name)\
.replace('PRODUCTNAME', product_name)\
.replace('FLASHSIZE', str(1024*1024*flashsizemb))\
.replace('USBPWR', str(pwr))\
.replace(' EXTRA_INFO', m_extra.rstrip())
    jsondir = os.path.abspath(os.path.dirname(__file__)) + "/json"
    f = open(jsondir + "/" + name + ".json", "w", newline='\n')
    f.write(json)
    f.close()

pkgjson = json.load(open(os.path.abspath(os.path.dirname(__file__)) + '/../package/package_pico_index.template.json'))
pkgjson['packages'][0]['platforms'][0]['boards'] = []

sys.stdout = open(os.path.abspath(os.path.dirname(__file__)) + "/../boards.txt", "w", newline='\n')
WriteWarning()
BuildGlobalMenuList()

# Note to new board manufacturers:  Please add your board so that it sorts
# alphabetically starting with the company name and then the board name.
# Otherwise it is difficult to find a specific board in the menu.

# Raspberry Pi
MakeBoard("rpipico", "Raspberry Pi", "Pico", "0x2e8a", "0x000a", 250, "RASPBERRY_PI_PICO", 2, "boot2_w25q080_2_padded_checksum")

#Amken
MakeBoard("amken_bunny","Amken","BunnyBoard","0x2770",["0x7303"],250,"AMKEN_BB",128,"boot2_w25q128jvxq_4_padded_checksum","","https://www.amken3d.com")
MakeBoard("amken_revelop","Amken","Revelop","0x2770",["0x7304"],250,"AMKEN_REVELOP",32,"boot2_W25Q32JVxQ_4_padded_checksum","","https://www.amken3d.com")
MakeBoard("amken_revelop_plus","Amken","Revelop Plus","0x2770",["0x7305"],250,"AMKEN_REVELOP_PLUS",32,"boot2_W25Q32JVxQ_4_padded_checksum","","https://www.amken3d.com")
MakeBoard("amken_revelop_es","Amken","Revelop eS","0x2770",["0x7306"],250,"AMKEN_ES",16,"boot2_w25q16jvxq_4_padded_checksum","","https://www.amken3d.com")

# Generic
MakeBoard("generic", "Generic", "RP2040", "0x2e8a", "0xf00a", 250, "GENERIC_RP2040", 16, "boot2_generic_03h_4_padded_checksum")

sys.stdout.close()
with open(os.path.abspath(os.path.dirname(__file__)) + '/../package/package_pico_index.template.json', 'w', newline='\n') as f:
    f.write(json.dumps(pkgjson, indent=3))
