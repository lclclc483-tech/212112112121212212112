import asyncio
import datetime
import logging
from typing import Optional

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ----------------------------------------------------
# НАСТРОЙКИ И КОНФИГУРАЦИЯ
import os

# Код считывает токен из настроек сервера
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7211484627
DB_NAME = "marketplace.db"

DISCLAIMER_TEXT = (
    "⚠️ <b>ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ (DISCLAIMER)</b>\n\n"
    "Данный бот является исключительно информационным посредником "
    "(площадкой для размещения объявлений) и не выступает стороной в сделках между пользователями.\n\n"
    "<b>1. Ограничение ответственности:</b>\n"
    "Администрация и разработчики бота <b>не несут никакой ответственности</b> за:\n"
    "• Финансовые, материальные или любые другие риски и убытки, возникшие в ходе сотрудничества пользователей.\n"
    "• Честность, качество, сроки и выполнение договоренностей между заказчиками и исполнителями.\n"
    "• Любые мошеннические действия, обман или недобросовестность участников.\n\n"
    "<b>2. Согласие с условиями:</b>\n"
    "Нажимая любую кнопку, совершая действие или продолжая использование бота, "
    "вы автоматически подтверждаете, что полностью согласны с данными условиями.\n\n"
    "<b>3. Отсутствие претензий:</b>\n"
    "Вы принимаете решение о любых сделках на свой страх и риск и обязуетесь "
    "<b>не предъявлять никаких претензий, исков и требований</b> к создателям и администраторам бота. "
    "Все спорные вопросы пользователи решают между собой самостоятельно."
)

CATEGORIES = {
    "IT": [
        "Разработка сайта", "Разработка интернет-магазина", "Разработка Telegram-бота",
        "Разработка Discord-бота", "Разработка приложения", "Разработка веб-приложения",
        "Парсер", "Скрипт", "Автоматизация", "API / интеграция", "База данных",
        "Исправление ошибок", "Доработка проекта", "Настройка сервера", "Настройка хостинга",
        "AI / нейросети", "Интеграция AI", "CRM", "Другое IT"
    ],
    "Дизайн": [
        "Логотип", "Фирменный стиль", "Баннер", "Постер", "Обложка", "Превью",
        "Дизайн сайта", "UI/UX", "Дизайн приложения", "Дизайн Telegram-канала",
        "Дизайн соцсетей", "Презентация", "Инфографика", "Визитка", "Иллюстрация",
        "3D-дизайн", "Другое"
    ],
    "Видео": [
        "Монтаж видео", "Монтаж TikTok", "Монтаж Reels", "Монтаж Shorts", "Монтаж YouTube",
        "Монтаж рекламы", "Монтаж подкаста", "Субтитры", "Motion Design", "Анимация",
        "VFX", "Цветокоррекция", "Превью", "Другое"
    ],
    "Фото": [
        "Обработка фото", "Ретушь", "Удаление фона", "Замена фона", "Обработка товаров",
        "Обработка портретов", "Восстановление фото", "Коллаж", "AI-обработка", "Другое"
    ],
    "Тексты": [
        "Копирайтинг", "Рерайтинг", "SEO-текст", "Статья", "Пост", "Описание товара",
        "Описание услуги", "Рекламный текст", "Продающий текст", "Сценарий",
        "Редактура", "Корректура", "Расшифровка аудио", "Другое"
    ],
    "SMM": [
        "Ведение Telegram", "Ведение TikTok", "Ведение Instagram", "Ведение VK",
        "Создание контента", "Контент-план", "Оформление соцсетей", "Постинг",
        "Продвижение", "Реклама в Telegram", "Работа с блогерами", "Другое"
    ],
    "Маркетинг и реклама": [
        "Настройка рекламы", "Таргет", "Контекстная реклама", "SEO", "Лидогенерация",
        "Поиск клиентов", "Реклама в Telegram", "Реклама в соцсетях", "Анализ конкурентов",
        "Маркетинговая стратегия", "Другое"
    ],
    "Аудио": [
        "Озвучка", "Диктор", "Голос за кадром", "Монтаж аудио", "Чистка звука",
        "Обработка голоса", "Подкаст", "Саунд-дизайн", "Другое"
    ],
    "Музыка": [
        "Создание бита", "Аранжировка", "Сведение", "Мастеринг", "Написание музыки",
        "Написание текста песни", "Обработка вокала", "Ремикс", "Другое"
    ],
    "Перевод": [
        "Перевод текста", "Перевод документов", "Локализация", "Субтитры",
        "Расшифровка", "Другое"
    ],
    "Документы": [
        "Резюме", "Презентация", "Коммерческое предложение", "Оформление документа",
        "Набор текста", "Таблицы", "Excel", "Google Таблицы", "Другое"
    ],
    "3D": [
        "3D-модель", "3D-визуализация", "3D-анимация", "Модель для печати",
        "Рендер", "Архитектурная визуализация", "Другое"
    ],
    "Иигры": [
        "Разработка игры", "Unity", "Unreal Engine", "Godot", "Игровые ассеты",
        "3D-модели", "Моды", "Другое"
    ],
    "Другое": [
        "Свой вариант"
    ]
}

logging.basicConfig(level=logging.INFO)


# ----------------------------------------------------
# СОСТОЯНИЯ FSM
# ----------------------------------------------------
class OrderForm(StatesGroup):
    category = State()
    subcategory = State()
    custom_category = State()
    description = State()
    price = State()
    deadline = State()
    contact = State()


class ServiceForm(StatesGroup):
    category = State()
    subcategory = State()
    custom_category = State()
    description = State()
    price = State()
    deadline = State()
    contact = State()


class PortfolioForm(StatesGroup):
    category = State()
    subcategory = State()
    custom_category = State()
    media = State()
    title = State()
    description = State()
    price = State()


class EditPostForm(StatesGroup):
    post_id = State()
    field = State()
    value = State()


