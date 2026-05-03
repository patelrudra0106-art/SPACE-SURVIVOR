class ObjectPool:
    """A generic object pool for reusing game objects like bullets to save memory."""
    def __init__(self, factory_func, initial_size=100):
        self.factory_func = factory_func
        self.pool = [self.factory_func() for _ in range(initial_size)]

    def get(self, *args, **kwargs):
        """Retrieve an inactive object from the pool, or create a new one if full."""
        for obj in self.pool:
            if not obj.active:
                obj.spawn(*args, **kwargs)
                return obj
        
        # Pool is full, expand it
        new_obj = self.factory_func()
        new_obj.spawn(*args, **kwargs)
        self.pool.append(new_obj)
        return new_obj

    def get_active(self):
        """Return a generator yielding only active objects."""
        for obj in self.pool:
            if obj.active:
                yield obj

    def reset(self):
        """Deactivate all objects in the pool."""
        for obj in self.pool:
            if hasattr(obj, 'deactivate'):
                obj.deactivate()
            else:
                obj.active = False
