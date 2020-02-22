
from migen import *
from migen.genlib import fsm
from migen.genlib import fifo
from migen.genlib import cdc

from migen.fhdl.decorators import ModuleTransformer
from litex.soc.interconnect.csr import CSRStorage, CSRStatus, CSRField, CSR, AutoCSR



# Hack the AutoCSR objects to enable access only via Module attributes.
class CSRTransform(ModuleTransformer):
    def __init__(self, parent):
        self.parent = parent

    def transform_instance(self, i):
        # Capture all the available CSRs, then burn the bridge.
        v = i.get_csrs()
        i.get_csrs = None
        
        for c in v:
            # Skip over modules already exposed, should handle potential renaming here.
            #if hasattr(i, c.name):
            #    pass

            # Attach csr as module attribute
            setattr(i, c.name,c)

            if isinstance(c, CSR):
                ...
            else:
                # Clear the finalise function so these aren't altered further.
                # Maybe not required?
                def _null(*kwargs):
                    ...   
                c.finalize = _null

                # Attach these to our modules submodules,
                # needed to ensure the objects are elaborated?
                self.parent.submodules += c

            # create extra bindings to support dev writing
            if isinstance(c, CSRStorage):
                    # .re is used to determine when .storage has been updated.
                    # so we need to create delayed re signal, we'll rename this to re0
                    setattr(c, "re0", c.re)
                    setattr(c.re0, "name", c.name + '_re0')

                    # Our personal .re signal will then update .re0 alongside .storage
                    setattr(c, "re", Signal(name=c.name + '_re'))
                    c.sync += c.re0.eq(c.re)

                    if hasattr(c, "fields"):
                        setattr(c, "dat_w", Record([]))
                        for a in c.fields.fields:
                            s = Signal(a.size,name=f'{c.name}_{a.name}0')

                            c.sync += If(c.re, 
                                c.storage[a.offset:a.offset + a.size].eq(s)
                            )
                            setattr(c.dat_w, a.name, s)

                    else:
                        # if the CSRStorage doesn't have any fields, just provide .dat_w
                        setattr(c, "dat_w", Signal(c.size))
                        c.sync += If(c.re, c.storage.eq(c.dat_w))

            