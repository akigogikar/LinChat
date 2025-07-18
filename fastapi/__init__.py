import inspect
import asyncio

class HTTPException(Exception):
    def __init__(self, status_code: int, detail=None):
        self.status_code = status_code
        self.detail = detail

class Depends:
    def __init__(self, dependency):
        self.dependency = dependency

class UploadFile:
    def __init__(self, filename: str, file):
        self.filename = filename
        self.file = file
    async def read(self):
        return self.file.read()

class File:
    def __init__(self, default):
        self.default = default

class Form:
    def __init__(self, default):
        self.default = default

class FastAPI:
    def __init__(self):
        self.routes = {}
        self.dependency_overrides = {}
    def route(self, path, method):
        def decorator(fn):
            self.routes[(method, path)] = fn
            return fn
        return decorator
    def get(self, path, **kwargs):
        return self.route(path, 'GET')
    def post(self, path, **kwargs):
        return self.route(path, 'POST')
    def include_router(self, router, prefix='', tags=None):
        pass
    def on_event(self, event):
        def decorator(fn):
            return fn
        return decorator

class HTTPBasic:
    pass

class HTTPBasicCredentials:
    def __init__(self, username: str = '', password: str = ''):
        self.username = username
        self.password = password
