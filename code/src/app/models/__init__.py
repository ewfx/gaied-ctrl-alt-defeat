from pymongo import ASCENDING, IndexModel

from .request_types import RequestTypeModel


async def create_indexes():
    await RequestTypeModel.collection.create_indexes([IndexModel([("name", ASCENDING)], unique=True)])