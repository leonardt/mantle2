import fault
import magma as m
from mantle2.counter import Counter


def test_counter_to():
    tester = fault.SynchronousTester(Counter(6))
    for j in range(2):
        for i in range(6):
            tester.circuit.O.expect(i)
            tester.advance_cycle()
    tester.compile_and_run("verilator")


def test_counter_to_cout():
    tester = fault.SynchronousTester(Counter(6, has_cout=True))
    for j in range(2):
        for i in range(6):
            tester.circuit.O.expect(i)
            tester.circuit.COUT.expect(i == 5)
            tester.advance_cycle()
    tester.compile_and_run("verilator")


def test_counter_to_enable():
    tester = fault.SynchronousTester(Counter(6, has_enable=True))
    for i in range(3):
        tester.circuit.O.expect(0)
        tester.advance_cycle()
    tester.circuit.CE = 1
    for i in range(3):
        tester.circuit.O.expect(i)
        tester.advance_cycle()
    tester.compile_and_run("verilator")


def test_counter_to_resetn():
    tester = fault.SynchronousTester(Counter(6, reset_type=m.ResetN))
    tester.circuit.RESETN = 1
    for i in range(3):
        tester.circuit.O.expect(i)
        tester.advance_cycle()
    tester.circuit.RESETN = 0
    tester.advance_cycle()
    tester.circuit.RESETN = 1
    for i in range(3):
        tester.circuit.O.expect(i)
        tester.advance_cycle()
    tester.compile_and_run("verilator")
