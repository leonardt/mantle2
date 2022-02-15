from hwtypes import BitVector
from mantle2.decoder import Decoder
import fault as f


def test_decode_simple():
    tester = f.Tester(Decoder(8))
    tester.circuit.I = I = BitVector.random(8)
    tester.eval()
    tester.circuit.O.expect(BitVector[2**8](1) << BitVector[2**8](int(I)))
    tester.compile_and_run("verilator")
