#!/usr/bin/env python3

import argparse
import os

from litex.soc.integration.builder import Builder

from soc_linux import SoCLinux, video_resolutions

kB = 1024

# Board definition----------------------------------------------------------------------------------

class Board:
    def __init__(self, soc_cls, soc_capabilities):
        self.soc_cls = soc_cls
        self.soc_capabilities = soc_capabilities

    def load(self):
        raise NotImplementedError

    def flash(self):
        raise NotImplementedError

# Arty support -------------------------------------------------------------------------------------

class Arty(Board):
    SPIFLASH_PAGE_SIZE    = 256
    SPIFLASH_SECTOR_SIZE  = 64*kB
    SPIFLASH_DUMMY_CYCLES = 11
    def __init__(self):
        from litex_boards.targets import arty
        Board.__init__(self, arty.EthernetSoC, {"serial", "ethernet", "spiflash", "leds", "rgb_led", "switches", "spi", "i2c", "xadc", "icap_bit", "mmcm"})

    def load(self):
        from litex.build.openocd import OpenOCD
        prog = OpenOCD("prog/openocd_xilinx.cfg")
        prog.load_bitstream("build/arty/gateware/top.bit")

    def flash(self):
        flash_regions = {
            "buildroot/Image.fbi":             "0x00000000", # Linux Image: copied to 0xc0000000 by bios
            "buildroot/rootfs.cpio.fbi":       "0x00500000", # File System: copied to 0xc0800000 by bios
            "buildroot/rv32.dtb.fbi":          "0x00d00000", # Device tree: copied to 0xc1000000 by bios
            "emulator/emulator.bin.fbi":       "0x00e00000", # MM Emulator: copied to 0x20000000 by bios
        }
        from litex.build.openocd import OpenOCD
        prog = OpenOCD("prog/openocd_xilinx.cfg",
            flash_proxy_basename="prog/bscan_spi_xc7a35t.bit")
        prog.set_flash_proxy_dir(".")
        for filename, base in flash_regions.items():
            base = int(base, 16)
            print("Flashing {} at 0x{:08x}".format(filename, base))
            prog.flash(base, filename)

# NeTV2 support ------------------------------------------------------------------------------------

class NeTV2(Board):
    SPIFLASH_PAGE_SIZE    = 256
    SPIFLASH_SECTOR_SIZE  = 64*kB
    SPIFLASH_DUMMY_CYCLES = 11
    def __init__(self):
        from litex_boards.targets import netv2
        Board.__init__(self, netv2.EthernetSoC, {"serial", "ethernet", "framebuffer", "spiflash", "leds", "xadc"})

    def load(self):
        from litex.build.openocd import OpenOCD
        prog = OpenOCD("prog/openocd_netv2_rpi.cfg")
        prog.load_bitstream("build/netv2/gateware/top.bit")

# Genesys2 support ---------------------------------------------------------------------------------

class Genesys2(Board):
    def __init__(self):
        from litex_boards.targets import genesys2
        Board.__init__(self, genesys2.EthernetSoC, {"serial", "ethernet"})

    def load(self):
        from litex.build.xilinx import VivadoProgrammer
        prog = VivadoProgrammer()
        prog.load_bitstream("build/genesys2/gateware/top.bit")

# KC705 support ---------------------------------------------------------------------------------

class KC705(Board):
    def __init__(self):
        from litex_boards.targets import kc705
        Board.__init__(self, kc705.EthernetSoC, {"serial", "ethernet", "leds", "xadc"})

    def load(self):
        from litex.build.xilinx import VivadoProgrammer
        prog = VivadoProgrammer()
        prog.load_bitstream("build/kc705/gateware/top.bit")


# KCU105 support -----------------------------------------------------------------------------------

class KCU105(Board):
    def __init__(self):
        from litex_boards.targets import kcu105
        Board.__init__(self, kcu105.EthernetSoC, {"serial", "ethernet"})

    def load(self):
        from litex.build.xilinx import VivadoProgrammer
        prog = VivadoProgrammer()
        prog.load_bitstream("build/kcu105/gateware/top.bit")


# Nexys4DDR support --------------------------------------------------------------------------------

class Nexys4DDR(Board):
    def __init__(self):
        from litex_boards.targets import nexys4ddr
        Board.__init__(self, nexys4ddr.EthernetSoC, {"serial", "ethernet"})

    def load(self):
        from litex.build.xilinx import VivadoProgrammer
        prog = VivadoProgrammer()
        prog.load_bitstream("build/nexys4ddr/gateware/top.bit")

# NexysVideo support -------------------------------------------------------------------------------

