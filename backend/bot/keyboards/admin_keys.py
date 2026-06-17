from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💻 انتخاب پنل برای فروش",
                    callback_data="admin:select_panel_for_sale",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 تنظیم قیمت نمایندگی", callback_data="admin:set_price"
                ),
            ],
            [
                InlineKeyboardButton(text="ℹ️ آمار", callback_data="admin:info"),
            ],
        ]
    )
    return keyboard


def show_panel_selection(panels):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{panel.name} - {panel.panel_type} - {"✅" if panel.for_bot else "❌"}",
                    callback_data=f"admin:panel_selected:{panel.id}",
                )
            ]
            for panel in panels
        ]
    )
    return keyboard
