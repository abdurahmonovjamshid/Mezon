"""Klaviatura qurish yordamchilari. Reply-klaviaturalar suhbat davomida doim
ko'rinadigan "Bekor qilish"/"O'tkazib yuborish" kabi tugmalar uchun, inline
klaviaturalar esa ro'yxatdan tanlash (mijoz/mahsulot/supplier) va
tasdiqlash/bekor qilish uchun ishlatiladi (PhoneAd-bot'dagi
`step_keyboard()`/`models_keyboard(page)` uslubiga o'xshash)."""
import calendar as calendar_module
import contextvars
from datetime import date

from telebot import types

CANCEL_TEXT = "❌ Bekor qilish"
BACK_TEXT = "⬅️ Orqaga"
SKIP_TEXT = "⏭ O'tkazib yuborish"
DONE_TEXT = "✅ Yakunlash"
ADD_MORE_TEXT = "➕ Yana qo'shish"

MENU_DASHBOARD = '🏠 Bosh sahifa'
MENU_SALES = '🛍 Sotuv'
MENU_PURCHASES = '📥 Xarid'
MENU_PAYMENTS = "💸 To'lovlar"
MENU_EXPENSES = '🧾 Xarajatlar'
MENU_INVENTORY = '🏬 Ombor'
MENU_BUTCHERING = "✂️ Bo'laklash"
MENU_CUSTOMERS = '👤 Mijozlar'
MENU_SUPPLIERS = '🚛 Yetkazib beruvchilar'
MENU_KASSA = '👛 Kassa'
MENU_REPORTS = '📊 Hisobotlar'


# Menyu tugmasi -> bo'lim (rollar bo'yicha ruxsat uchun, apps/accounts/roles.py)
MENU_SECTIONS = {
    MENU_DASHBOARD: 'dashboard',
    MENU_SALES: 'sales',
    MENU_PURCHASES: 'purchases',
    MENU_INVENTORY: 'inventory',
    MENU_BUTCHERING: 'butchering',
    MENU_KASSA: 'kassa',
    MENU_PAYMENTS: 'payments',
    MENU_EXPENSES: 'expenses',
    MENU_CUSTOMERS: 'customers',
    MENU_SUPPLIERS: 'suppliers',
    MENU_REPORTS: 'reports',
}

MENU_LAYOUT = (
    (MENU_DASHBOARD,),
    (MENU_SALES, MENU_PURCHASES),
    (MENU_INVENTORY, MENU_BUTCHERING),
    (MENU_KASSA, MENU_PAYMENTS, MENU_EXPENSES),
    (MENU_CUSTOMERS, MENU_SUPPLIERS),
    (MENU_REPORTS,),
)

# Joriy xabarni yuborgan foydalanuvchi (common.on_text/on_callback o'rnatadi) —
# main_menu() har bir chaqiruvda unga ruxsat etilgan tugmalarnigina ko'rsatadi.
_current_user = contextvars.ContextVar('bot_current_user', default=None)


def set_current_user(user):
    _current_user.set(user)


def menu_allowed(text, user=None):
    from apps.accounts.roles import can_access
    user = user if user is not None else _current_user.get()
    section = MENU_SECTIONS.get(text)
    return section is None or user is None or can_access(user, section)


def main_menu():
    """Bo'limlar guruhlangan: savdo/xarid, ombor, moliya, kontragentlar, tahlil.
    Foydalanuvchi roliga ruxsat etilmagan tugmalar ko'rsatilmaydi."""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in MENU_LAYOUT:
        buttons = [text for text in row if menu_allowed(text)]
        if buttons:
            kb.row(*buttons)
    return kb


def cancel_only():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(CANCEL_TEXT)
    return kb


def cancel_and_skip():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(SKIP_TEXT)
    kb.row(CANCEL_TEXT)
    return kb


def confirm_cancel_inline(confirm_data, cancel_data='noop:cancel'):
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton('✅ Tasdiqlash', callback_data=confirm_data),
        types.InlineKeyboardButton('❌ Bekor qilish', callback_data=cancel_data),
    )
    return kb


def picker(prefix, items, page=0, page_size=8, extra_rows=None):
    """`items`: [(id, label), ...]. Callback data: "{prefix}:{id}" har bir
    qator uchun, "{prefix}_pg:{page}" sahifalash uchun."""
    kb = types.InlineKeyboardMarkup()
    start = page * page_size
    chunk = items[start:start + page_size]
    for item_id, label in chunk:
        kb.row(types.InlineKeyboardButton(str(label)[:60], callback_data=f'{prefix}:{item_id}'))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton('⬅️', callback_data=f'{prefix}_pg:{page - 1}'))
    if start + page_size < len(items):
        nav.append(types.InlineKeyboardButton('➡️', callback_data=f'{prefix}_pg:{page + 1}'))
    if nav:
        kb.row(*nav)
    for row in (extra_rows or []):
        kb.row(*row)
    return kb


MONTH_NAMES_UZ = [
    'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
    'Iyul', 'Avgust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr',
]
WEEKDAY_LABELS_UZ = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya']


def calendar_keyboard(prefix, year=None, month=None, extra_rows=None):
    """Oy grid'i: har bir kun `{prefix}:{YYYY-MM-DD}`, oy almashtirish
    `{prefix}_nav:{YYYY-MM}`, bo'sh/sarlavha katakchalari `noop:cal`
    callback_data bilan (dispatcher bularni indamay javob beradi)."""
    today = date.today()
    year = year or today.year
    month = month or today.month
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    kb = types.InlineKeyboardMarkup(row_width=7)
    kb.row(
        types.InlineKeyboardButton('◀️', callback_data=f'{prefix}_nav:{prev_year}-{prev_month:02d}'),
        types.InlineKeyboardButton(f'{MONTH_NAMES_UZ[month - 1]} {year}', callback_data='noop:cal'),
        types.InlineKeyboardButton('▶️', callback_data=f'{prefix}_nav:{next_year}-{next_month:02d}'),
    )
    kb.row(*[types.InlineKeyboardButton(w, callback_data='noop:cal') for w in WEEKDAY_LABELS_UZ])
    for week in calendar_module.Calendar(firstweekday=0).monthdayscalendar(year, month):
        kb.row(*[
            types.InlineKeyboardButton(
                str(day) if day else ' ',
                callback_data=f'{prefix}:{year}-{month:02d}-{day:02d}' if day else 'noop:cal',
            )
            for day in week
        ])
    for row in (extra_rows or []):
        kb.row(*row)
    return kb


def add_more_or_done(add_data, done_data):
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton(ADD_MORE_TEXT, callback_data=add_data))
    kb.row(types.InlineKeyboardButton(DONE_TEXT, callback_data=done_data))
    return kb