class NexysVideo(Board):
    def __init__(self):
        from litex_boards.targets import nexys_video
        Board.__init__(self, nexys_video.EthernetSoC, {"serial", "framebuffer"})

    def load(self):
        from litex.build.xilinx import VivadoProgrammer
        prog = VivadoProgrammer()
        prog.load_bitstream("build/nexys_video/gateware/top.bit")

# MiniSpartan6 support -----------------------------------------------------------------------------

class MiniSpartan6(Board):
    def __init__(self):
        from litex_boards.targets import minispartan6
        Board.__init__(self, minispartan6.BaseSoC, {"serial"})

    def load(self):
        os.system("xc3sprog -c ftdi build/minispartan6/gateware/top.bit")


# Pipistrello support ------------------------------------------------------------------------------

class Pipistrello(Board):
    def __init__(self):
        from litex_boards.targets import pipistrello
        Board.__init__(self, pipistrello.BaseSoC, {"serial"})

    def load(self):
        os.system("fpgaprog -f build/pipistrello/gateware/top.bit")


# Versa ECP5 support -------------------------------------------------------------------------------

class VersaECP5(Board):
    SPIFLASH_PAGE_SIZE    = 256
    SPIFLASH_SECTOR_SIZE  = 64*kB
    SPIFLASH_DUMMY_CYCLES = 11
    def __init__(self):
        from litex_boards.targets import versa_ecp5
        Board.__init__(self, versa_ecp5.EthernetSoC, {"serial", "ethernet", "spiflash"})

    def load(self):
        os.system("openocd -f prog/ecp5-versa5g.cfg -c \"transport select jtag; init; svf build/versa_ecp5/gateware/top.svf; exit\"")

# ULX3S support ------------------------------------------------------------------------------------

class ULX3S(Board):
    def __init__(self):
        from litex_boards.targets import ulx3s
        Board.__init__(self, ulx3s.BaseSoC, {"serial"})

    def load(self):
        os.system("ujprog build/ulx3s/gateware/top.svf")

# HADBadge support ---------------------------------------------------------------------------------

class HADBadge(Board):
    SPIFLASH_PAGE_SIZE    = 256
    SPIFLASH_SECTOR_SIZE  = 64*kB
    SPIFLASH_DUMMY_CYCLES = 6
    FLASH_REGIONS = [
        #"": "0x00000000", # FPGA bootloader image:  loaded at startup
        #"build/hadbadge/gateware/ecp5_compress_qspi_38.8M.bit":
        #                               "0x00180000", # FPGA user image 
        ["buildroot/Image",        "KERNEL_IMAGE",       "0x00400000"], # Linux Image: copied to 0xc0000000 by bios
        ["buildroot/rootfs.cpio",  "ROOTFS_IMAGE",       "0x00880000"], # File System: copied to 0xc0800000 by bios
        ["buildroot/rv32.dtb",     "DEVICE_TREE_IMAGE",  "0x00f00000"], # Device tree: copied to 0xc1000000 by bios
        ["emulator/emulator.bin",  "EMULATOR_IMAGE",     "0x00f01000"], # MM Emulator: copied to 0x20000000 by bios
    ]

    def __init__(self):
        from litex_boards.targets import hadbadge
        #Board.__init__(self, hadbadge.BaseSoC, {"serial", "spiflash"})     
        Board.__init__(self, hadbadge.BaseSoC, {"usb_cdc", "spiflash"})     

    def flash(self):
        import struct
        import binascii

        flash_regions_final = self.FLASH_REGIONS
        flash_regions = {}

        # hadbadge DFU lets you flash user data starting at address 0x00200000
        # So we shift all offsets so they end up in the right place
        offset = int("0x00200000", 16)
        for filename, _, base in flash_regions_final:
            base = int(base, 16)
            new_address = base - offset
            flash_regions[filename] = new_address


        # Create binary with all 4 blocks. 
        # Each block has the following format
        #
        # 0x0000    : <length of payload (bytes)>
        # 0x0004    : <crc32 covering payload>
        # 0x0008    : payload
        # length + 8: last byte of payload
        output_file = 'build/hadbadge/gateware/flash_image.bin'
        total_len = 0
        with open(output_file, "wb") as f:
            for filename, base in flash_regions.items():
                data = open(filename, "rb").read()
                crc = binascii.crc32(data)
                
                data_write = bytearray()
                data_write += struct.pack('<I', len(data)) # len
                data_write += struct.pack('<I', crc) # CRC
                data_write += data
                # Print some stats, data is useful for checking vaild data loaded.
                print(f' ')
                print(f'Inserting: {filename:60}')
                print(f'  Start address: 0x{base:08x}')
                print(f'  Length       : 0x{len(data):08x} bytes')
                print(f'  crc32        : 0x{crc:08x}')
                print(f'           data: ' + f' '.join(f'{i:02x}' for i in data_write[:16]))
                f.seek(base)
                f.write(data_write)

                total_len += len(data_write)

        # Print some stats
        remain = 16*1024*1024 - (
            0x200000 + total_len)
        print("-"*40)
        print(("      Total Image Size: {:10} bytes"
               " ({} Megabits, {:.2f} Megabytes)"
               ).format(total_len, int(total_len*8/1024/1024), total_len/1024/1024))
        print("-"*40)
        print(("       Remaining space: {:10} bytes"
               " ({} Megabits, {:.2f} Megabytes)"
               ).format(remain, int(remain*8/1024/1024), remain/1024/1024))
        total = 16*1024*1024 - (0x200000)
        print(("           Total space: {:10} bytes"
               " ({} Megabits, {:.2f} Megabytes)"
               ).format(total, int(total*8/1024/1024), total/1024/1024))

    # create a compress bitstream with faster SPI parameters. This speeds up loading.
        build_name = 'build/hadbadge/gateware/top.config'
        ecp5_bitstream = 'build/hadbadge/gateware/ecp5_bitstream.bit'
        os.system(f'ecppack {build_name} --compress --spimode qspi --freq 38.8 --bit {ecp5_bitstream}')
        
        
        os.system("dfu-util -d 1d50:614b --alt 2 --download build/hadbadge/gateware/ecp5_bitstream.bit")
        os.system("dfu-util -d 1d50:614b --alt 4 --download build/hadbadge/gateware/flash_image.bin --reset")

    def load(self):
        os.system("dfu-util -d 1d50:614b --alt 2 --download build/hadbadge/gateware/top.bit --reset")

