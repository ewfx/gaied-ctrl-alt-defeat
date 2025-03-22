from pymongo import ASCENDING, IndexModel

from .request_types import RequestTypeModel
from .sub_request_types import SubRequestTypeModel


async def create_indexes():
    await SubRequestTypeModel.collection.create_indexes([IndexModel([("name", ASCENDING)], unique=True)])
    await RequestTypeModel.collection.create_indexes([IndexModel([("name", ASCENDING)], unique=True)])