from sqlite3 import adapt
from aiogram import Router, F
from aiogram.enums import parse_mode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from backend.bot.config.db_conf import ADMIN_ID
from backend.bot.keyboards.user_keys import (
    main_users_menu,
    register_menu,
    payment_methods_register,
    payment_methods_buy,
    cancel_button,
)
from backend.db import crud
from backend.db.engin import sessionLocal

r = Router()


class RegisterState(StatesGroup):
    waiting_receipt = State()


class BuyTrafficState(StatesGroup):
    amount = State()
    receipt = State()


@r.callback_query(F.data == "user:cancel")
async def back_tomain_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text="❌ عملیات لغو شد.", reply_markup=main_users_menu()
    )
    await state.clear()
    return


@r.callback_query(F.data == "user:my_acc")
async def show_user_acc(callback: CallbackQuery):
    from backend.config.env import config

    db = sessionLocal()
    user = crud.get_user(db, callback.from_user.id)

    text = (
        "👤 <b>اطلاعات حساب کاربری</b>\n\n"
        f"🆔 آیدی تلگرام: <code>{user.chat_id}</code>\n"
        f"📛 نام: {user.name}\n"
        f"👤 یوزرنیم: @{user.username if user.username else '-'}\n"
        f"📌 وضعیت ثبت‌نام: {'✅' if user.is_registered else '❌'}\n"
        f"🤝 نماینده: {'✅' if user.is_reseller else '❌'}\n"
        f"🔵 وضعیت حساب: {'✅' if user.is_active else '❌'}\n"
    )

    if user.is_reseller and user.admin:
        admin = user.admin

        expiry = (
            admin.expiry_date.strftime("%Y-%m-%d %H:%M")
            if admin.expiry_date
            else "نامحدود"
        )

        text += (
            "\n━━━━━━━━━━━━━━\n"
            "💼 <b>اطلاعات نمایندگی</b>\n\n"
            f"👨‍💻 نام کاربری پنل: <code>{admin.username}</code>\n"
            f"🔐 پسورد پنل: <code>{admin.marzban_password}</code>\n"
            f"🌐 پنل: {config.PANEL_ADDRESS}\n"
            f"📊 ترافیک فعلی: {admin.traffic / (1024**3):.2f} GB\n"
            f"📦 ترافیک اولیه: {admin.initial_traffic / (1024**3):.2f} GB\n"
            f"📅 تاریخ انقضا: {expiry}\n"
            f"🔄 بازگشت ترافیک هنگام بروزرسانی: {'✅' if admin.update_return_traffic else '❌'}\n"
            f"🗑 بازگشت ترافیک هنگام حذف: {'✅' if admin.delete_return_traffic else '❌'}\n"
            f"⚡ وضعیت نمایندگی: {'✅' if admin.is_active else '❌'}"
        )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_users_menu(),
    )


@r.callback_query(F.data == "user:register")
async def admin_register(callback: CallbackQuery):
    db = sessionLocal()

    user = crud.get_user(db, callback.from_user.id)
    setting = crud.get_all_settings(db)

    if user.is_reseller:
        await callback.message.edit_text(
            text=(
                "❕ <b>شما هم‌اکنون نماینده مجموعه هستید.</b>\n\n"
                "برای مدیریت سرویس‌های خود از پنل نمایندگی استفاده کنید."
            ),
            parse_mode="HTML",
            reply_markup=main_users_menu(),
        )
        return

    if not setting.registration_enabled:
        await callback.message.text(
            text=(
                "❌ <b>ثبت‌نام نمایندگی موقتاً غیرفعال است.</b>\n\n"
                "پس از فعال شدن مجدداً اقدام نمایید."
            ),
            parse_mode="HTML",
            reply_markup=main_users_menu(),
        )
        return

    text = f"""
<b>🌟 ثبت درخواست نمایندگی</b>

با دریافت نمایندگی می‌توانید کاربران خود را مدیریت کرده و از پنل اختصاصی استفاده کنید.

<b>💰 شرایط نمایندگی</b>

💵 هزینه درخواست نمایندگی:
<b>{setting.start_price:,} تومان</b>


📊 قیمت هر گیگ:
<b>{setting.price_per_gb:,} تومان</b>

📦 حداقل خرید بسته:
<b>{setting.minimum_purchase_amount:,} تومان</b>

━━━━━━━━━━━━━━

<b>امکانات نمایندگی</b>

✅ پنل اختصاصی
✅ ساخت نامحدود کاربر
✅ مدیریت کاربران
✅ تمدید و حذف سرویس
✅ مشاهده مصرف کاربران
✅ پشتیبانی

━━━━━━━━━━━━━━

در صورت تمایل روی دکمه «ثبت درخواست» کلیک کنید.
"""

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=register_menu(),
    )


@r.callback_query(F.data == "user:request_for_register")
async def request_for_register(callback: CallbackQuery):
    db = sessionLocal()

    user = crud.get_user(db, callback.from_user.id)
    settings = crud.get_all_settings(db)

    if user.is_reseller:
        await callback.answer(
            "شما قبلاً نماینده هستید.",
            show_alert=True,
        )
        return

    if settings.start_price == 0:
        await send_register_request(
            callback.bot,
            user,
        )

        await callback.message.edit_text(
            "✅ درخواست شما با موفقیت ثبت شد.\n\n"
            "پس از بررسی توسط مدیریت نتیجه برای شما ارسال خواهد شد."
        )
        return

    await callback.message.edit_text(
        text=(
            f"💳 هزینه ثبت نمایندگی: <b>{settings.start_price:,}</b> تومان\n\n"
            "روش پرداخت را انتخاب کنید."
        ),
        parse_mode="HTML",
        reply_markup=payment_methods_register(),
    )


