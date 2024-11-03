import random
import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
# Применение nest_asyncio
nest_asyncio.apply()
# Словарь с картами Таро и их описаниями
tarot_cards = {
    "0": ("Дурак", "Новые начинания, свобода, спонтанность.",
          "Дурак символизирует новые начинания и возможность исследовать мир с открытым сердцем. Он призывает вас следовать своим инстинктам и не бояться рисковать."),
    "I": ("Маг", "Мастерство, умение, ресурсность.",
          "Маг представляет собой силу воли и мастерство. Он напоминает вам о ваших талантах и о том, как вы можете использовать их для достижения своих целей."),
    "II": ("Жрица", "Интуиция, тайны, женская мудрость.",
           "Жрица символизирует интуицию и внутреннее понимание. Она призывает вас полагаться на свои чувства и инстинкты, а также искать знания в тишине."),
    "III": ("Императрица", "Плодородие, природа, изобилие.",
            "Императрица символизирует изобилие, материнство и заботу. Она олицетворяет природу и плодородие."),
    "IV": ("Император", "Структура, власть, руководство.",
            "Император символизирует порядок и стабильность. Это карта авторитета и контроля."),
    "V": ("Иерофант", "Традиция, духовность, учение.",
           "Иерофант олицетворяет традиции и духовные поиски. Он призывает вас обратиться к своему внутреннему я."),
    "VI": ("Влюбленные", "Любовь, гармония, партнерство.",
            "Влюбленные представляют собой связь и гармонию. Эта карта говорит о важности выборов в любви."),
    "VII": ("Колесница", "Победа, управление, воля.",
             "Колесница символизирует победу и уверенность. Вы управляете своей судьбой и успехом."),
    "VIII": ("Сила", "Смелость, уверенность, сострадание.",
             "Сила олицетворяет внутреннюю силу и смелость. Это призыв использовать сострадание."),
    "IX": ("Отшельник", "Поиск истины, внутренний мир.",
            "Отшельник представляет поиск внутренней истины. Это время для саморазмышления."),
    "X": ("Колесо Фортуны", "Циклы, изменения, судьба.",
           "Колесо Фортуны символизирует изменения и циклы жизни. Будьте готовы к неожиданному."),
    "XI": ("Справедливость", "Баланс, равновесие, честность.",
            "Справедливость олицетворяет баланс и правильные решения. Это призыв учитывать последствия."),
    "XII": ("Повешенный", "Смена перспектив, жертва.",
            "Повешенный говорит о необходимости жертвы ради большего блага. Посмотрите на ситуацию с новой точки зрения."),
    "XIII": ("Смерть", "Конец, трансформация, новое начало.",
             "Смерть символизирует завершение одного периода и начало нового. Это путь к трансформации."),
    "XIV": ("Умеренность", "Баланс, терпение, гармония.",
             "Умеренность призывает к умеренности и гармонии. Это карта баланса в действиях."),
    "XV": ("Дьявол", "Привязанности, материализм, иллюзия.",
            "Дьявол символизирует зависимости и негативные влияния. Будьте внимательны к материализму."),
    "XVI": ("Башня", "Разрушение, изменения, освобождение.",
            "Башня говорит о резких переменах, которые могут привести к освобождению от старого."),
    "XVII": ("Звезда", "Надежда, вдохновение, спокойствие.",
             "Звезда символизирует надежду и вдохновение. Ощувствуйте светлое будущее."),
    "XVIII": ("Луна", "Сны, интуиция, обман.",
               "Луна олицетворяет тайны и интуицию. Будьте осторожны с иллюзиями."),
    "XIX": ("Солнце", "Радость, успех, жизненная сила.",
             "Солнце символизирует радость и успех. Это время для оптимизма и положительного мышления."),
    "XX": ("Суд", "Восхождение, обновление, прощение.",
            "Суд олицетворяет обновление и возрождение. Это время для самоанализов и новых начинаний."),
    "XXI": ("Мир", "Завершение, единство, успех.",
             "Мир символизирует завершение и гармонию. Вы достигли своих целей.")
}
# Список нежелательных слов и вопросов
banned_words = ["дурак", "ты", "завтра", "что будет", "если"]
banned_questions = ["Как стать богатым?", "Когда я умру?", "Напиши мне будущее."]

# Определим состояния
CHOOSING, QUESTIONING = range(2)
# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Получить расклад на любовь", "Получить расклад на карьеру"],
        ["Получить расклад на здоровье", "Общий расклад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать в Бота Таро!🃏\nВыберите расклад:", reply_markup=reply_markup)
    return CHOOSING

# Обработка выбора расклада
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text.strip()
    context.user_data['chosen_type'] = user_choice  # Сохраним выбор в контексте
    await update.message.reply_text("Отлично! Пожалуйста, задайте правильный вопрос:")
    return QUESTIONING

# Обработка вопросов от пользователей
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.strip()
    selected_cards = random.sample(list(tarot_cards.items()), 3)

    # Проверка на наличие запрещенных слов
    if any(banned_word in user_question for banned_word in banned_words):
        await update.message.reply_text("Ваш вопрос содержит недопустимые слова. Пожалуйста, задайте другой вопрос.")
        return QUESTIONING

    # Проверка на наличие нежелательных вопросов
    if user_question in banned_questions:
        await update.message.reply_text("Ваш вопрос не может быть обработан. Пожалуйста, задайте другой вопрос.")
        return QUESTIONING

    selected_cards = random.sample(list(tarot_cards.items()), 3)

    result = "Ваш расклад:\n\n"

    for card_num, (card_name, short_desc, full_desc) in selected_cards:
        result += f"{card_name} ({card_num}): {short_desc}\nПолное описание: {full_desc}\n\n"

    interpretation = interpret_draw(selected_cards)
    result += "Логическое решение вопроса: " + interpretation

    # Кнопки для выбора расклада
    keyboard = [
        ["Получить расклад на любовь", "Получить расклад на карьеру"],
        ["Получить расклад на здоровье", "Общий расклад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(result, reply_markup=reply_markup)
    return CHOOSING  # Возвращаем в состояние выбора расклада
# Интерпретация расклада
def interpret_draw(selected_cards):
    interpretations = []
    for card_num, (card_name, short_desc, full_desc) in selected_cards:
        interpretations.append(full_desc)
    return " ".join(interpretations)

# Основная функция
async def main():
    application = ApplicationBuilder().token('7884607985:AAER00ZtUz6U8AAmRGLdL8jIgls6ma7mw1M').build()

    # Настройка обработчика разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_type)],
            QUESTIONING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    # Запустить приложение
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())