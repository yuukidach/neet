import functools

__all__ = ["Value", "make_traceable"]


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
                inputs.append(self.make_constant(arg))

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
    @functools.wraps(obj)
    def wrapper(*args, **kwargs):
        return Value(
            data=None,
            name=obj.__name__,
            op=obj,
            args=args,
            kwargs=kwargs,
        )

    return wrapper