# OrangeCrab support -------------------------------------------------------------------------------

class OrangeCrab(Board):
    def __init__(self):
        from litex_boards.targets import orangecrab
        Board.__init__(self, orangecrab.BaseSoC, {"serial"})

    def load(self):
        os.system("openocd -f openocd/ecp5-versa5g.cfg -c \"transport select jtag; init; svf build/gateware/top.svf; exit\"")

# Cam Link 4K support ------------------------------------------------------------------------------

class CamLink4K(Board):
    def __init__(self):
        from litex_boards.targets import camlink_4k
        Board.__init__(self, camlink_4k.BaseSoC, {"serial"})

    def load(self):
        os.system("camlink configure build/gateware/top.bit")

# De10Lite support ---------------------------------------------------------------------------------

class De10Lite(Board):
    def __init__(self):
        from litex_boards.targets import de10lite
        Board.__init__(self, de10lite.BaseSoC, {"serial"})

    def load(self):
        from litex.build.altera import USBBlaster
        prog = USBBlaster()
        prog.load_bitstream("build/de10lite/gateware/top.sof")

# De10Nano support ----------------------------------------------------------------------------------

class De10Nano(Board):
    def __init__(self):
        from litex_boards.targets import de10nano
        Board.__init__(self, de10nano.MiSTerSDRAMSoC, {"serial", "leds", "switches"})

    def load(self):
        from litex.build.altera import USBBlaster
        prog = USBBlaster()
        prog.load_bitstream("build/de10nano/gateware/top.sof")

# De0Nano support ----------------------------------------------------------------------------------

class De0Nano(Board):
    def __init__(self):
        from litex_boards.targets import de0nano
        Board.__init__(self, de0nano.BaseSoC, {"serial"})

    def load(self):
        from litex.build.altera import USBBlaster
        prog = USBBlaster()
        prog.load_bitstream("build/de0nano/gateware/top.sof")

# Main ---------------------------------------------------------------------------------------------

supported_boards = {
    # Xilinx
    "arty":         Arty,
    "netv2":        NeTV2,
    "genesys2":     Genesys2,
    "kc705":        KC705,
    "kcu105":       KCU105,
    "nexys4ddr":    Nexys4DDR,
    "nexys_video":  NexysVideo,
    "minispartan6": MiniSpartan6,
    "pipistrello":  Pipistrello,
    # Lattice
    "versa_ecp5":   VersaECP5,
    "ulx3s":        ULX3S,
    "hadbadge":     HADBadge,
    "orangecrab":   OrangeCrab,
    "camlink_4k":   CamLink4K,
    # Altera/Intel
    "de0nano":      De0Nano,
    "de10lite":     De10Lite,
    "de10nano":     De10Nano,
}

