import inspect
import asyncio
from . import UploadFile, Depends, HTTPException

class Response:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data
    def json(self):
        return self._data

class TestClient:
    def __init__(self, app):
        self.app = app

    def request(self, method, path, params=None, data=None, files=None):
        handler = self.app.routes.get((method, path))
        if not handler:
            return Response(404, {"detail": "Not Found"})
        sig = inspect.signature(handler)
        kwargs = {}
        for name, param in sig.parameters.items():
            if isinstance(param.default, Depends):
                dep_fn = self.app.dependency_overrides.get(param.default.dependency, param.default.dependency)
                val = dep_fn()
                if asyncio.iscoroutine(val):
                    val = asyncio.run(val)
                kwargs[name] = val
            elif files and name == 'file':
                file_tuple = files['file']
                kwargs[name] = UploadFile(file_tuple[0], file_tuple[1])
            elif params and name in params:
                kwargs[name] = params[name]
            elif data and name in data:
                kwargs[name] = data[name]
        result = handler(**kwargs)
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)
        status = 200
        if isinstance(result, dict):
            data = result
        else:
            data = result
        if isinstance(result, HTTPException):
            status = result.status_code
            data = {"detail": result.detail}
        return Response(status, data)

    def get(self, path, params=None):
        return self.request('GET', path, params=params)

    def post(self, path, params=None, data=None, files=None):
        return self.request('POST', path, params=params, data=data, files=files)
