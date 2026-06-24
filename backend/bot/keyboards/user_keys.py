from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_users_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ درخواست نمایندگی",
                    callback_data="user:register",
                )
            ],
            [InlineKeyboardButton(text="👤 حساب من", callback_data="user:my_acc")],
        ]
    )
    return keyboard


def payment_methods():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 کارت به کارت",
                    callback_data="user:pay_with_card",
                )
            ],
        ]
    )
    return keyboard


def register_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ ثبت درخواست",
                    callback_data="user:request_for_register",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ انصراف",
                    callback_data="user:back",
                )
            ],
        ]
    )