class SearchOrderForm(StatesGroup):
    category = State()
    subcategory = State()
    custom_category = State()
    sort_choice = State()


class SearchServiceForm(StatesGroup):
    category = State()
    subcategory = State()
    custom_category = State()
    sort_choice = State()


class UsernameSearchForm(StatesGroup):
    username = State()


class AdminBroadcastForm(StatesGroup):
    text = State()


# ----------------------------------------------------
# БАЗА ДАННЫХ
# ----------------------------------------------------
async def init_db() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                is_banned INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                category TEXT,
                subcategory TEXT,
                title TEXT,
                description TEXT,
                price INTEGER,
                deadline TEXT,
                contact TEXT,
                media_id TEXT,
                media_type TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                target_id INTEGER,
                target_type TEXT,
                PRIMARY KEY (user_id, target_id, target_type)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                user_id INTEGER,
                blocked_user_id INTEGER,
                PRIMARY KEY (user_id, blocked_user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER,
                category TEXT,
                subcategory TEXT,
                PRIMARY KEY (user_id, category, subcategory)
            )
        """)
        await db.commit()

        # Автоматическая миграция для предотвращения ошибки "no such column: subcategory"
        try:
            await db.execute("ALTER TABLE posts ADD COLUMN subcategory TEXT;")
            await db.commit()
        except Exception:
            pass


async def add_user(user_id: int, username: Optional[str], full_name: str) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def check_daily_limit(user_id: int) -> bool:
    time_24h_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT COUNT(*) FROM posts WHERE user_id = ? AND created_at >= ? AND type IN ('order', 'service')",
                (user_id, time_24h_ago)
        ) as cursor:
            res = await cursor.fetchone()
            return res[0] < 5 if res else True


# ----------------------------------------------------
# КЛАВИАТУРЫ
# ----------------------------------------------------
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Создать заказ"), KeyboardButton(text="Искать заказ")],
        [KeyboardButton(text="Создать услугу"), KeyboardButton(text="Искать услугу")],
        [KeyboardButton(text="Поиск по @username")],
        [KeyboardButton(text="👤 Мой профиль")]
    ]
    if user_id == ADMIN_ID:
        kb.append([KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_inline_categories(prefix: str, include_all: bool = False) -> InlineKeyboardMarkup:
    kb = []
    if include_all:
        kb.append([InlineKeyboardButton(text="🌐 Все категории", callback_data=f"{prefix}_cat_ALL")])

    row = []
    for cat in CATEGORIES.keys():
        row.append(InlineKeyboardButton(text=cat, callback_data=f"{prefix}_cat_{cat}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)

    kb.append([InlineKeyboardButton(text="✍️ Свой вариант", callback_data=f"{prefix}_cat_CUSTOM")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="nav_close_flow")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_inline_subcategories(prefix: str, category: str, include_all: bool = False) -> InlineKeyboardMarkup:
    kb = []
    if include_all:
        kb.append([InlineKeyboardButton(text="🌐 Все подкатегории", callback_data=f"{prefix}_sub_ALL")])

    subcategories_list = CATEGORIES.get(category, [])
    row = []
    for idx, sub in enumerate(subcategories_list):
        row.append(InlineKeyboardButton(text=sub, callback_data=f"{prefix}_sub_{idx}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)

    kb.append([InlineKeyboardButton(text="✍️ Свой вариант", callback_data=f"{prefix}_sub_CUSTOM")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"nav_back_to_cat_{prefix}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_inline_sort_keyboard(prefix: str) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🆕 Новые", callback_data=f"{prefix}_sort_new"),
            InlineKeyboardButton(text="📉 Дешевле", callback_data=f"{prefix}_sort_cheap")
        ],
        [
            InlineKeyboardButton(text="📈 Дороже", callback_data=f"{prefix}_sort_expensive")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"nav_back_to_sub_{prefix}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )


def get_skip_back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")], [KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )


# ----------------------------------------------------
# ДИСПАТЧЕР И НАВИГАЦИЯ
# ----------------------------------------------------
dp = Dispatcher(storage=MemoryStorage())


@dp.message(F.text.in_(["Назад", "⬅️ Назад"]))
async def global_back_handler(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    await message.answer("Возвращаемся в главное меню:", reply_markup=get_main_keyboard(message.from_user.id))


@dp.callback_query(F.data == "nav_close_flow")
async def nav_close_flow_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await state.clear()
    await callback.answer()


@dp.callback_query(F.data.startswith("nav_back_to_cat_"))
async def nav_back_to_cat_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    prefix = callback.data.replace("nav_back_to_cat_", "")

    if prefix == "ord":
        await state.set_state(OrderForm.category)
        await callback.message.edit_text("Выберите категорию заказа:", reply_markup=get_inline_categories("ord"))
    elif prefix == "srv":
        await state.set_state(ServiceForm.category)
        await callback.message.edit_text("Выберите категорию услуги:", reply_markup=get_inline_categories("srv"))
    elif prefix == "pf":
        await state.set_state(PortfolioForm.category)
        await callback.message.edit_text("Выберите категорию работы:", reply_markup=get_inline_categories("pf"))
    elif prefix == "s_ord":
        await state.set_state(SearchOrderForm.category)
        await callback.message.edit_text("Выберите категорию для поиска заказов:",
                                         reply_markup=get_inline_categories("s_ord", include_all=True))
    elif prefix == "s_srv":
        await state.set_state(SearchServiceForm.category)
        await callback.message.edit_text("Выберите категорию для поиска услуг:",
                                         reply_markup=get_inline_categories("s_srv", include_all=True))

    await callback.answer()


@dp.callback_query(F.data.startswith("nav_back_to_sub_"))
async def nav_back_to_sub_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    prefix = callback.data.replace("nav_back_to_sub_", "")
    data = await state.get_data()
    cat = data.get('category', 'ALL')

    if cat == "ALL":
        if prefix == "s_ord":
            await state.set_state(SearchOrderForm.category)
            await callback.message.edit_text("Выберите категорию для поиска заказов:",
                                             reply_markup=get_inline_categories("s_ord", include_all=True))
        elif prefix == "s_srv":
            await state.set_state(SearchServiceForm.category)
            await callback.message.edit_text("Выберите категорию для поиска услуг:",
                                             reply_markup=get_inline_categories("s_srv", include_all=True))
    else:
        if prefix == "s_ord":
            await state.set_state(SearchOrderForm.subcategory)
            await callback.message.edit_text("Выберите подкатегорию:",
                                             reply_markup=get_inline_subcategories("s_ord", cat, include_all=True))
        elif prefix == "s_srv":
            await state.set_state(SearchServiceForm.subcategory)
            await callback.message.edit_text("Выберите подкатегорию:",
                                             reply_markup=get_inline_subcategories("s_srv", cat, include_all=True))

    await callback.answer()


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    # Кнопка подтверждения дисклеймера
    disclaimer_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я согласен / Войти", callback_data="accept_disclaimer")]
        ]
    )

    # Отправляем дисклеймер при /start
    await message.answer(
        text=DISCLAIMER_TEXT,
        parse_mode="HTML",
        reply_markup=disclaimer_kb
    )


@dp.callback_query(F.data == "accept_disclaimer")
async def accept_disclaimer_cb(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await callback.message.answer(
        "Добро пожаловать на биржу! Выберите действие в меню ниже:",
        reply_markup=get_main_keyboard(callback.from_user.id)
    )
    await callback.answer()


# ----------------------------------------------------
# ПРОФИЛЬ
# ----------------------------------------------------
def get_profile_data(viewer_id: int, target_user_id: int, user_tuple: tuple) -> tuple[str, InlineKeyboardMarkup]:
    username, full_name = user_tuple
    is_me = (viewer_id == target_user_id)
    profile_title = "👤 **Ваш профиль:**" if is_me else f"👤 **Профиль пользователя:** {full_name}"

    text = f"{profile_title}\n\n**Имя:** {full_name}\n**Username:** @{username or 'отсутствует'}\n**ID:** `{target_user_id}`"

    kb = [
        [
            InlineKeyboardButton(text="📦 Заказы", callback_data=f"list_{target_user_id}_order_0"),
            InlineKeyboardButton(text="🛠 Услуги", callback_data=f"list_{target_user_id}_service_0"),
            InlineKeyboardButton(text="📁 Портфолио", callback_data=f"list_{target_user_id}_portfolio_0")
        ]
    ]

    if is_me:
        kb.append([InlineKeyboardButton(text="➕ Добавить в портфолио", callback_data="btn_add_portfolio")])
        kb.append([
            InlineKeyboardButton(text="⭐️ Избранное", callback_data="btn_favorites"),
            InlineKeyboardButton(text="🚫 Заблокированные", callback_data="btn_blocked")
        ])
        kb.append([InlineKeyboardButton(text="🔔 Уведомления", callback_data="btn_notifications")])
        kb.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")])
    else:
        kb.append([InlineKeyboardButton(text="⭐️ Добавить в избранное", callback_data=f"fav_user_{target_user_id}")])
        kb.append([InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"block_user_{target_user_id}")])
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="delete_msg")])

    return text, InlineKeyboardMarkup(inline_keyboard=kb)


async def send_profile_card(viewer_id: int, target_user_id: int, message: Message) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username, full_name FROM users WHERE user_id = ?", (target_user_id,)) as cursor:
            user = await cursor.fetchone()

    if not user:
        await message.answer("Пользователь не найден.")
        return

    text, reply_markup = get_profile_data(viewer_id, target_user_id, user)
    await message.answer(text, reply_markup=reply_markup)


@dp.message(F.text == "👤 Мой профиль")
async def show_my_profile(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    await send_profile_card(message.from_user.id, message.from_user.id, message)


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard(callback.from_user.id))
    await callback.answer()


@dp.callback_query(F.data == "back_to_profile")
async def back_to_profile_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username, full_name FROM users WHERE user_id = ?",
                              (callback.from_user.id,)) as cursor:
            user = await cursor.fetchone()

    if user:
        text, reply_markup = get_profile_data(callback.from_user.id, callback.from_user.id, user)
        try:
            await callback.message.edit_text(text, reply_markup=reply_markup)
        except TelegramAPIError:
            await callback.message.delete()
            await callback.message.answer(text, reply_markup=reply_markup)
    await callback.answer()


# ----------------------------------------------------
# РЕНДЕР И ПАГИНАЦИЯ (ОТРИСОВКА КАРТОЧЕК)
# ----------------------------------------------------
async def render_post_page(callback: CallbackQuery, target_id: int, post_type: str, page: int) -> None:
    if not isinstance(callback.message, Message):
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                """SELECT id, title, description, price, deadline, contact, media_id, media_type, category, subcategory 
                   FROM posts WHERE user_id = ? AND type = ? AND status = 'active' ORDER BY id DESC""",
                (target_id, post_type)
        ) as cursor:
            items = [tuple(r) for r in await cursor.fetchall()]

    if not items:
        try:
            await callback.message.delete()
        except TelegramAPIError:
            pass
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="back_to_profile")]])
        await callback.message.answer("Список пуст.", reply_markup=kb)
        return

    total = len(items)
    if page >= total:
        page = total - 1

    item = items[page]
    p_id, title, desc, price, deadline, contact, media_id, media_type, category, subcategory = item
    is_owner = (callback.from_user.id == target_id)

    type_name = "Заказ" if post_type == "order" else ("Услуга" if post_type == "service" else "Работа из портфолио")
    header = f"📌 **[{type_name}]** ({page + 1}/{total})\n\n"

    cat_str = f"{category} -> {subcategory}" if subcategory else category

    if post_type == "portfolio":
        if is_owner:
            content = f"**Название:** {title}\n**Категория:** {cat_str}\n**Описание:** {desc}\n💰 **Цена:** {price or 'не указана'} руб."
        else:
            price_text = f"\n\n💰 {price} руб." if price else ""
            content = f"**{title}** ({cat_str})\n\n{desc}{price_text}"
    else:
        content = f"**Категория:** {cat_str}\n**Описание:** {desc}\n💰 **Цена:** {price} руб.\n⏳ **Срок:** {deadline}\n📞 **Контакт:** {contact}"

    full_text = header + content

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Предыдущ", callback_data=f"list_{target_id}_{post_type}_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(text="⬅️ В профиль", callback_data="back_to_profile"))
    if page < total - 1:
        nav_buttons.append(
            InlineKeyboardButton(text="Следущ ➡️", callback_data=f"list_{target_id}_{post_type}_{page + 1}"))

    kb = [nav_buttons]

    if is_owner:
        kb.append([
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_post_{p_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_post_{p_id}_{post_type}_{page}")
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    try:
        await callback.message.delete()
    except TelegramAPIError:
        pass

    if media_id and media_type:
        if media_type == "photo":
            await callback.message.answer_photo(photo=media_id, caption=full_text, reply_markup=keyboard)
        elif media_type == "video":
            await callback.message.answer_video(video=media_id, caption=full_text, reply_markup=keyboard)
        elif media_type == "document":
            await callback.message.answer_document(document=media_id, caption=full_text, reply_markup=keyboard)
    else:
        await callback.message.answer(full_text, reply_markup=keyboard)


@dp.callback_query(F.data.startswith("list_"))
async def process_list_pagination(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    _, target_id_str, post_type, page_str = callback.data.split("_")
    await render_post_page(callback, int(target_id_str), post_type, int(page_str))
    await callback.answer()


@dp.callback_query(F.data == "delete_msg")
async def delete_msg_handler(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        await callback.message.delete()


# ----------------------------------------------------
# УДАЛЕНИЕ С АВТОПЕРЕХОДОМ
# ----------------------------------------------------
@dp.callback_query(F.data.startswith("delete_post_"))
async def delete_my_post(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    data_parts = callback.data.split("_")
    post_id = int(data_parts[2])
    post_type = data_parts[3] if len(data_parts) > 3 else "order"
    page = int(data_parts[4]) if len(data_parts) > 4 else 0

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE posts SET status = 'deleted' WHERE id = ? AND user_id = ?",
                         (post_id, callback.from_user.id))
        await db.commit()

    await callback.answer("Удалено!")
    await render_post_page(callback, callback.from_user.id, post_type, page)


# ----------------------------------------------------
# РЕДАКТИРОВАНИЕ
# ----------------------------------------------------
@dp.callback_query(F.data.startswith("edit_post_"))
async def start_edit_post(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    post_id = int(callback.data.split("_")[2])
    await state.update_data(post_id=post_id)
    await state.set_state(EditPostForm.field)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название", callback_data="field_title")],
        [InlineKeyboardButton(text="Описание", callback_data="field_description")],
        [InlineKeyboardButton(text="Цену", callback_data="field_price")],
        [InlineKeyboardButton(text="Срок", callback_data="field_deadline")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel_edit")]
    ])
    await callback.message.answer("Что именно вы хотите изменить?", reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data == "cancel_edit")
async def cancel_edit_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await state.clear()
    await callback.answer("Редактирование отменено")


@dp.callback_query(F.data.startswith("field_"))
async def process_field_choice(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    field = callback.data.split("_")[1]
    await state.update_data(field=field)
    await state.set_state(EditPostForm.value)

    field_names = {
        "title": "новое название",
        "description": "новое описание",
        "price": "новую цену (число)",
        "deadline": "новый срок"
    }
    await callback.message.answer(f"Введите {field_names.get(field, 'новое значение')}:",
                                  reply_markup=get_back_keyboard())
    await callback.answer()


@dp.message(EditPostForm.value)
async def process_edit_value(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    data = await state.get_data()
    post_id = data['post_id']
    field = data['field']
    val = message.text

    if field == "price" and not val.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return

    val_to_save = int(val) if field == "price" else val

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE posts SET {field} = ? WHERE id = ? AND user_id = ?",
                         (val_to_save, post_id, message.from_user.id))
        await db.commit()

    await state.clear()
    await message.answer("Запись обновлена!", reply_markup=get_main_keyboard(message.from_user.id))


# ----------------------------------------------------
# ДОБАВЛЕНИЕ В ПОРТФОЛИО (INLINE)
# ----------------------------------------------------
@dp.callback_query(F.data == "btn_add_portfolio")
async def start_create_portfolio_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.set_state(PortfolioForm.category)
    await callback.message.answer("Выберите категорию работы:", reply_markup=get_inline_categories("pf"))
    await callback.answer()


@dp.callback_query(F.data.startswith("pf_cat_"), PortfolioForm.category)
async def process_portfolio_category(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    cat = callback.data.split("_")[2]
    if cat == "CUSTOM":
        await state.set_state(PortfolioForm.custom_category)
        await callback.message.edit_text("Введите название категории:")
        await callback.answer()
        return

    await state.update_data(category=cat)
    await state.set_state(PortfolioForm.subcategory)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=get_inline_subcategories("pf", cat))
    await callback.answer()


@dp.callback_query(F.data.startswith("pf_sub_"), PortfolioForm.subcategory)
async def process_portfolio_subcategory(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    sub_val = callback.data.split("_")[2]
    data = await state.get_data()

    if sub_val == "CUSTOM":
        await state.set_state(PortfolioForm.custom_category)
        await callback.message.edit_text("Введите подкатегорию вручную:")
        await callback.answer()
        return

    cat_list = CATEGORIES.get(data.get('category', ''), [])
    subcategory = cat_list[int(sub_val)] if sub_val.isdigit() and int(sub_val) < len(cat_list) else "Все"

    await state.update_data(subcategory=subcategory)
    await state.set_state(PortfolioForm.media)
    await callback.message.delete()
    await callback.message.answer("Отправьте Фото, Видео или Документ работы (или нажмите «Пропустить»):",
                                  reply_markup=get_skip_back_keyboard())
    await callback.answer()


@dp.message(PortfolioForm.custom_category)
async def process_portfolio_custom_category(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(category=message.text, subcategory="Свое")
    await state.set_state(PortfolioForm.media)
    await message.answer("Отправьте Фото, Видео или Документ работы (или нажмите «Пропустить»):",
                         reply_markup=get_skip_back_keyboard())


@dp.message(PortfolioForm.media)
async def process_portfolio_media(message: Message, state: FSMContext) -> None:
    if message.text == "Пропустить":
        await state.update_data(media_id=None, media_type=None)
    elif message.photo:
        await state.update_data(media_id=message.photo[-1].file_id, media_type="photo")
    elif message.video:
        await state.update_data(media_id=message.video.file_id, media_type="video")
    elif message.document:
        await state.update_data(media_id=message.document.file_id, media_type="document")
    else:
        await message.answer("Пожалуйста, отправьте медиафайл или нажмите «Пропустить».")
        return

    await state.set_state(PortfolioForm.title)
    await message.answer("Введите название работы:", reply_markup=get_back_keyboard())


@dp.message(PortfolioForm.title)
async def process_portfolio_title(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(title=message.text)
    await state.set_state(PortfolioForm.description)
    await message.answer("Введите описание работы:", reply_markup=get_back_keyboard())


@dp.message(PortfolioForm.description)
async def process_portfolio_description(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(description=message.text)
    await state.set_state(PortfolioForm.price)
    await message.answer("Укажите цену (по желанию):", reply_markup=get_skip_back_keyboard())


@dp.message(PortfolioForm.price)
async def process_portfolio_price(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    price = int(message.text) if message.text and message.text.isdigit() else None
    data = await state.get_data()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """INSERT INTO posts (user_id, type, category, subcategory, title, description, price, media_id, media_type)
               VALUES (?, 'portfolio', ?, ?, ?, ?, ?, ?, ?)""",
            (message.from_user.id, data.get('category', 'Другое'), data.get('subcategory', 'Все'),
             data.get('title', ''), data.get('description', ''), price, data.get('media_id'),
             data.get('media_type'))
        )
        await db.commit()

    await state.clear()
    await message.answer("Работа успешно добавлена в портфолио!", reply_markup=get_main_keyboard(message.from_user.id))


# ----------------------------------------------------
# СОЗДАНИЕ ЗАКАЗА И УСЛУГИ (INLINE)
# ----------------------------------------------------
@dp.message(F.text == "Создать заказ")
async def start_create_order(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    if not await check_daily_limit(message.from_user.id):
        await message.answer("Превышен лимит: не более 5 объявлений в сутки.")
        return
    await state.set_state(OrderForm.category)
    await message.answer("Выберите категорию заказа:", reply_markup=get_inline_categories("ord"))


@dp.callback_query(F.data.startswith("ord_cat_"), OrderForm.category)
async def process_order_category_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    cat = callback.data.split("_")[2]
    if cat == "CUSTOM":
        await state.set_state(OrderForm.custom_category)
        await callback.message.edit_text("Введите название вашей категории:")
        await callback.answer()
        return

    await state.update_data(category=cat)
    await state.set_state(OrderForm.subcategory)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=get_inline_subcategories("ord", cat))
    await callback.answer()


@dp.callback_query(F.data.startswith("ord_sub_"), OrderForm.subcategory)
async def process_order_subcategory_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    sub_val = callback.data.split("_")[2]
    data = await state.get_data()

    if sub_val == "CUSTOM":
        await state.set_state(OrderForm.custom_category)
        await callback.message.edit_text("Введите подкатегорию вручную:")
        await callback.answer()
        return

    cat_list = CATEGORIES.get(data.get('category', ''), [])
    subcategory = cat_list[int(sub_val)] if sub_val.isdigit() and int(sub_val) < len(cat_list) else "Все"

    await state.update_data(subcategory=subcategory)
    await state.set_state(OrderForm.description)
    await callback.message.delete()
    await callback.message.answer("Введите описание заказа:", reply_markup=get_back_keyboard())
    await callback.answer()


@dp.message(OrderForm.custom_category)
async def process_order_custom_category(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(category=message.text, subcategory="Свое")
    await state.set_state(OrderForm.description)
    await message.answer("Введите описание заказа:", reply_markup=get_back_keyboard())


@dp.message(OrderForm.description)
async def process_order_description(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(description=message.text)
    await state.set_state(OrderForm.price)
    await message.answer("Укажите цену (только число):", reply_markup=get_back_keyboard())


@dp.message(OrderForm.price)
async def process_order_price(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    await state.update_data(price=int(message.text))
    await state.set_state(OrderForm.deadline)
    await message.answer("Укажите срок исполнения:", reply_markup=get_back_keyboard())


@dp.message(OrderForm.deadline)
async def process_order_deadline(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(deadline=message.text)
    await state.set_state(OrderForm.contact)
    await message.answer("Укажите контакт для связи:", reply_markup=get_back_keyboard())


@dp.message(OrderForm.contact)
async def process_order_contact(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    await state.update_data(contact=message.text)
    data = await state.get_data()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """INSERT INTO posts (user_id, type, category, subcategory, description, price, deadline, contact)
               VALUES (?, 'order', ?, ?, ?, ?, ?, ?)""",
            (message.from_user.id, data.get('category', 'Другое'), data.get('subcategory', 'Все'),
             data.get('description', ''), data.get('price', 0), data.get('deadline', ''), data.get('contact', ''))
        )
        await db.commit()

    await state.clear()
    await message.answer("Заказ успешно создан!", reply_markup=get_main_keyboard(message.from_user.id))


@dp.message(F.text == "Создать услугу")
async def start_create_service(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    if not await check_daily_limit(message.from_user.id):
        await message.answer("Превышен лимит: не более 5 объявлений в сутки.")
        return
    await state.set_state(ServiceForm.category)
    await message.answer("Выберите категорию услуги:", reply_markup=get_inline_categories("srv"))


@dp.callback_query(F.data.startswith("srv_cat_"), ServiceForm.category)
async def process_service_category_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    cat = callback.data.split("_")[2]
    if cat == "CUSTOM":
        await state.set_state(ServiceForm.custom_category)
        await callback.message.edit_text("Введите название вашей категории:")
        await callback.answer()
        return

    await state.update_data(category=cat)
    await state.set_state(ServiceForm.subcategory)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=get_inline_subcategories("srv", cat))
    await callback.answer()


@dp.callback_query(F.data.startswith("srv_sub_"), ServiceForm.subcategory)
async def process_service_subcategory_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    sub_val = callback.data.split("_")[2]
    data = await state.get_data()

    if sub_val == "CUSTOM":
        await state.set_state(ServiceForm.custom_category)
        await callback.message.edit_text("Введите подкатегорию вручную:")
        await callback.answer()
        return

    cat_list = CATEGORIES.get(data.get('category', ''), [])
    subcategory = cat_list[int(sub_val)] if sub_val.isdigit() and int(sub_val) < len(cat_list) else "Все"

    await state.update_data(subcategory=subcategory)
    await state.set_state(ServiceForm.description)
    await callback.message.delete()
    await callback.message.answer("Введите описание услуги:", reply_markup=get_back_keyboard())
    await callback.answer()


@dp.message(ServiceForm.custom_category)
async def process_service_custom_category(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(category=message.text, subcategory="Свое")
    await state.set_state(ServiceForm.description)
    await message.answer("Введите описание услуги:", reply_markup=get_back_keyboard())


@dp.message(ServiceForm.description)
async def process_service_description(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(description=message.text)
    await state.set_state(ServiceForm.price)
    await message.answer("Укажите цену (только число):", reply_markup=get_back_keyboard())


@dp.message(ServiceForm.price)
async def process_service_price(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    await state.update_data(price=int(message.text))
    await state.set_state(ServiceForm.deadline)
    await message.answer("Укажите срок исполнения:", reply_markup=get_back_keyboard())


@dp.message(ServiceForm.deadline)
async def process_service_deadline(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(deadline=message.text)
    await state.set_state(ServiceForm.contact)
    await message.answer("Укажите контакт для связи:", reply_markup=get_back_keyboard())


@dp.message(ServiceForm.contact)
async def process_service_contact(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    await state.update_data(contact=message.text)
    data = await state.get_data()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """INSERT INTO posts (user_id, type, category, subcategory, description, price, deadline, contact)
               VALUES (?, 'service', ?, ?, ?, ?, ?, ?)""",
            (message.from_user.id, data.get('category', 'Другое'), data.get('subcategory', 'Все'),
             data.get('description', ''), data.get('price', 0), data.get('deadline', ''), data.get('contact', ''))
        )
        await db.commit()

    await state.clear()
    await message.answer("Услуга успешно создана!", reply_markup=get_main_keyboard(message.from_user.id))


# ----------------------------------------------------
# ПОИСК ОБЪЯВЛЕНИЙ (INLINE)
# ----------------------------------------------------
@dp.message(F.text == "Искать заказ")
async def start_search_order(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchOrderForm.category)
    await message.answer("Выберите категорию для поиска заказов:",
                         reply_markup=get_inline_categories("s_ord", include_all=True))


@dp.callback_query(F.data.startswith("s_ord_cat_"), SearchOrderForm.category)
async def search_order_cat_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    cat = callback.data.split("_")[3]

    if cat == "ALL":
        await state.update_data(category="ALL", subcategory="ALL", post_type="order")
        await state.set_state(SearchOrderForm.sort_choice)
        await callback.message.edit_text("Выберите вариант сортировки:", reply_markup=get_inline_sort_keyboard("s_ord"))
        await callback.answer()
        return

    if cat == "CUSTOM":
        await state.set_state(SearchOrderForm.custom_category)
        await callback.message.edit_text("Введите название категории:")
        await callback.answer()
        return

    await state.update_data(category=cat, post_type="order")
    await state.set_state(SearchOrderForm.subcategory)
    await callback.message.edit_text("Выберите подкатегорию:",
                                     reply_markup=get_inline_subcategories("s_ord", cat, include_all=True))
    await callback.answer()


@dp.callback_query(F.data.startswith("s_ord_sub_"), SearchOrderForm.subcategory)
async def search_order_subcat_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    sub_val = callback.data.split("_")[3]
    data = await state.get_data()

    if sub_val == "ALL":
        subcat = "ALL"
    elif sub_val == "CUSTOM":
        await state.set_state(SearchOrderForm.custom_category)
        await callback.message.edit_text("Введите подкатегорию вручную:")
        await callback.answer()
        return
    else:
        cat_list = CATEGORIES.get(data.get('category', ''), [])
        subcat = cat_list[int(sub_val)] if sub_val.isdigit() and int(sub_val) < len(cat_list) else "ALL"

    await state.update_data(subcategory=subcat)
    await state.set_state(SearchOrderForm.sort_choice)
    await callback.message.edit_text("Выберите вариант сортировки:", reply_markup=get_inline_sort_keyboard("s_ord"))
    await callback.answer()


@dp.message(SearchOrderForm.custom_category)
async def search_order_custom_cat(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(category=message.text, subcategory="ALL", post_type="order")
    await state.set_state(SearchOrderForm.sort_choice)
    await message.answer("Выберите вариант сортировки:", reply_markup=get_inline_sort_keyboard("s_ord"))


@dp.message(F.text == "Искать услугу")
async def start_search_service(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchServiceForm.category)
    await message.answer("Выберите категорию для поиска услуг:",
                         reply_markup=get_inline_categories("s_srv", include_all=True))


@dp.callback_query(F.data.startswith("s_srv_cat_"), SearchServiceForm.category)
async def search_service_cat_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    cat = callback.data.split("_")[3]

    if cat == "ALL":
        await state.update_data(category="ALL", subcategory="ALL", post_type="service")
        await state.set_state(SearchServiceForm.sort_choice)
        await callback.message.edit_text("Выберите вариант сортировки:", reply_markup=get_inline_sort_keyboard("s_srv"))
        await callback.answer()
        return

    if cat == "CUSTOM":
        await state.set_state(SearchServiceForm.custom_category)
        await callback.message.edit_text("Введите название категории:")
        await callback.answer()
        return

    await state.update_data(category=cat, post_type="service")
    await state.set_state(SearchServiceForm.subcategory)
    await callback.message.edit_text("Выберите подкатегорию:",
                                     reply_markup=get_inline_subcategories("s_srv", cat, include_all=True))
    await callback.answer()


@dp.callback_query(F.data.startswith("s_srv_sub_"), SearchServiceForm.subcategory)
async def search_service_subcat_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    sub_val = callback.data.split("_")[3]
    data = await state.get_data()

    if sub_val == "ALL":
        subcat = "ALL"
    elif sub_val == "CUSTOM":
        await state.set_state(SearchServiceForm.custom_category)
        await callback.message.edit_text("Введите подкатегорию вручную:")
        await callback.answer()
        return
    else:
        cat_list = CATEGORIES.get(data.get('category', ''), [])
        subcat = cat_list[int(sub_val)] if sub_val.isdigit() and int(sub_val) < len(cat_list) else "ALL"

    await state.update_data(subcategory=subcat)
    await state.set_state(SearchServiceForm.sort_choice)
    await callback.message.edit_text("Выберите вариант сортировки:", reply_markup=get_inline_sort_keyboard("s_srv"))
    await callback.answer()


@dp.message(SearchServiceForm.custom_category)
async def search_service_custom_cat(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(category=message.text, subcategory="ALL", post_type="service")
    await state.set_state(SearchServiceForm.sort_choice)
    await message.answer("Выберите вариант сортировки:", reply_markup=get_inline_sort_keyboard("s_srv"))


@dp.callback_query(F.data.startswith("s_ord_sort_"), SearchOrderForm.sort_choice)
@dp.callback_query(F.data.startswith("s_srv_sort_"), SearchServiceForm.sort_choice)
async def execute_search_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return

    data = await state.get_data()
    category = data.get('category')
    subcategory = data.get('subcategory')
    post_type = data.get('post_type')
    sort_type = callback.data.split("_")[3]

    order_by = "created_at DESC"
    if sort_type == "cheap":
        order_by = "price ASC"
    elif sort_type == "expensive":
        order_by = "price DESC"

    query_conditions = ["type = ?", "status = 'active'",
                        "user_id NOT IN (SELECT blocked_user_id FROM blocks WHERE user_id = ?)"]
    params = [post_type, callback.from_user.id]

    if category != "ALL":
        query_conditions.append("category = ?")
        params.append(category)

    if subcategory != "ALL" and subcategory is not None:
        query_conditions.append("subcategory = ?")
        params.append(subcategory)

    sql_query = f"""
        SELECT id, user_id, category, subcategory, description, price, created_at, deadline, contact
        FROM posts
        WHERE {" AND ".join(query_conditions)}
        ORDER BY {order_by}
        LIMIT 10
    """

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(sql_query, tuple(params)) as cursor:
            posts = [tuple(r) for r in await cursor.fetchall()]

    await state.clear()
    await callback.message.delete()

    if not posts:
        await callback.message.answer("Объявлений не найдено.", reply_markup=get_main_keyboard(callback.from_user.id))
        await callback.answer()
        return

    await callback.message.answer(f"Результаты поиска ({len(posts)}):",
                                  reply_markup=get_main_keyboard(callback.from_user.id))
    for post in posts:
        post_id, user_id, cat, subcat, desc, price, created_at, deadline, contact = post
        cat_str = f"{cat} -> {subcat}" if subcat else cat
        text = f"📋 **Категория:** {cat_str}\n📝 **Описание:** {desc}\n💰 **Цена:** {price} руб.\n⏳ **Срок:** {deadline}\n📞 **Контакт:** {contact}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Профиль автора", callback_data=f"user_profile_{user_id}")],
            [InlineKeyboardButton(text="⭐️ В избранное", callback_data=f"fav_post_{post_id}")]
        ])
        await callback.message.answer(text, reply_markup=kb)

    await callback.answer()


@dp.message(F.text == "Поиск по @username")
async def start_search_user(message: Message, state: FSMContext) -> None:
    await state.set_state(UsernameSearchForm.username)
    await message.answer("Введите @username пользователя:", reply_markup=get_back_keyboard())


@dp.message(UsernameSearchForm.username)
async def process_search_user(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    username = message.text.replace("@", "").strip()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE username = ?", (username,)) as cursor:
            user = await cursor.fetchone()

    await state.clear()
    if not user:
        await message.answer("Пользователь не найден.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    await send_profile_card(message.from_user.id, user[0], message)


@dp.callback_query(F.data.startswith("user_profile_"))
async def show_user_profile_cb(callback: CallbackQuery) -> None:
    if not callback.data or not isinstance(callback.message, Message):
        return
    target_id = int(callback.data.split("_")[2])
    await send_profile_card(callback.from_user.id, target_id, callback.message)
    await callback.answer()


# ----------------------------------------------------
# ИЗБРАННОЕ И ЗАБЛОКИРОВАННЫЕ (CALLBACKS)
# ----------------------------------------------------
@dp.callback_query(F.data == "btn_favorites")
async def show_favorites_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    async with aiosqlite.connect(DB_NAME) as db:
        query = """
            SELECT p.id, p.category, p.subcategory, p.description, p.price, p.deadline, p.contact
            FROM favorites f
            JOIN posts p ON f.target_id = p.id
            WHERE f.user_id = ? AND f.target_type = 'post' AND p.status = 'active'
        """
        async with db.execute(query, (callback.from_user.id,)) as cursor:
            posts = [tuple(r) for r in await cursor.fetchall()]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="back_to_profile")]])

    if not posts:
        await callback.message.edit_text("Ваш список избранного пуст.", reply_markup=kb)
        await callback.answer()
        return

    await callback.message.edit_text("Избранные объявления:")
    for p in posts:
        post_id, cat, subcat, desc, price, deadline, contact = p
        cat_str = f"{cat} -> {subcat}" if subcat else cat
        text = f"📋 **Категория:** {cat_str}\n📝 **Описание:** {desc}\n💰 **Цена:** {price} руб.\n⏳ **Срок:** {deadline}\n📞 **Контакт:** {contact}"
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data == "btn_blocked")
async def show_blocked_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT b.blocked_user_id, u.username FROM blocks b JOIN users u ON b.blocked_user_id = u.user_id WHERE b.user_id = ?",
                (callback.from_user.id,)
        ) as cursor:
            users = [tuple(r) for r in await cursor.fetchall()]

    kb_back = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="back_to_profile")]])

    if not users:
        await callback.message.edit_text("Список заблокированных пуст.", reply_markup=kb_back)
        await callback.answer()
        return

    await callback.message.edit_text("Заблокированные пользователи:")
    for uid, uname in users:
        kb_item = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Разблокировать", callback_data=f"unblock_{uid}")],
            [InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="back_to_profile")]
        ])
        await callback.message.answer(f"🚫 User ID: {uid} (@{uname or 'без юзернейма'})", reply_markup=kb_item)
    await callback.answer()


@dp.callback_query(F.data.startswith("unblock_"))
async def unblock_user(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    target_id = int(callback.data.split("_")[1])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM blocks WHERE user_id = ? AND blocked_user_id = ?",
                         (callback.from_user.id, target_id))
        await db.commit()
    await callback.answer("Пользователь разблокирован.")


@dp.callback_query(F.data.startswith("fav_post_"))
async def add_fav_post(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    post_id = int(callback.data.split("_")[2])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO favorites (user_id, target_id, target_type) VALUES (?, ?, 'post')",
            (callback.from_user.id, post_id)
        )
        await db.commit()
    await callback.answer("Добавлено в избранное!")


@dp.callback_query(F.data.startswith("fav_user_"))
async def add_fav_user(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    target_user_id = int(callback.data.split("_")[2])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO favorites (user_id, target_id, target_type) VALUES (?, ?, 'user')",
            (callback.from_user.id, target_user_id)
        )
        await db.commit()
    await callback.answer("Пользователь добавлен в избранное!")


@dp.callback_query(F.data.startswith("block_user_"))
async def block_user_callback(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    target_user_id = int(callback.data.split("_")[2])
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO blocks (user_id, blocked_user_id) VALUES (?, ?)",
            (callback.from_user.id, target_user_id)
        )
        await db.commit()
    await callback.answer("Пользователь заблокирован.")


# ----------------------------------------------------
# УВЕДОМЛЕНИЯ И АДМИНКА
# ----------------------------------------------------
@dp.callback_query(F.data == "btn_notifications")
async def manage_notifications_cb(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT category FROM subscriptions WHERE user_id = ?",
                              (callback.from_user.id,)) as cursor:
            subs = [row[0] for row in await cursor.fetchall()]

    buttons = []
    for cat in CATEGORIES.keys():
        status = "✅" if cat in subs else "❌"
        buttons.append([InlineKeyboardButton(text=f"{status} {cat}", callback_data=f"toggle_sub_{cat}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="back_to_profile")])

    await callback.message.edit_text("Настройка подписок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@dp.callback_query(F.data.startswith("toggle_sub_"))
async def toggle_subscription(callback: CallbackQuery) -> None:
    if not callback.data:
        return
    category = callback.data.split("_")[2]
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM subscriptions WHERE user_id = ? AND category = ?",
                              (user_id, category)) as cursor:
            exists = await cursor.fetchone()

        if exists:
            await db.execute("DELETE FROM subscriptions WHERE user_id = ? AND category = ?", (user_id, category))
        else:
            await db.execute("INSERT INTO subscriptions (user_id, category, subcategory) VALUES (?, ?, 'ALL')",
                             (user_id, category))
        await db.commit()

    await callback.answer("Настройки обновлены.")


@dp.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    if message.from_user.id != ADMIN_ID:
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📢 Рассылка")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель администратора:", reply_markup=kb)


@dp.message(F.text == "📊 Статистика")
async def admin_stats(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    if message.from_user.id != ADMIN_ID:
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c1:
            res = await c1.fetchone()
            total_users = res[0] if res else 0

    await message.answer(f"📊 Всего пользователей: {total_users}")


@dp.message(F.text == "📢 Рассылка")
async def admin_broadcast_start(message: Message, state: FSMContext) -> None:
    if not message.from_user or message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminBroadcastForm.text)
    await message.answer("Введите текст сообщения для рассылки:", reply_markup=get_back_keyboard())


@dp.message(AdminBroadcastForm.text)
async def admin_broadcast_execute(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.text:
        return
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            users = [tuple(r) for r in await cursor.fetchall()]

    count = 0
    for u in users:
        try:
            await bot.send_message(u[0], message.text)
            count += 1
        except TelegramAPIError:
            pass

    await state.clear()
    await message.answer(f"Рассылка завершена! Отправлено: {count}",
                         reply_markup=get_main_keyboard(message.from_user.id))


# ----------------------------------------------------
# ЗАПУСК
# ----------------------------------------------------
async def main() -> None:
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
