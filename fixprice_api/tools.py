
class AwaitableDict(dict):
    def __init__(self, data: dict | None):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __await__(self):
        async def _wrap():
            return self._data
        return _wrap().__await__()
