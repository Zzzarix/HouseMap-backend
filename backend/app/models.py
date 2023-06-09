class _Object:

    _fields = ...

    def get_payload(self) -> dict:
        payload = {}
        for f in self._fields:
            payload[f] = getattr(self, f)

        return payload


class Map(_Object):

    _fields = ['id', 'name', 'filename']

    id: str
    name: str
    filename: str

    def __init__(self, id: str, name: str, filename: str, **kwargs) -> None:
        self.id = id
        self.name = name
        self.filename = filename


class Point(_Object):

    _fields = ['id', 'map_id', 'filenames', 'pos_x', 'pos_y', 'name', 'color']

    id: str
    map_id: str
    filenames: list[str]
    pos_x: float
    pos_y: float
    name: str
    color: str

    def __init__(self, id: str, map_id: str, filenames: list[str], pos_x: float, pos_y: float, name: str, color: str, **kwargs) -> None:
        self.id = id
        self.map_id = map_id
        self.filenames = filenames
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.name = name
        self.color = color
