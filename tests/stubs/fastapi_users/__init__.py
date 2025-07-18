class FastAPIUsers:
    def __init__(self, *a, **k):
        pass
    def get_auth_router(self, backend):
        return object()
    def get_register_router(self, read, create):
        return object()
    def get_users_router(self, read, update):
        return object()
    def current_user(self, active=True):
        return lambda: None
    def on_after_register(self, cb):
        pass
    def on_after_login(self, cb):
        pass
