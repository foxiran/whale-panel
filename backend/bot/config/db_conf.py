from backend.db import crud
from backend.db.engin import sessionLocal

db = sessionLocal()
tg_bot = crud.get_tgbot(db)

TOKEN = tg_bot.token if tg_bot else None
ADMIN_ID = tg_bot.admin_id if tg_bot else None
IS_ACTIVE = tg_bot.is_active if tg_bot else None
