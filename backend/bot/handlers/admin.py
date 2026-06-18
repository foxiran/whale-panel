from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from backend.bot.config.db_conf import ADMIN_ID
from backend.bot.keyboards.admin_keys import (
    main_menu,
    show_panel_selection,
    cancel_button,
)
from backend.db import crud
from backend.db.engin import sessionLocal

r = Router()
# r.message.middleware(AdminMiddleware([ADMIN_ID]))


class AdminState(StatesGroup):
    set_price = State()
    set_request_price = State()


@r.callback_query(F.data == "admin:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text="❌ عملیات لغو شد.", reply_markup=main_menu())
    await state.clear()
    return


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


@r.callback_query(F.data == "admin:set_price")
async def set_price(callback: CallbackQuery, state: FSMContext):
    db = sessionLocal()
    setting = crud.get_all_settings(db)
    try:
        text = f"💰 قیمت فروش هر گیگ برای نمایندگی را وارد کنید:(به تومان)\nقیمت فعلی: {setting.price_per_gb}"
        await callback.message.answer(text=text, reply_markup=cancel_button())
        await state.set_state(AdminState.set_price)
    except Exception as e:
        await callback.message.answer(text=f"❌ خطا هنگام تنظیم قیمت: \n{e}")
    return


@r.message(AdminState.set_price)
async def set_price_message(message: Message, state: FSMContext):
    try:
        db = sessionLocal()
        price = message.text
        if not price.isdigit():
            await message.answer(text="❌ قیمت باید یک عدد باشد.")
            return
        crud.change_setting_price(db, int(price))
        await message.answer(
            text=f"✅ قیمت فروش هر گیگ برای نمایندگی با موفقیت تنظیم شد، حالا قیمت درخواست برای نمایندگی را وارد کنید: (به تومان)",
            reply_markup=cancel_button(),
        )
        await state.set_state(AdminState.set_request_price)
    except Exception as e:
        await message.answer(text=f"❌ خطا هنگام تنظیم قیمت: \n{e}")
    return


@r.message(AdminState.set_request_price)
async def set_request_price_message(message: Message, state: FSMContext):
    try:
        db = sessionLocal()
        price = message.text
        if not price.isdigit():
            await message.answer(text="❌ قیمت باید یک عدد باشد.")
            return
        crud.change_setting_request_price(db, int(price))
        await message.answer(
            text="✅ قیمت درخواست برای نمایندگی با موفقیت تنظیم شد.",
            reply_markup=main_menu(),
        )
        await state.clear()

    except Exception as e:
        await message.answer(text=f"❌ خطا هنگام تنظیم قیمت درخواست: \n{e}")
    return
