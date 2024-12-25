import logging, os, json
from telegram import (BotCommand,ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters)

TOKEN = "7858277817:AAGt_RDeo8KcoIpu1ZOXZ8Lm2T7S1aQ9ca0"
app = Application.builder().token(TOKEN).build()
dir_path = os.getcwd()
CHOOSING, IDENTIFICATION, HOW_TO_SET_GOALS,SET_GOALS,SEEK_KNOWLEDGE,CONTACT_US,MAIN_GOAL, SUB_GOALS = range(8)

commands = [
    BotCommand("start",'🤖 تعريف شريك الهمة'),
    BotCommand("learn_how","🤔 كيف أحدّد أهدافي"),
    BotCommand("goal",'📋 تسجيل أهدافي الخاصة'),
    BotCommand("study",'📚 الاطلاع على مسارات طلب العلم'),
    BotCommand("contact",'📥 الاتصال بنا')
]

async def set_command_menu():
    await app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # options=[['تعريف شريك الهمة'],['كيف أحدّد أهدافي'],['تسجيل أهذافي الخاصة'],['الاطلاع على مسارات طلب العلم'],['الاتصال بنا']]
    username = update.message.from_user.username
    projectName = 'شريك الهمّة'

    # keyboard = [
    #     [InlineKeyboardButton('🤖 تعريف شريك الهمة', callback_data='identification')],
    #     [InlineKeyboardButton('🤔 كيف أحدّد أهدافي', callback_data='how_to_set_goals')],
    #     [InlineKeyboardButton('📋 تسجيل أهدافي الخاصة', callback_data='set_goals')],
    #     [InlineKeyboardButton('📚 الاطلاع على مسارات طلب العلم', callback_data='learning_tracks')],
    #     [InlineKeyboardButton('📥 الاتصال بنا', callback_data='contact_us')]
    # ]
    
    # reply_markup = InlineKeyboardMarkup(keyboard)

    keyboard = [
        [InlineKeyboardButton('🤖 تعريف شريك الهمة')],
        [InlineKeyboardButton('🤔 كيف أحدّد أهدافي')],
        [InlineKeyboardButton('📋 تسجيل أهدافي الخاصة')],
        [InlineKeyboardButton('📚 الاطلاع على مسارات طلب العلم')],
        [InlineKeyboardButton('📥 الاتصال بنا')]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(
     f'🌹السلام عليكم <b>{username}</b>\n'
     '\n'
     f'مرحباً بكم معنا في <b>{projectName}</b> رفيقكم في تحقيق أهدافكم وشريككم نحو مستوى وعي أرقى 🍃\n'
     '\n'
     ' اختر(ي) طلبك من القائمة أسفله واستعن بالله ولا تعجز✔️'
     '\n',
     parse_mode='HTML',
     reply_markup=reply_markup,
    )
    return CHOOSING

# async def choosing(update: Update,context: ContextTypes.DEFAULT_TYPE):
#     if 
async def handle_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data == 'identification':
        await identification(update, context)
    elif callback_data == 'how_to_set_goals':
        await how_to_set_goals(update, context)
    elif callback_data == 'set_goals':
        await set_goals(update, context)
        # return MAIN_GOAL
    elif callback_data == 'learning_tracks':
        await learning_tracks(update, context)
    elif callback_data == 'contact_us':
        await contact_us(update, context)
    elif callback_data == 'main_goal_req':
        await main_goal_req(update, context)
    elif callback_data == 'sub_goal_req':
        await main_goal_req(update, context)
    else:   
        await handle_default(update, context)

async def identification(update, context):
    file_path = os.path.join(dir_path,'text-files/introduction.txt')
    with open(file_path, 'r', encoding='utf-8') as welcome_file:
        file_data = welcome_file.read()
    await update.message.reply_text(file_data.replace('\n', '\n'), parse_mode='HTML')

async def how_to_set_goals(update, context):
    #  await update.callback_query.answer(text="الملف في طريقه...")
     pdf_path = os.path.join(dir_path, 'pdf-files/numPDF1.pdf')
     with open(pdf_path, 'rb') as pdf_file:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_file,
            filename="طريقة تحديد الأهداف.pdf",
            caption="اقرأ الملف بتمعّن ولا تتردد في السؤال📑"
        )

