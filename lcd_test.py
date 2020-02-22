# Small example fading the red led on the board up and down using PWM

from migen import *
#from migen.build.platforms import icebreaker
from litex_boards.platforms import hadbadge
import lcd as hadlcd
from litex.soc.cores.clock import ECP5PLL

import os

from gen import Generator

class PWMFade(Module):
    def __init__(self, clk, lcd_pins, kaypad, sim=False):
        # Add extra clocks needed by the USB system
        self.clock_domains.cd_sys = ClockDomain()
        
        from litevideo.terminal.core import Terminal
        from stream_gen import StreamGenerator

        # Note this pll is actually driven by the main sys_clk PLL
        # It should probably be run from clk8, but it's difficult to ge access to that pin.
        if sim:
            self.comb += self.cd_sys.clk.eq(clk)
        else:    
            self.submodules.pix_pll = pix_pll = ECP5PLL()
            pix_pll.register_clkin(clk, 8e6)
            #pix_pll.create_clkout(self.cd_pix_s, 12e6, phase=1)
            pix_pll.create_clkout(self.cd_sys, 48e6)
        
        self.submodules.lcd = lcd = hadlcd.LCD(lcd_pins, sim)
        
        # VGA clock domain
        self.clock_domains.cd_vga = ClockDomain()
        self.comb += self.cd_vga.clk.eq(ClockSignal())

        # Create VGA terminal
        #mem_map["terminal"] = 0x30000000
        self.submodules.terminal = terminal = Terminal()
        #self.add_wb_slave(mem_decoder(0x30000000), self.terminal.bus)
        #self.add_memory_region("terminal", 0x30000000, 0x10000)

        self.submodules.generator = generator = Generator()

        self.submodules.streamgen = sg = StreamGenerator()

        # Connect VGA pins
        self.comb += [
            lcd.vsync.eq(~terminal.vsync),
            lcd.hsync.eq(~terminal.hsync),
            lcd.r.eq(terminal.red),
            lcd.g.eq(terminal.green),
            lcd.b.eq(terminal.blue),

            generator.bus.connect(terminal.bus),

            sg.source.connect(generator.sink)
        ]

def add_fsm_state_names():
    """Hack the FSM module to add state names to the output"""
    from migen.fhdl.visit import NodeTransformer
    from migen.genlib.fsm import NextState, NextValue, _target_eq
    from migen.fhdl.bitcontainer import value_bits_sign

    class My_LowerNext(NodeTransformer):
        def __init__(self, next_state_signal, next_state_name_signal, encoding, aliases):
            self.next_state_signal = next_state_signal
            self.next_state_name_signal = next_state_name_signal
            self.encoding = encoding
            self.aliases = aliases
            # (target, next_value_ce, next_value)
            self.registers = []

        def _get_register_control(self, target):
            for x in self.registers:
                if _target_eq(target, x[0]):
                    return x[1], x[2]
            raise KeyError

        def visit_unknown(self, node):
            if isinstance(node, NextState):
                try:
                    actual_state = self.aliases[node.state]
                except KeyError:
                    actual_state = node.state
                return [
                    self.next_state_signal.eq(self.encoding[actual_state]),
                    self.next_state_name_signal.eq(int.from_bytes(actual_state.encode(), byteorder="big"))
                ]
            elif isinstance(node, NextValue):
                try:
                    next_value_ce, next_value = self._get_register_control(node.target)
                except KeyError:
                    related = node.target if isinstance(node.target, Signal) else None
                    next_value = Signal(bits_sign=value_bits_sign(node.target), related=related)
                    next_value_ce = Signal(related=related)
                    self.registers.append((node.target, next_value_ce, next_value))
                return next_value.eq(node.value), next_value_ce.eq(1)
            else:
                return node
    import migen.genlib.fsm as fsm
    def my_lower_controls(self):
        self.state_name = Signal(len(max(self.encoding,key=len))*8, reset=int.from_bytes(self.reset_state.encode(), byteorder="big"))
        self.next_state_name = Signal(len(max(self.encoding,key=len))*8, reset=int.from_bytes(self.reset_state.encode(), byteorder="big"))
        self.comb += self.next_state_name.eq(self.state_name)
        self.sync += self.state_name.eq(self.next_state_name)
        return My_LowerNext(self.next_state, self.next_state_name, self.encoding, self.state_aliases)
    fsm.FSM._lower_controls = my_lower_controls    

def _test(dut):
    for i in range(1000):
        yield

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 1:
        if sys.argv[1] == "sim":
            
            plat = hadbadge.Platform()
            clk = plat.request("clk8")
            lcd_pins = plat.request("lcd")
            keypad = plat.request("keypad")
            dut = PWMFade(clk, lcd_pins, keypad,sim=True)

            add_fsm_state_names()
            
            plat.build(dut, build_dir='build_lcd', run=False)

            os.system('iverilog build_lcd/tb.v build_lcd/top.v -o build_lcd/a.out')
            cwd = os.getcwd()
            os.chdir('build_lcd')

            os.system('vvp a.out')

            os.chdir(cwd)
            
            #dut.clock_domains.cd_sys = ClockDomain("sys")
            #run_simulation(dut, _test(dut), vcd_name="pwm_fade.vcd")
    else:
        plat = hadbadge.Platform()
        clk = plat.request("clk8")
        lcd_pins = plat.request("lcd")
        keypad = plat.request("keypad")

        pwm_fade = PWMFade(clk, lcd_pins, keypad)
        plat.build(pwm_fade, build_dir='build_lcd')
        os.system(f'ecppack build_lcd/top.config --compress --spimode qspi --freq 38.8 --bit build_lcd/top.bit')
        os.system("dfu-util -d 1d50:614b --alt 2 --download build_lcd/top.bit -R")
        #plat.create_programmer().flash(0, 'build/top.bin')