def main():
    description = "Linux on LiteX-VexRiscv\n\n"
    description += "Available boards:\n"
    for name in supported_boards.keys():
        description += "- " + name + "\n"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--board", required=True, help="FPGA board")
    parser.add_argument("--build", action="store_true", help="build bitstream")
    parser.add_argument("--load", action="store_true", help="load bitstream (to SRAM)")
    parser.add_argument("--flash", action="store_true", help="flash bitstream/images (to SPI Flash)")
    parser.add_argument("--local-ip", default="192.168.1.50", help="local IP address")
    parser.add_argument("--remote-ip", default="192.168.1.100", help="remote IP address of TFTP server")
    parser.add_argument("--spi-bpw", type=int, default=8, help="Bits per word for SPI controller")
    parser.add_argument("--spi-sck-freq", type=int, default=1e6, help="SPI clock frequency")
    parser.add_argument("--video", default="1920x1080_60Hz", help="video configuration")
    parser.add_argument("--fbi", action="store_true", help="generate fbi images")
    args = parser.parse_args()

    if args.board == "all":
        board_names = list(supported_boards.keys())
    else:
        args.board = args.board.lower()
        args.board = args.board.replace(" ", "_")
        board_names = [args.board]
    for board_name in board_names:
        board = supported_boards[board_name]()
        soc_kwargs = {"integrated_rom_size": 0x8000}
        if board_name in ["versa_ecp5", "ulx3s", "hadbadge", "orangecrab"]:
            soc_kwargs["toolchain"] = "trellis"
        if board_name in ["de0nano"]:
            soc_kwargs["l2_size"] = 2048 # Not enough blockrams for default l2_size of 8192
        if board_name in ["kc705"]:
            soc_kwargs["uart_baudrate"] = 500e3 # Set UART baudrate to 500KBauds since 1Mbauds not supported
        soc = SoCLinux(board.soc_cls, **soc_kwargs)
        if "spiflash" in board.soc_capabilities:
            soc.add_spi_flash(dummy_cycles=board.SPIFLASH_DUMMY_CYCLES)
            soc.add_constant("SPIFLASH_PAGE_SIZE", board.SPIFLASH_PAGE_SIZE)
            soc.add_constant("SPIFLASH_SECTOR_SIZE", board.SPIFLASH_SECTOR_SIZE)
            if hasattr(board,'FLASH_REGIONS'):
                for _, name, offset in board.FLASH_REGIONS:
                    soc.add_constant(f'{name}_FLASH_OFFSET', int(offset,16))
        if "ethernet" in board.soc_capabilities:
            soc.configure_ethernet(local_ip=args.local_ip, remote_ip=args.remote_ip)
        if "leds" in board.soc_capabilities:
            soc.add_leds()
        if "rgb_led" in board.soc_capabilities:
            soc.add_rgb_led()
        if "switches" in board.soc_capabilities:
            soc.add_switches()
        if "spi" in board.soc_capabilities:
            soc.add_spi(args.spi_bpw, args.spi_sck_freq)
        if "i2c" in board.soc_capabilities:
            soc.add_i2c()
        if "xadc" in board.soc_capabilities:
            soc.add_xadc()
        if "framebuffer" in board.soc_capabilities:
            assert args.video in video_resolutions.keys(), "Unsupported video resolution"
            video_settings = video_resolutions[args.video]
            soc.add_framebuffer(video_settings)
        if "icap_bit" in board.soc_capabilities:
            soc.add_icap_bitstream()
        if "mmcm" in board.soc_capabilities:
            soc.add_mmcm()
        if "usb_cdc" in board.soc_capabilities:
            soc.add_serial_cdc()
        soc.configure_boot()

        build_dir = os.path.join("build", board_name)
        if args.build:
            builder = Builder(soc, output_dir=build_dir,
                csr_json=os.path.join(build_dir, "csr.json"))
        else:
            builder = Builder(soc, output_dir="build/" + board_name,
                compile_software=True, compile_gateware=False,
                csr_json=os.path.join(build_dir, "csr.json"))
        if board_name == "camlink_4k": # FIXME
            builder.build("/usr/local/diamond/3.10_x64/bin/lin64")
        else:
            builder.build()

        soc.generate_dts(board_name)
        soc.compile_dts(board_name)
        soc.compile_emulator(board_name)

        if args.fbi:
            os.system("python3 -m litex.soc.software.mkmscimg buildroot/Image -o buildroot/Image.fbi --fbi --little")
            os.system("python3 -m litex.soc.software.mkmscimg buildroot/rootfs.cpio -o buildroot/rootfs.cpio.fbi --fbi --little")
            os.system("python3 -m litex.soc.software.mkmscimg buildroot/rv32.dtb -o buildroot/rv32.dtb.fbi --fbi --little")
            os.system("python3 -m litex.soc.software.mkmscimg emulator/emulator.bin -o emulator/emulator.bin.fbi --fbi --little")

        if args.load:
            board.load()

        if args.flash:
            board.flash()

if __name__ == "__main__":
    main()
