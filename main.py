import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

BOT_TOKEN = "8752246289:AAH484uHVY_r-e0fC3vZ7XZ19H2TgO-qUeI"
ADMIN_ID = 995387118

# Человекочитаемые подписи для админки
BOT_TYPE_LABELS = {"shop": "🤖 Магазин", "chat": "💬 Чат-бот", "auto": "📊 Автоматизация", "other": "🧩 Другое"}
BUDGET_LABELS = {"b1": "💸 До 100$", "b2": "💰 100–300$", "b3": "💎 300–1000$", "b4": "🚀 1000$+"}
TIMELINE_LABELS = {"t1": "⚡ Срочно (1-3 дня)", "t2": "⏱️ До недели", "t3": "🗓️ До месяца"}
GOAL_LABELS = {"g1": "💰 Продажи", "g2": "🛎 Поддержка", "g3": "📅 Запись", "g4": "⚙️ Автоматизация"}

AUDIENCE_LABELS = {
    "aud_b2b": "👨‍💼 B2B",
    "aud_b2c": "🧑‍🤝‍🧑 B2C",
    "aud_mass": "🌍 Широкая аудитория"
}
FUNCTIONALITY_LABELS = {
    "func_catalog": "📦 Каталог + заявки",
    "func_booking": "📅 Запись/бронь",
    "func_support": "💬 FAQ + поддержка",
    "func_advanced": "🧠 Сложная логика"
}
UX_LABELS = {"ux_min": "🟢 Минималистичный", "ux_std": "🔵 Стандартный", "ux_pro": "🟣 Премиум"}
TONE_LABELS = {
    "tone_formal": "👔 Официальный",
    "tone_friendly": "😊 Дружелюбный",
    "tone_fun": "😎 Неформальный"
}
YES_NO_LABELS = {
    "content_yes": "✅ Да", "content_no": "❌ Нет",
    "int_yes": "✅ Да", "int_no": "❌ Нет",
    "db_yes": "✅ Да", "db_no": "❌ Нет",
    "sup_yes": "✅ Да", "sup_no": "❌ Нет",
}

# Новые значения
BOT_TYPE_VALUES = {"shop", "chat", "auto", "other"}
BUDGET_VALUES = {"b1", "b2", "b3", "b4"}
TIMELINE_VALUES = {"t1", "t2", "t3"}
GOAL_VALUES = {"g1", "g2", "g3", "g4"}

def audience_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💼 B2B", callback_data="aud_b2b")],
        [InlineKeyboardButton(text="🧑‍🤝‍🧑 B2C", callback_data="aud_b2c")],
        [InlineKeyboardButton(text="🌍 Широкая аудитория", callback_data="aud_mass")]
    ])

def functionality_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Каталог + заявки", callback_data="func_catalog")],
        [InlineKeyboardButton(text="📅 Запись/бронь", callback_data="func_booking")],
        [InlineKeyboardButton(text="💬 FAQ + поддержка", callback_data="func_support")],
        [InlineKeyboardButton(text="🧠 Сложная логика", callback_data="func_advanced")]
    ])

def ux_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Минималистичный", callback_data="ux_min")],
        [InlineKeyboardButton(text="🔵 Стандартный", callback_data="ux_std")],
        [InlineKeyboardButton(text="🟣 Премиум", callback_data="ux_pro")]
    ])

def pretty(data: dict, key: str, labels: dict) -> str:
    value = data.get(key, "—")
    return labels.get(value, value)

async def edit_or_send(call: CallbackQuery, text: str, kb: InlineKeyboardMarkup | None = None):
    if isinstance(call.message, Message):
        await call.message.edit_text(text, reply_markup=kb)
    else:
        await bot.send_message(call.from_user.id, text, reply_markup=kb)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    contact = State()
    bot_type = State()
    budget = State()
    timeline = State()
    goal = State()
    audience = State()
    functionality = State()
    content = State()
    integrations = State()
    storage = State()
    ux = State()
    tone = State()      # <-- новый шаг
    support = State()

# ---------- КНОПКИ ----------

def bot_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Магазин", callback_data="shop")],
        [InlineKeyboardButton(text="💬 Чат-бот", callback_data="chat")],
        [InlineKeyboardButton(text="📊 Автоматизация", callback_data="auto")],
        [InlineKeyboardButton(text="🧩 Другое", callback_data="other")]
    ])

def budget_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 До 100$", callback_data="b1")],
        [InlineKeyboardButton(text="💰 100–300$", callback_data="b2")],
        [InlineKeyboardButton(text="💎 300–1000$", callback_data="b3")],
        [InlineKeyboardButton(text="🚀 1000$+", callback_data="b4")]
    ])

