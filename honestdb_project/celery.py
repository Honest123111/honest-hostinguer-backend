# This file is a placeholder for compatibility
# Original Celery functionality has been removed for Firebase App Hosting compatibility

class DummyCeleryApp:
    def __init__(self):
        self.name = "honestdb_project"
    
    def task(self, *args, **kwargs):
        # Return a dummy decorator that does nothing
        def decorator(func):
            return func
        return decorator
    
    def autodiscover_tasks(self, *args, **kwargs):
        pass

app = DummyCeleryApp()
