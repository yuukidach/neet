import functools
import types
import inspect

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
    def _make_fn_traceable(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if under_trace():
                return Value(
                    op=fn,
                    args=args,
                    kwargs=kwargs,
                    name=fn.__name__,
                )
            else:
                return fn(*args, **kwargs)

        wrapper.__is_traceable__ = True
        return wrapper

    def _make_cls_traceable(cls):
        setattr(cls, "__call__", _make_fn_traceable(cls.__call__))
        return cls

    if isinstance(obj, types.FunctionType):
        return _make_fn_traceable(obj)
    elif callable(obj):
        return _make_cls_traceable(obj)
    else:
        raise TypeError(f"Cannot make {obj} traceable.")


def is_traceable(obj):
    if isinstance(obj, types.FunctionType):
        return getattr(obj, "__is_traceable__", False)
    elif callable(obj):
        return getattr(obj.__call__, "__is_traceable__", False)
    else:
        return False


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
