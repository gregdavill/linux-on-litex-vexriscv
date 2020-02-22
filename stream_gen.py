
from migen import *

from litex.soc.interconnect import wishbone
from litex.soc.interconnect import stream



class StreamGenerator(Module):
    def __init__(self, start):
        # Wishbone interface
        self.source = source = stream.Endpoint([('data',8)])

        self.submodules.fsm = fsm = FSM()
        

        counter = Signal(32)
        idx = Signal(16)

        counter_done = Signal()
        counter_ce = Signal()
        counter_val = Signal(32)

        self.sync += [
            If(counter_ce,
                counter.eq(counter_val)
            ).Elif(counter > 0,
                counter.eq(counter - 1)
            )
        ]

        self.comb += [
            counter_done.eq(counter == 0)
        ]

        char = Signal(8, reset=0x40)
        idx = Signal(32)


        data_to_send = bytearray("root\n", encoding='ASCII')

        #display init data 
        
        out_buffer = self.specials.out_buffer = Memory(8, len(data_to_send), init=data_to_send)
        self.specials.out_buffer_rd = out_buffer_rd = out_buffer.get_port(write_capable=False)
        self.autocsr_exclude = ['out_buffer']

        self.comb += [
            out_buffer_rd.adr.eq(idx),
        ]

        start_reg = Signal()

        fsm.act('INIT',
            #counter_val.eq(50),
            
            NextValue(idx,0),
            If(start & ~start_reg,
                NextState('ADD_CHAR')
            ),
            NextValue(start_reg, start)

            
        )


        fsm.act('ADD_CHAR',
            If(counter_done,
                source.data.eq(out_buffer_rd.dat_r),
                source.valid.eq(1),
                If(source.ready,
                    #source.valid.eq(0),
                    counter_val.eq(20),
                    counter_ce.eq(1),
                    NextValue(idx,idx+1),
                    If(idx > (len(data_to_send)-1),
                        NextState('INIT')
                    )
                ),
            )
        )
