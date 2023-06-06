import motor.motor_asyncio as mongo
from .models import *
import secrets


class _Storage:

    def __init__(self):
        self.__client = mongo.AsyncIOMotorClient(
            'mongodb://Ybu7yNneQNKY7fXnc5nL262z1dE:f4-NO_WtpyZOFejOu8_xwWRiZo0@77.232.137.229:27017/')
        self.__db: mongo.AsyncIOMotorDatabase = self.__client.get_database('HouseMapDb')

    async def __check_conn(self):
        try:
            await self.__client.server_info()
        except:
            self.__init__()

    async def create_map(self, map_id: str, filename: str) -> Map:
        await self.__check_conn()
        map = Map(id=map_id, filename=filename)

        await self.__db.maps.insert_one(map.get_payload())

        return map

    async def get_map(self, map_id: str) -> Map:
        await self.__check_conn()
        res = await self.__db.maps.find_one({'id': map_id})

        return Map(**res) if res else None
    
    async def get_maps(self) -> list[Map]:
        await self.__check_conn()
        res = []

        async for m in self.__db.maps.find({}):
            res.append(Map(**m))

        return res

    async def create_point(self, point_id: str, map_id: str, name: str, pos_x: float, pos_y: float, color: str, filenames: list[str]) -> Point:
        await self.__check_conn()
        point = Point(id=point_id, map_id=map_id, name=name, pos_x=pos_x,
                      pos_y=pos_y, color=color, filenames=filenames)

        await self.__db.points.insert_one(point.get_payload())

        return point

    async def get_point(self, map_id: str, point_id: str) -> Point:
        await self.__check_conn()
        res = await self.__db.points.find_one({'map_id': map_id, 'point_id': point_id})

        return Point(**res) if res else None

    async def get_points(self, map_id: str) -> list[Point]:
        await self.__check_conn()
        res = []

        async for p in self.__db.points.find({'map_id': map_id}):
            res.append(Point(**p))

        return res
