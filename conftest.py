import pytest
import magma


@pytest.fixture(autouse=True)
def magma_test():
    magma.frontend.coreir_.ResetCoreIR()
