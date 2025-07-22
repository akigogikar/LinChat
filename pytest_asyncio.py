import asyncio
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    if pyfuncitem.get_closest_marker("asyncio"):
        func = pyfuncitem.obj
        asyncio.run(func(**pyfuncitem.funcargs))
        return True