def timeline_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Срочно (1-3 дня)", callback_data="t1")],
        [InlineKeyboardButton(text="⏱️ До недели", callback_data="t2")],
        [InlineKeyboardButton(text="🗓️ До месяца", callback_data="t3")]
    ])

def goal_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Продажи", callback_data="g1")],
        [InlineKeyboardButton(text="🛎 Поддержка", callback_data="g2")],
        [InlineKeyboardButton(text="📅 Запись", callback_data="g3")],
        [InlineKeyboardButton(text="⚙️ Автоматизация", callback_data="g4")]
    ])

def yes_no_kb(prefix):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data=f"{prefix}_yes")],
        [InlineKeyboardButton(text="❌ Нет", callback_data=f"{prefix}_no")]
    ])

def tone_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👔 Официальный", callback_data="tone_formal")],
        [InlineKeyboardButton(text="😊 Дружелюбный", callback_data="tone_friendly")],
        [InlineKeyboardButton(text="😎 Неформальный", callback_data="tone_fun")]
    ])

async def safe_delete_message(msg: Message):
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

# --- NEW FUNCTIONS ADDED --- #
def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться номером", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def with_back(kb: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=kb.inline_keyboard + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )

def question_for(state_name: str | None) -> tuple[str, InlineKeyboardMarkup]:
    if state_name == Form.bot_type.state:
        return "1/10 • Какой бот нужен?", with_back(bot_type_kb())
    if state_name == Form.budget.state:
        return "2/10 • Выбери бюджет:", with_back(budget_kb())
    if state_name == Form.timeline.state:
        return "3/10 • Сроки запуска:", with_back(timeline_kb())
    if state_name == Form.goal.state:
        return "4/10 • Главная цель бота:", with_back(goal_kb())
    if state_name == Form.audience.state:
        return "5/10 • Целевая аудитория:", with_back(audience_kb())
    if state_name == Form.functionality.state:
        return "6/10 • Основной функционал:", with_back(functionality_kb())
    if state_name == Form.content.state:
        return "7/10 • Есть готовый контент?", with_back(yes_no_kb("content"))
    if state_name == Form.integrations.state:
        return "8/10 • Нужны интеграции?", with_back(yes_no_kb("int"))
    if state_name == Form.storage.state:
        return "9/10 • Нужно хранение данных?", with_back(yes_no_kb("db"))
    if state_name == Form.ux.state:
        return "10/10 • Какой UX предпочитаешь?", with_back(ux_kb())
    if state_name == Form.tone.state:
        return "Характер общения бота:", with_back(tone_kb())

    return "Нужна поддержка после запуска?", with_back(yes_no_kb("sup"))
# -------------------------------- #

# ---------- ЛОГИКА ----------

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Укажи контакт (нажми кнопку ниже):", reply_markup=phone_kb())
    await state.set_state(Form.contact)

@dp.message(Form.contact, F.contact)
async def get_contact(message: Message, state: FSMContext):
    if message.contact is None:
        await message.answer("Пожалуйста, отправь контакт кнопкой ниже.", reply_markup=phone_kb())
        return

    username = f"@{message.from_user.username}" if message.from_user and message.from_user.username else "Нет"
    await state.update_data(
        contact=message.contact.phone_number,
        username=username
    )
    await message.answer("✅ Номер получен", reply_markup=ReplyKeyboardRemove())
    text, kb = question_for(Form.bot_type.state)
    await message.answer(text, reply_markup=kb)
    await state.set_state(Form.bot_type)

@dp.message(Form.contact)
async def get_contact_text_fallback(message: Message):
    await message.answer("Пожалуйста, нажми кнопку «📱 Поделиться номером».", reply_markup=phone_kb())

# --- Updated handlers using question_for --- #

@dp.callback_query(F.data == "back")
async def go_back(call: CallbackQuery, state: FSMContext):
    await call.answer()

    current_state = await state.get_state()

    state_order = [
        Form.bot_type.state,
        Form.budget.state,
        Form.timeline.state,
        Form.goal.state,
        Form.audience.state,
        Form.functionality.state,
        Form.content.state,
        Form.integrations.state,
        Form.storage.state,
        Form.ux.state,
        Form.tone.state,
        Form.support.state,
    ]

    if current_state not in state_order:
        return

    idx = state_order.index(current_state)
    if idx == 0:
        await state.set_state(Form.contact)
        await bot.send_message(call.from_user.id, "Укажи контакт (нажми кнопку ниже):", reply_markup=phone_kb())
        return

    prev_state = state_order[idx - 1]
    await state.set_state(prev_state)
    text, kb = question_for(prev_state)
    await edit_or_send(call, text, kb)

