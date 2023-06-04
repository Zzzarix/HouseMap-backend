import motor.motor_asyncio as mongo
from .models import *
import secrets


class Storage:

    def init(cls):
        _client = mongo.AsyncIOMotorClient('mongodb://Ybu7yNneQNKY7fXnc5nL262z1dE:f4-NO_WtpyZOFejOu8_xwWRiZo0@77.232.137.229:27017/')
        cls.__db: mongo.AsyncIOMotorDatabase = _client.get_database('HouseMapDb')


    @classmethod
    async def create_map(cls, map_id: str, filename: str) -> Map:
        map = Map(id=map_id, filename=filename)

        await cls.__db.maps.insert_one(map.get_payload())

        return map

    @classmethod
    async def get_map(cls, map_id: str) -> Map:
        res = await cls.__db.maps.find_one({'id': map_id})

        return Map(**res) if res else None

    @classmethod
    async def create_point(cls, point_id: str, name: str, pos_x: float, pos_y: float, color: str, filenames: list[str]) -> Point:
        point = Point(point_id=point_id, name=name, pos_x=pos_x,
                      pos_y=pos_y, color=color, filenames=filenames)

        await cls.__db.points.insert_one(point.get_payload())

        return point

    @classmethod
    async def get_points(cls, map_id: str) -> list[Point]:
        res = []

        async for p in cls.__db.points.find({'map_id': map_id}):
            res.append(Point(**p))

        return res
