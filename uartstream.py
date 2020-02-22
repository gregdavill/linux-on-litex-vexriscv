
from enum import IntEnum

from migen import *
from migen.genlib import fsm
from migen.genlib import fifo
from migen.genlib import cdc
from migen.fhdl.decorators import ModuleTransformer

from litex.soc.integration.doc import AutoDoc, ModuleDoc
from litex.soc.interconnect import stream
from litex.soc.interconnect import csr_eventmanager as ev



from litex.soc.interconnect.csr import CSRStorage, CSRStatus, CSRField, CSR, AutoCSR


from litex.soc.interconnect.csr_eventmanager import *
from litex.soc.interconnect import stream


class UARTStream(Module, AutoDoc, ModuleDoc, AutoCSR):
    """DummyUSB Self-Enumerating USB Controller

    This implements a device that simply responds to the most common SETUP packets.
    It is intended to be used alongside the Wishbone debug bridge.
    """

    def __init__(self):
        

        # create interface for UART
        self._rxtx = CSR(8)
        self._txfull = CSRStatus()
        self._rxempty = CSRStatus()

        self.submodules.ev = EventManager()
        self.ev.tx = EventSourceProcess()
        self.ev.rx = EventSourceProcess()
        self.ev.finalize()

        self._tuning_word = CSRStorage(32, reset=0)
        
        self._configured = CSR()

        self.sink   = stream.Endpoint([("data", 8)])
        self.source = stream.Endpoint([("data", 8)])

        # TX
        tx_fifo = ClockDomainsRenamer({"write":"sys","read":"pix"})(stream.AsyncFIFO([("data", 8)], 4, buffered=False))
        self.submodules += tx_fifo

        self.comb += [
            tx_fifo.sink.valid.eq(self._rxtx.re),
            tx_fifo.sink.data.eq(self._rxtx.r),
            self._txfull.status.eq(~tx_fifo.sink.ready),
            tx_fifo.source.connect(self.source),
            # Generate TX IRQ when tx_fifo becomes non-full
            self.ev.tx.trigger.eq(~tx_fifo.sink.ready)
        ]

        # RX
        rx_fifo = ClockDomainsRenamer({"write":"pix","read":"sys"})(stream.AsyncFIFO([("data", 8)], 4, buffered=False))
        self.submodules += rx_fifo

        self.comb += [
            self.sink.connect(rx_fifo.sink),
            self._rxempty.status.eq(~rx_fifo.source.valid),
            self._rxtx.w.eq(rx_fifo.source.data),
            rx_fifo.source.ready.eq(self.ev.rx.clear | (False & self._rxtx.we)),
            # Generate RX IRQ when tx_fifo becomes non-empty
            self.ev.rx.trigger.eq(~rx_fifo.source.valid)
        ]
