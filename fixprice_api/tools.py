class AwaitableDict(dict):
    def __await__(self):
        async def _wrap():
            return dict(self)

        return _wrap().__await__()
