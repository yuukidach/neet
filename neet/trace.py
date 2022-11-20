import functools

__all__ = ["Value", "make_traceable", "is_traceable", "Tracer"]


class Value:
    def __init__(self, data=None, name=None, op=None, args=None, kwargs=None):
        self.name = name
        self.op = op
        self.inputs = []
        self._cached_data = data

        self._collate(args, kwargs)

    def _collate(self, args, kwargs):
        """Collate the inputs into a list of Value objects."""
        inputs = []
        args = args or []
        kwargs = kwargs or {}

        for arg in args:
            if isinstance(arg, type(self)):
                inputs.append(arg)
            else:
                inputs.append(
                    self.make_constant(arg, name=arg.__class__.__name__)
                )

        for k, v in kwargs.items():
            if isinstance(v, type(self)):
                inputs.append(v)
            else:
                inputs.append(self.make_constant(v, name=k))

        self.inputs.extend(inputs)

    @property
    def data(self):
        return self.realize_cached_data()

    def detach(self):
        return self.make_constant(self.realize_cached_data(), self.name)

    @classmethod
    def make_constant(cls, data, name):
        value = cls(data, name)
        return value

    def realize_cached_data(self):
        if self._cached_data is not None:
            return self._cached_data
        self._cached_data = self.compute(*[i.data for i in self.inputs])
        return self._cached_data

    def compute(self, *inputs):
        return self.op(*inputs)


def make_traceable(obj):
    """Make a class or function traceable."""
    obj.__is_traceable__ = True

    @functools.wraps(obj)
    def wrapper(*args, **kwargs):
        if under_trace():
            return Value(
                data=None,
                name=obj.__name__,
                op=obj,
                args=args,
                kwargs=kwargs,
            )
        else:
            return obj(*args, **kwargs)

    return wrapper


def is_traceable(obj):
    return getattr(obj, "__is_traceable__", False)


def under_trace():
    return Tracer._cur is not None


class Tracer:
    _cur = None

    def __init__(self, imperative=False):
        self._pre = None
        self._imperative = imperative

    def __enter__(self):
        self._pre = Tracer._cur
        Tracer._cur = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Tracer._cur = self._pre
