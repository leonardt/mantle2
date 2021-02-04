import magma as m
from mantle2.queue import Queue
import fault as f


def test_queue():
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