@r.callback_query(F.data == "user:register_pay_card")
async def pay_register(callback: CallbackQuery, state: FSMContext):
    db = sessionLocal()

    settings = crud.get_all_settings(db)

    text = (
        "💳 <b>پرداخت کارت به کارت</b>\n\n"
        f"💰 مبلغ: <b>{settings.start_price:,}</b> تومان\n\n"
        f"💳 شماره کارت:\n<code>{settings.card_number}</code>\n\n"
        f"👤 صاحب کارت:\n<b>{settings.card_holder}</b>\n\n"
        "پس از پرداخت، عکس رسید را ارسال نمایید."
    )
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
    )

    await state.set_state(RegisterState.waiting_receipt)


@r.message(RegisterState.waiting_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
    db = sessionLocal()

    user = crud.get_user(db, message.from_user.id)

    photo = message.photo[-1].file_id

    await send_register_request(
        message.bot,
        user,
        photo=photo,
    )

    await message.answer(
        "✅ رسید پرداخت دریافت شد.\n" "پس از بررسی توسط مدیریت نتیجه اعلام خواهد شد."
    )

    await state.clear()


@r.message(RegisterState.waiting_receipt)
async def invalid_receipt(message: Message):
    await message.answer("❌ لطفاً فقط تصویر رسید پرداخت را ارسال کنید.")


async def send_register_request(bot, user, photo=None):

    text = (
        "📥 <b>درخواست جدید نمایندگی</b>\n\n"
        f"👤 نام: {user.name}\n"
        f"🆔 <code>{user.chat_id}</code>\n"
        f"👤 یوزرنیم: @{user.username or '-'}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تایید",
                    callback_data=f"admin:accept_register:{user.chat_id}",
                ),
                InlineKeyboardButton(
                    text="❌ رد",
                    callback_data=f"admin:reject_register:{user.chat_id}",
                ),
            ]
        ]
    )

    if photo:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


@r.callback_query(F.data == "user:buy_traffic")
async def buy_traffic(callback: CallbackQuery, state: FSMContext):
    db = sessionLocal()

    user = crud.get_user(db, callback.from_user.id)

    if not user.is_reseller:
        await callback.answer(
            "فقط نمایندگان امکان خرید ترافیک دارند.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "📦 مقدار ترافیک مورد نظر را به گیگابایت وارد کنید.\n\n"
        "مثال: <code>50</code>",
        parse_mode="HTML",
    )

    await state.set_state(BuyTrafficState.amount)


@r.message(BuyTrafficState.amount)
async def buy_amount(message: Message, state: FSMContext):
    db = sessionLocal()

    if not message.text.isdigit():
        await message.answer("❌ فقط عدد وارد کنید.", reply_markup=cancel_button())
        return

    gb = int(message.text)

    settings = crud.get_all_settings(db)

    if gb <= 0:
        await message.answer("❌ مقدار نامعتبر است.", reply_markup=cancel_button())
        return

    if gb * settings.price_per_gb < settings.minimum_purchase_amount:
        await message.answer(
            f"حداقل خرید {settings.minimum_purchase_amount} تومان است.",
            reply_markup=cancel_button(),
        )
        return

    price = gb * settings.price_per_gb

    await state.update_data(
        gb=gb,
        price=price,
    )

    await message.answer(
        f"""
💳 خرید ترافیک

📦 مقدار:
<b>{gb} GB</b>
💰 مبلغ:
<b>{price:,} تومان</b>

روش پرداخت را انتخاب کنید.
""",
        parse_mode="HTML",
        reply_markup=payment_methods_buy(),
    )


@r.callback_query(F.data == "user:buy_pay_card")
async def pay_card(callback: CallbackQuery, state: FSMContext):
    db = sessionLocal()

    settings = crud.get_all_settings(db)

    data = await state.get_data()

    await callback.message.edit_text(
        f"""
💳 کارت به کارت

مبلغ:
<b>{data['price']:,} تومان</b>

شماره کارت
<code>{settings.card_number}</code>
{settings.card_holder}

پس از پرداخت، تصویر رسید را ارسال کنید.
""",
        parse_mode="HTML",
        reply_markup=cancel_button(),
    )

    await state.set_state(BuyTrafficState.receipt)


@r.message(BuyTrafficState.receipt, F.photo)
async def receipt(message: Message, state: FSMContext):
    db = sessionLocal()

    data = await state.get_data()

    user = crud.get_user(db, message.from_user.id)

    photo = message.photo[-1].file_id

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تایید",
                    callback_data=f"admin:accept_buy:{user.chat_id}:{data['gb']}",
                ),
                InlineKeyboardButton(
                    text="❌ رد",
                    callback_data=f"admin:reject_buy:{user.chat_id}",
                ),
            ]
        ]
    )

    caption = f"""
🛒 خرید ترافیک
👤 {user.name}
🆔 <code>{user.chat_id}</code>
📦 {data['gb']} GB

💰 {data['price']:,} تومان
"""

    await message.bot.send_photo(
        ADMIN_ID,
        photo=photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    await message.answer(
        "✅ رسید ارسال شد.\nپس از تایید مدیریت، ترافیک شما افزایش خواهد یافت."
    )

    await state.clear()