@dp.callback_query(Form.bot_type, F.data.in_(BOT_TYPE_VALUES))
async def get_bot_type(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(bot_type=call.data)
    text, kb = question_for(Form.budget.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.budget)

@dp.callback_query(Form.budget, F.data.in_(BUDGET_VALUES))
async def get_budget(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(budget=call.data)
    text, kb = question_for(Form.timeline.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.timeline)

@dp.callback_query(Form.timeline, F.data.in_(TIMELINE_VALUES))
async def get_timeline(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(timeline=call.data)
    text, kb = question_for(Form.goal.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.goal)

@dp.callback_query(Form.goal, F.data.in_(GOAL_VALUES))
async def get_goal(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(goal=call.data)
    text, kb = question_for(Form.audience.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.audience)

@dp.callback_query(Form.audience, F.data.startswith("aud_"))
async def get_audience(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(audience=call.data)
    text, kb = question_for(Form.functionality.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.functionality)

@dp.callback_query(Form.functionality, F.data.startswith("func_"))
async def get_functionality(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(functionality=call.data)
    text, kb = question_for(Form.content.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.content)

@dp.callback_query(Form.content, F.data.startswith("content_"))
async def get_content(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(content=call.data)
    text, kb = question_for(Form.integrations.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.integrations)

@dp.callback_query(Form.integrations, F.data.startswith("int_"))
async def get_integrations(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(integrations=call.data)
    text, kb = question_for(Form.storage.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.storage)

@dp.callback_query(Form.storage, F.data.startswith("db_"))
async def get_storage(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(storage=call.data)
    text, kb = question_for(Form.ux.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.ux)

@dp.callback_query(Form.ux, F.data.startswith("ux_"))
async def get_ux(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(ux=call.data)
    text, kb = question_for(Form.tone.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.tone)

@dp.callback_query(Form.tone, F.data.startswith("tone_"))
async def get_tone(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(tone=call.data)
    text, kb = question_for(Form.support.state)
    await edit_or_send(call, text, kb)
    await state.set_state(Form.support)

@dp.callback_query(Form.support, F.data.startswith("sup_"))
async def finish(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(support=call.data)
    data = await state.get_data()

    text = (
        "📥 Новая анкета:\n\n"
        f"👤 Имя: {data.get('name', '—')}\n"
        f"🔗 Username: {data.get('username', '—')}\n"
        f"📱 Контакт: {data.get('contact', '—')}\n"
        f"🤖 Тип: {pretty(data, 'bot_type', BOT_TYPE_LABELS)}\n"
        f"💰 Бюджет: {pretty(data, 'budget', BUDGET_LABELS)}\n"
        f"🗓️ Сроки: {pretty(data, 'timeline', TIMELINE_LABELS)}\n"
        f"🎯 Цель: {pretty(data, 'goal', GOAL_LABELS)}\n"
        f"👥 Аудитория: {pretty(data, 'audience', AUDIENCE_LABELS)}\n"
        f"⚙️ Функционал: {pretty(data, 'functionality', FUNCTIONALITY_LABELS)}\n"
        f"📝 Контент: {pretty(data, 'content', YES_NO_LABELS)}\n"
        f"🔌 Интеграции: {pretty(data, 'integrations', YES_NO_LABELS)}\n"
        f"🗄️ Хранение данных: {pretty(data, 'storage', YES_NO_LABELS)}\n"
        f"✨ UX: {pretty(data, 'ux', UX_LABELS)}\n"
        f"🗣️ Характер бота: {pretty(data, 'tone', TONE_LABELS)}\n"
        f"🛠️ Поддержка: {pretty(data, 'support', YES_NO_LABELS)}"
    )

    try:
        await bot.send_message(ADMIN_ID, text)
    except TelegramBadRequest as e:
        await bot.send_message(
            call.from_user.id,
            "⚠️ Заявка принята, но не удалось отправить администратору. Напишите /start админу и проверьте ADMIN_ID."
        )
        print(f"[ADMIN SEND ERROR] ADMIN_ID={ADMIN_ID}, error={e}")

    await edit_or_send(call, "✅ Спасибо! Заявка отправлена. Я свяжусь с вами 🚀")
    await state.clear()

# --- NEW COMMAND HANDLER ---

@dp.message(Command("myid"))
async def my_id(message: Message):
    if message.from_user is None:
        await message.answer("Не удалось определить ID пользователя.")
        return

    await message.answer(f"Ваш ID: {message.from_user.id}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())