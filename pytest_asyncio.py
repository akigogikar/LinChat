import asyncio
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    if pyfuncitem.get_closest_marker("asyncio"):
        func = pyfuncitem.obj
        asyncio.get_event_loop().run_until_complete(func(**pyfuncitem.funcargs))
        return True
