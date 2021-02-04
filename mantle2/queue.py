"""
Based on
https://github.com/chipsalliance/chisel3/blob/master/src/main/scala/chisel3/util/Decoupled.scala
(missing support for `flow` and `pipe` parameters)
"""
import magma as m
from mantle2.counter import CounterTo


def ispow2(n):
    return (n & (n - 1) == 0) and n != 0


class Queue(m.Generator2):
    def __init__(self, entries: int, T: m.Kind):
        assert entries >= 0
        self.io = m.IO(
            # Flipped since enq/deq is from perspective of the client
            enq=m.DeqIO[T],
            deq=m.EnqIO[T]
        ) + m.ClockIO()

        ram = m.Memory(entries, T)()
        enq_ptr = CounterTo(entries - 1, has_enable=True)()
        deq_ptr = CounterTo(entries - 1, has_enable=True)()
        maybe_full = m.Register(init=False, has_enable=True)()

        ptr_match = enq_ptr.O == deq_ptr.O
        empty = ptr_match & ~maybe_full.O
        full = ptr_match & maybe_full.O

        self.io.deq.valid @= ~empty
        self.io.enq.ready @= ~full

        do_enq = self.io.enq.fired()
        do_deq = self.io.deq.fired()

        ram.write(self.io.enq.data, enq_ptr.O, m.enable(do_enq))

        enq_ptr.CE @= m.enable(do_enq)
        deq_ptr.CE @= m.enable(do_deq)

        maybe_full.I @= m.enable(do_enq)
        maybe_full.CE @= m.enable(do_enq != do_deq)
        self.io.deq.data @= ram[deq_ptr.O]
