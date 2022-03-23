from hwtypes import BitVector
from mantle2 import Decoder
import fault as f


def test_decode_simple():
    n = 8
    tester = f.Tester(Decoder(n))
    tester.circuit.I = I = BitVector.random(n)
    tester.eval()
    tester.circuit.O.expect(BitVector[2**n](1) << BitVector[2**n](int(I)))
    tester.compile_and_run("verilator")