async def set_goals(update, context):
    await update.message.reply_text(
    'تم اختيار: <b>تسجيل أهدافي الخاصة📋</b>\n'
    '\n'
    'المرجو كتابة الهدف الرئيسي وإرساله، ومتابعة ذلك بالأهداف الفرعية\n'
    'مثال ذلك كما يلي🍃: \n\n'
    '<blockquote><b>تحديد الهدف الرئيسي 👇</b></blockquote> \n'
    'بداية اكتساب مهارة القراءة\n\n'
    '<blockquote>قم بعملية الإرسال ✅</blockquote>\n\n'
    '<blockquote><b>تحديد الأهداف الفرعية</b></blockquote> \n'
    'اختيار الكتب\n\n'
    '<blockquote>قم بعملية الإرسال ✅</blockquote>\n\n'
    '<blockquote><b>تحديد الأهداف الفرعية</b></blockquote> \n'
    'تخصيص مفكرة للتفريغ\n\n'
    '<blockquote>قم بعملية الإرسال ✅</blockquote>\n\n'
    '<blockquote><b>تحديد الأهداف الفرعية</b></blockquote> \n'
    'ساعة قراءة يوميا\n\n'
    '<blockquote>قم بعملية الإرسال ✅</blockquote>',
    parse_mode='HTML'
    )
    # return MAIN_GOAL

    # await update.callback_query.message.reply_text(
    #     'تفضل(ي) 🤩',  # This is the required 'text' argument
    #     parse_mode='HTML'
    #     # reply_markup=InlineKeyboardMarkup(
    #     #     [[InlineKeyboardButton('اضغط هنا لإرسال الهدف الرئيسي 🎯', callback_data='main_goal_req')]]
    #     # )
    # )
    
    # # context.user_data['current_state'] = MAIN_GOAL 
    await update.callback_query.answer()  # Acknowledge the callback query

    await update.message.reply_text(
    'تفضل(ي) 🤩',
    parse_mode='HTML'
    )
    return MAIN_GOAL
    # Transition to MAIN_GOAL state
    # context.user_data['current_state'] = MAIN_GOAL

async def main_goal_req(update, context):
    # print("Main goal state activated")
    context.user_data['main_goal'] = update.message.text
    await update.message.reply_text('main_goal_req')
    await update.message.reply_text('hello')
    # print('SUB GOALS IS PRINTED')
    return SUB_GOALS

async def sub_goal_req(update, context):
    context.user_data['sub_goals'] = update.message.text
    await update.message.reply_text('sub_goals')
    
async def handle_user_input(update, context):
    user_response = update.message.text
    if user_response == '📋 تسجيل أهدافي الخاصة':
        await update.message.reply_text('hello')
        return MAIN_GOAL
    
async def learning_tracks(update, context):
    await update.callback_query.message.reply_text('مسارات')
async def contact_us(update, context):
    await update.callback_query.message.reply_text('اتصل بنا')
async def handle_default(update, context):
    await update.callback_query.message.reply_text('التلقائي')
async def cancel(update, context):
    await update.callback_query.message.reply_text('Canceled')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    # Optionally, send a message to the user when an error occurs
    if update.effective_chat:
        await update.effective_chat.send_message(text="حدث خطأ ما X__X")

async def handle_input(update, context):
    print("hello")
    user_input = update.message.text
    if user_input == "🤖 تعريف شريك الهمة":
        await identification(update, context)
    elif user_input == "🤔 كيف أحدّد أهدافي":
        await how_to_set_goals(update, context)
    elif user_input == "📋 تسجيل أهدافي الخاصة":
        await set_goals(update, context)
    elif user_input == "📚 الاطلاع على مسارات طلب العلم":
       await learning_tracks(update, context)
    elif user_input == "📥 الاتصال بنا":
        await contact_us(update, context)

def main():
        
    convo_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        # CHOOSING: [MessageHandler(filters.Regex("^(🤖 تعريف شريك الهمة|🤔 كيف أحدّد أهدافي|📚 الاطلاع على مسارات طلب العلم|📥 الاتصال بنا)$"), handle_input)],
        # IDENTIFICATION: [MessageHandler(filters.TEXT,identification)],
        # HOW_TO_SET_GOALS: [MessageHandler(filters.TEXT,how_to_set_goals)],
        # SET_GOALS: [MessageHandler(filters.TEXT,set_goals)],
        # SEEK_KNOWLEDGE: [MessageHandler(filters.TEXT,learning_tracks)],
        MAIN_GOAL: [MessageHandler(filters.TEXT,main_goal_req)],
        SUB_GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sub_goal_req)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(convo_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_user_messages))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    app.add_error_handler(error_handler)
    app.run_polling()
    
if __name__ == "__main__":
    main()