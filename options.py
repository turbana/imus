class ObjectDict(dict):
    def __init__(self, *args, **kwargs):
        args = [self.__translate_dict(d) for d in args]
        kwargs = self.__translate_dict(kwargs)
        super(ObjectDict, self).__init__(*args, **kwargs)

    def update(self, d):
        d = self.__translate_dict(d)
        super(ObjectDict, self).update(d)

    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("No such attribute: " + name)
        return self[name]

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = ObjectDict(value)
        self[name] = value

    def __delattr__(self, name):
        if name not in self:
            raise AttributeError("No such attribute: " + name)
        del self[name]

    @staticmethod
    def __translate_dict(d):
        return {k: ObjectDict(v) if isinstance(v, dict) else v
                for k, v in d.items()}


options = ObjectDict()
