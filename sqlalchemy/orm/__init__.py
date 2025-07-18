class relationship:
    def __init__(self, *args, **kwargs):
        pass

class MappedMeta(type):
    def __getitem__(cls, item):
        return cls

class Mapped(metaclass=MappedMeta):
    pass

def mapped_column(*args, **kwargs):
    return None

class DeclarativeBase:
    pass

class sessionmaker:
    def __init__(self, *a, **k):
        pass
