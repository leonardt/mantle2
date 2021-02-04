from typing import Optional
import magma as m

from mantle2.util import ispow2


class CounterTo(m.Generator2):
    """
    Counts to a specific number `n`
    """
    def __init__(self, n: int, has_enable: bool = False,
                 has_cout: bool = False, reset_type: Optional[m.Type] = None):
        num_bits = max(n.bit_length(), 1)

        self.io = m.IO(O=m.Out(m.UInt[num_bits]))
        if has_cout:
            self.io += m.IO(COUT=m.Out(m.Bit))
        self.io += m.clock_io.gen_clock_io(reset_type, has_enable)

        reg = m.Register(m.UInt[num_bits], has_enable=has_enable,
                         reset_type=reset_type)()
        if has_enable:
            reg.CE @= self.io.CE
        self.io.O @= reg.O
        if has_cout:
            # Maybe we can skip the cin input?
            # https://github.com/leonardt/hwtypes/issues/143
            I, COUT = reg.O.adc(1, 0)
            self.io.COUT @= COUT
        else:
            I = reg.O + 1
        if not ispow2(n):
            I = m.mux([I, 0], reg.O == n)
        reg.I @= I
