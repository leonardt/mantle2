from hwtypes import Bit, BitVector
import magma as m
from mantle2.queue import Queue
import fault as f
import pysv
from pysv.util import clear_imports


class QueueModel:
    @pysv.sv()
    def __init__(self, num_entries):
        # TODO: How can we encode the type information as a parameter?
        self.num_entries = num_entries
        self._entries = []

    @pysv.sv(value=pysv.DataType.UInt)
    def enq(self, value):
        if len(self._entries) > self.num_entries:
            raise Exception("Queue is full")
        print(f"Enq {value}")
        self._entries.append(value)

    @pysv.sv(return_type=pysv.DataType.UInt)
    def deq(self):
        if len(self._entries) == 0:
            raise Exception("Queue is empty")
        print(f"Deq {self._entries[0]}")
        return self._entries.pop(0)


def test_queue_simple():
    tester = f.SynchronousTester(Queue(4, m.Bits[2]))
    tester.advance_cycle()
    for i in range(4):
        tester.circuit.enq.data = i
        tester.circuit.enq.valid = 1
        tester.circuit.enq.ready.expect(1)
        tester.advance_cycle()
    tester.circuit.enq.valid = 0
    tester.circuit.enq.ready.expect(0)
    for i in range(4):
        tester.circuit.deq.data.expect(i)
        tester.circuit.deq.valid.expect(1)
        tester.circuit.deq.ready = 1
        tester.advance_cycle()
    tester.circuit.deq.valid.expect(0)
    tester.compile_and_run("verilator")


def test_queue_model():
    clear_imports(QueueModel)
    num_entries = 4
    tester = f.SynchronousTester(Queue(num_entries, m.UInt[32]))
    model = tester.Var("model", QueueModel)
    tester.poke(model, tester.make_call(QueueModel, num_entries))
    for i in range(10):
        enq_valid = Bit.random()
        enq_data = BitVector.random(32)
        tester.circuit.enq.data = enq_data
        tester.circuit.enq.valid = enq_valid
        if_tester = tester._if(
            tester.circuit.enq.valid & tester.circuit.enq.ready)
        if_tester.make_call_stmt(model.enq, enq_data)
        tester.advance_cycle()
        tester.circuit.enq.valid = 0

        deq_ready = Bit.random()
        tester.circuit.deq.ready = deq_ready
        if_tester = tester._if(
            tester.circuit.deq.valid & tester.circuit.deq.ready)
        var = if_tester.Var("deq_data", BitVector[32])
        if_tester.poke(var, if_tester.make_call(model.deq))
        # TODO: Expect calls function twice (second time for erorr message)
        if_tester.circuit.deq.data.expect(var)
        tester.advance_cycle()
        tester.circuit.deq.ready = 0
    tester.compile_and_run("verilator", use_pysv=True, disp_type="realtime")
