from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from backend.bot.config.db_conf import ADMIN_ID
from backend.bot.keyboards.admin_keys import main_menu, show_panel_selection
from backend.db import crud
from backend.db.engin import sessionLocal

r = Router()
# r.message.middleware(AdminMiddleware([ADMIN_ID]))


@r.callback_query(F.data == "admin:select_panel_for_sale")
async def select_panel(
    callback: CallbackQuery,
):
    db = sessionLocal()
    panels = crud.get_all_panels(db)
    if not panels:
        await callback.message.answer(
            text="هیچ پنلی برای فروش وجود ندارد. لطفا ابتدا پنل‌ها را اضافه کنید.",
        )
        return

    await callback.message.answer(
        text="لطفا فقط یک پنل مورد نظر خود را برای فروش نمایندپی روی آن انتخاب کنید.",
        reply_markup=show_panel_selection(panels),
    )


@r.callback_query(F.data.startswith("admin:panel_selected:"))
async def panel_selected(
    callback: CallbackQuery,
):
    panel_id = int(callback.data.split(":")[-1])
    db = sessionLocal()
    try:
        update_panel = crud.change_panel_bot_status(db, panel_id)
        await callback.message.delete()
        await callback.message.answer(
            text="✅ پنل انتخابی شما با موفقیت در وضعیت فروش نمایندگی قرار گرفت.",
            reply_markup=main_menu(),
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(text=f"❌ خطا هنگام انتخاب پنل: \n{e}")
