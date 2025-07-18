class HTMLResponse(str):
    pass

class FileResponse(str):
    def __new__(cls, path):
        return str.__new__(cls, path)
