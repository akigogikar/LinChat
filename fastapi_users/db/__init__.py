class SQLAlchemyBaseUserTableMeta(type):
    def __getitem__(cls, item):
        return cls

class SQLAlchemyBaseUserTable(metaclass=SQLAlchemyBaseUserTableMeta):
    pass
