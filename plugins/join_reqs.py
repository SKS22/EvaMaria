from logging import getLogger
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
import asyncio

from info import REQ_CHANNEL
# adjust import to match how JoinReqs is defined in your repo:
# try from database.join_reqs import JoinReqs or from database import JoinReqs
from database import JoinReqs

logger = getLogger(name)
db_class = JoinReqs  # either a class or an instance depending on your code

@Client.on_chat_join_request(filters.chat(REQ_CHANNEL))
async def join_reqs(bot: Client, join_req: ChatJoinRequest):
    # create instance if JoinReqs is a class
    req_db = db_class() if callable(db_class) else db_class

    # support both sync and async isActive()
    is_active = False
    if hasattr(req_db, "isActive"):
        if asyncio.iscoroutinefunction(req_db.isActive):
            is_active = await req_db.isActive()
        else:
            is_active = req_db.isActive()

    if not is_active:
        logger.debug("JoinReqs tracking not active; ignoring join request.")
        return

    user = join_req.from_user
    payload = {
        "user_id": user.id,
        "first_name": user.first_name,
        "username": getattr(user, "username", None),
        "date": join_req.date
    }

    add_user = getattr(req_db, "add_user", None)
    if add_user is None:
        logger.error("JoinReqs has no add_user method; please check import.")
        return

    if asyncio.iscoroutinefunction(add_user):
        await add_user(**payload)
    else:
        add_user(**payload)

    logger.info("Logged join request for user %s", user.id)
