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
            [
                InlineKeyboardButton(text="👤 حساب من", callback_data="user:my_acc"),
                InlineKeyboardButton(
                    text="🔋 خرید حجم اضافه", callback_data="user:buy_traffic"
                ),
            ],
        ]
    )
    return keyboard


def payment_methods_register():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 کارت به کارت",
                    callback_data="user:register_pay_card",
                )
            ]
        ]
    )


def payment_methods_buy():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 کارت به کارت",
                    callback_data="user:buy_pay_card",
                )
            ]
        ]
    )


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


def cancel_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ لغو", callback_data="user:cancel")]
        ]
    )
    return keyboard
