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
                (
                    InlineKeyboardButton(
                        text="⚙️ تنطیمات", callback_data="admin:settings"
                    )
                ),
            ],
        ]
    )
    return keyboard


def settings_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 تنظیم پیام آغاز", callback_data="admin:set_start_message"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 تنظیم پیام راهنما", callback_data="admin:set_help_message"
                )
            ],
        ]
    )
    return keyboard


def cancel_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ خروج", callback_data="admin:cancel")]
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
