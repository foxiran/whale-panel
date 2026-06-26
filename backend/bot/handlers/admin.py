from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from backend.bot.middlewares.admin import AdminMiddleware
from backend.bot.config.db_conf import ADMIN_ID
from backend.bot.keyboards.admin_keys import (
    main_menu,
    show_panel_selection,
    cancel_button,
    settings_menu,
)
from backend.db import crud
from backend.db.engin import sessionLocal

r = Router()
r.message.middleware(AdminMiddleware())
r.callback_query.middleware(AdminMiddleware())


class AdminState(StatesGroup):
    set_price = State()
    set_request_price = State()
    set_start_message = State()
    set_help_message = State()


class RegisterAdminState(StatesGroup):
    username = State()
    password = State()


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
        text = f"💰 قیمت فروش هر گیگ برای نمایندگی را وارد کنید:(به تومان)\nقیمت فعلی: {setting.price_per_gb:,.0f}"
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


@r.callback_query(F.data == "admin:settings")
async def settings(callback: CallbackQuery):
    await callback.message.answer(text="🔄 تنظیمات عمومی", reply_markup=settings_menu())
    return


@r.callback_query(F.data == "admin:set_start_message")
async def set_start_message(callback: CallbackQuery, state: FSMContext):
    db = sessionLocal()
    current_message = crud.get_all_settings(db).start_message
    await callback.message.answer(
        text=f"🔄 پیام آغاز فعلی:\n{current_message}", reply_markup=cancel_button()
    )
    await state.set_state(AdminState.set_start_message)
    return


@r.message(AdminState.set_start_message)
async def set_start_message_message(message: Message, state: FSMContext):
    try:
        db = sessionLocal()

        text = message.text

        updated = crud.change_setting_start_message(db, text)

        if not updated:
            await message.answer("❌ خطا هنگام ذخیره پیام.")
            return

        await message.answer(
            "✅ پیام آغاز با موفقیت تنظیم شد.",
            reply_markup=main_menu(),
        )
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ {e}")


@r.callback_query(F.data == "admin:set_help_message")
async def set_help_message(callback: CallbackQuery, state: FSMContext):
    db = sessionLocal()
    current_message = crud.get_all_settings(db).help_message
    await callback.message.answer(
        text=f"🔄 پیام راهنمای فعلی:\n{current_message}", reply_markup=cancel_button()
    )
    await state.set_state(AdminState.set_help_message)
    return


@r.message(AdminState.set_help_message)
async def set_help_message_message(message: Message, state: FSMContext):
    try:
        db = sessionLocal()

        text = message.text

        updated = crud.change_setting_help_message(db, text)

        if not updated:
            await message.answer("❌ خطا هنگام ذخیره پیام.")
            return

        await message.answer(
            "✅ پیام راهنما با موفقیت تنظیم شد.",
            reply_markup=main_menu(),
        )

        await state.clear()

    except Exception as e:
        await message.answer(f"❌ {e}")


@r.callback_query(F.data == "admin:info")
async def bot_info(callback: CallbackQuery):
    db = sessionLocal()
    users, admins, settings = crud.get_info_for_bot(db)
    text = (
        f"👥 تعداد کل کاربران ربات: {len(users)}\n"
        f"👨‍💻 تعداد کل نمایندگان: {len(admins)}\n"
        f"💵 قیمت هرگیگ برای نماینگان: {settings.price_per_gb:,.0f}تومان\n"
        f"⭐ قیمت درخواست و استارت نمایندگی: {settings.start_price:,.0f}تومان\n"
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=main_menu())


@r.callback_query(F.data.startswith("admin:accept_register:"))
async def accept_register(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split(":")[-1])

    await state.update_data(chat_id=chat_id)

    await callback.message.answer(
        "👤 نام کاربری ورود به پنل را برای این نماینده وارد کنید:"
    )

    await state.set_state(RegisterAdminState.username)

    await callback.answer()


@r.message(RegisterAdminState.username)
async def get_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())

    await message.answer("🔑 رمز عبور ورود به پنل را وارد کنید:")

    await state.set_state(RegisterAdminState.password)


@r.message(RegisterAdminState.password)
async def get_password(message: Message, state: FSMContext):
    from backend.schema._input import AdminInput

    db = sessionLocal()

    data = await state.get_data()

    chat_id = data["chat_id"]
    username = data["username"]
    password = message.text.strip()

    user = crud.get_user(db, chat_id)

    if not user:
        await message.answer("❌ کاربر پیدا نشد.")
        await state.clear()
        return

    try:
        _panel = crud.get_for_bot_panel(db)
        _admin = AdminInput(
            username=username,
            password=password,
            panel=_panel.name,
            marzban_password=password,
            traffic=0,
        )

        admin = crud.add_admin(db=db, admin_input=_admin)

        crud.make_user_reseller(
            db=db,
            user=user,
            admin=admin,
        )

    except Exception as e:
        await message.answer(f"error: {e}")

    await message.bot.send_message(
        chat_id=user.chat_id,
        text=(
            "🎉 درخواست نمایندگی شما تایید شد.\n\n"
            "اطلاعات ورود به پنل:\n\n"
            f"👤 نام کاربری: <code>{username}</code>\n"
            f"🔑 رمز عبور: <code>{password}</code>"
        ),
        parse_mode="HTML",
    )

    await message.answer(
        "✅ نماینده با موفقیت ایجاد و اطلاعات ورود به پنل ارسال شد، حالا نیازه یکبار از طریق داشبورد مدیریت یکبار ادمین ایجاد شده را ادیت و درصورت لزوم اینباند های مخصوصش رو ادیت کنید!."
    )

    await state.clear()


@r.callback_query(F.data.startswith("admin:reject_register:"))
async def reject_register(callback: CallbackQuery):
    chat_id = int(callback.data.split(":")[-1])

    await callback.bot.send_message(
        chat_id, "❌ درخواست نمایندگی شما توسط مدیریت رد شد."
    )

    await callback.message.edit_reply_markup()

    await callback.answer("درخواست رد شد.")


@r.callback_query(F.data.startswith("admin:accept_buy:"))
async def accept_buy(callback: CallbackQuery):
    db = sessionLocal()

    _, _, chat_id, gb = callback.data.split(":")

    chat_id = int(chat_id)
    gb = int(gb)

    user = crud.get_user(db, chat_id)

    admin = user.admin

    admin.traffic += gb * 1024**3
    admin.initial_traffic += gb * 1024**3

    db.commit()

    await callback.bot.send_message(
        chat_id, f"🎉 خرید شما تایید شد.\n\n{gb} گیگ به موجودی شما اضافه شد."
    )

    await callback.message.edit_reply_markup()

    await callback.answer("تایید شد.")


@r.callback_query(F.data.startswith("admin:reject_buy:"))
async def reject_buy(callback: CallbackQuery):
    chat_id = int(callback.data.split(":")[-1])

    await callback.bot.send_message(chat_id, "❌ رسید پرداخت شما رد شد.")

    await callback.message.edit_reply_markup()

    await callback.answer("رد شد.")
