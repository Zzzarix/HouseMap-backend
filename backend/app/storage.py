import motor.motor_asyncio as mongo
from .models import *

_client = mongo.AsyncIOMotorClient('mongodb://root:root@housemap-db:13450')
_db: mongo.AsyncIOMotorDatabase = _client.get_database('HouseMapDb')


class Storage:

    @classmethod
    async def create_map(cls, map_id: str, filename: str) -> Map:
        map = Map(id=map_id, filename=filename)

        await _db.maps.insert_one(map.get_payload())

        return map

    @classmethod
    async def get_map(cls, map_id: str) -> Map:
        res = await _db.maps.find_one({'id': map_id})

        return Map(**res)

    @classmethod
    async def create_point(cls, point_id: str, name: str, pos_x: float, pos_y: float, color: str, filenames: list[str]) -> Point:
        point = Point(point_id=point_id, name=name, pos_x=pos_x,
                      pos_y=pos_y, color=color, filenames=filenames)

        await _db.points.insert_one(point.get_payload())

        return point

    @classmethod
    async def get_points(cls, map_id: str) -> list[Point]:
        res = []

        async for p in _db.points.find({'map_id': map_id}):
            res.append(Point(**p))

        return res
