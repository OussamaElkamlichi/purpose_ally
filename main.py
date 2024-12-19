from datetime import datetime
import logging
import os
import json
import requests
from dotenv import load_dotenv
from telegram import (BotCommand, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)
from classes.userGoals import UserGoals
from telegram.error import BadRequest
from dbAgent.agent import essential_seed, show_demo_db, edit_prep, updateGoal, cron_seed
TOKEN = "7858277817:AAGt_RDeo8KcoIpu1ZOXZ8Lm2T7S1aQ9ca0"
app = Application.builder().token(TOKEN).build()
dir_path = os.getcwd()
IDENTIFICATION, HOW_TO_SET_GOALS, SET_GOALS, SEEK_KNOWLEDGE, CONTACT_US, MAIN_GOAL, SUB_GOALS, EDIT_GOAL, SET_CRON, SET_CRON_TIME, SET_CRON_WEEKDAY , EDIT_CRON_TIME, VALIDATE_CRON= range(
    13)

commands = [
    BotCommand("start", '🤖 تعريف شريك الهمة'),
    BotCommand("learn_how", "🤔 كيف أحدّد أهدافي"),
    BotCommand("goal", '📋 تسجيل أهدافي الخاصة'),
    BotCommand("study", '📚 الاطلاع على مسارات طلب العلم'),
    BotCommand("contact", '📥 الاتصال بنا')
]


async def set_command_menu():
    await app.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user_type = update.message.chat.type
    course_id = 0
    result = essential_seed(username, user_id, user_type, course_id)
    message = result.get("message", "An error occurred.")
    reply_markup = result.get("reply_markup")
    if message not in ["don't send", "Error: Unread result found"]:
        await update.message.reply_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup,
        )

    projectName = 'شريك الهمّة'
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{result}\nWelcome to {projectName}!")

    keyboard = [
        [InlineKeyboardButton('🤖 تعريف شريك الهمة',
                              callback_data='identification')],
        [InlineKeyboardButton('🤔 كيف أحدّد أهدافي',
                              callback_data='how_to_set_goals')],
        [InlineKeyboardButton('📋 تسجيل أهدافي الخاصة',
                              callback_data='set_goals')],
        [InlineKeyboardButton('📚 الاطلاع على مسارات طلب العلم',
                              callback_data='learning_tracks')],
        [InlineKeyboardButton('📥 الاتصال بنا', callback_data='contact_us')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

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



async def identification(update, context):

    file_path = os.path.join(dir_path, 'text-files/introduction.txt')
    with open(file_path, 'r', encoding='utf-8') as welcome_file:
        file_data = welcome_file.read()
    await update.callback_query.message.reply_text(file_data.replace('\n', '\n'), parse_mode='HTML')


async def how_to_set_goals(update, context):
    await update.callback_query.answer(text="الملف في طريقه...")
    pdf_path = os.path.join(dir_path, 'pdf-files/numPDF1.pdf')
    with open(pdf_path, 'rb') as pdf_file:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_file,
            filename="طريقة تحديد الأهداف.pdf",
            caption="اقرأ الملف بتمعّن ولا تتردد في السؤال📑"
        )


async def set_goals(update, context):

    await update.callback_query.edit_message_text(
        text='تم اختيار: <b>تسجيل أهدافي الخاصة📋</b>\n'
             '\n'
             'المرجو كتابة الهدف الرئيسي وإرساله، ومتابعة <b>الإرشادات</b>\n\n'
             'تفضل(ي) 🍃🖋️',
        parse_mode='HTML'
    )

    return MAIN_GOAL


async def main_goal_req(update, context):
    user_id = update.message.from_user.id
    main_goal = update.message.text

    # Store user data in context.user_data using user_id as a key
    if user_id not in context.user_data:
        context.user_data[user_id] = UserGoals(user_id)

    # Store the main goal in the user's goal data
    context.user_data[user_id].add_main_goal(user_id, main_goal)

    await update.message.reply_text(
        'تم تسجيل الهدف الرئيسي تحت عنوان:\n\n'
        f"<blockquote>{main_goal}</blockquote>\n\n"
        ' <b>تفضل(ي)</b> بتحديد الهدف الفرعي \n\n',
        parse_mode='HTML'
    )
    # Store main goal in user_data for later reference
    context.user_data[user_id].current_main_goal = main_goal

    return SUB_GOALS


async def sub_goal_req(update, context):
    user_id = update.message.from_user.id
    sub_goal = update.message.text

    if user_id not in context.user_data:
        await update.message.reply_text("يبدو أنك لم تحدد هدفًا رئيسيًا بعد. يرجى البدء بتحديد هدفك الرئيسي.")
        return ConversationHandler.END

    if sub_goal.lower() in ["انتهاء", "إنتهاء", "done"]:
        goals_count = context.user_data[user_id].goals_count()
        if len(goals_count.keys()) < 2:
            # Inform user they need at least two goals
            await update.message.reply_text(
                'المرجو تحديد هدفين رئيسيين على الأقل.\n'
                'اكتب(ي) "آخر" لإضافة هدف رئيسي جديد.'
            )
            return SUB_GOALS  # Stay in the same state and avoid sending the next message
        else:
            # Proceed to end the input if goals count is sufficient
            goals_seed = context.user_data[user_id].launch(user_id)
            keyboard = [[InlineKeyboardButton(
                "كيف ستبدو أهدافك؟", callback_data="show_demo")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                '<blockquote>تم إنهاء الإدخال 🎉</blockquote>\n',
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            return ConversationHandler.END
    elif sub_goal.lower() in ["آخر", "اخر"]:
        # Handle adding a new main goal
        await update.message.reply_text(
            'تفضل(ي) بتحديد الهدف الرئيسي الآخر📝\n',
            parse_mode='HTML'
        )
        return MAIN_GOAL

    # Otherwise, add the sub-goal under the current main goal
    main_goal = context.user_data[user_id].current_main_goal
    context.user_data[user_id].add_sub_goal(user_id, main_goal, sub_goal)

    # Only send the confirmation message when a sub-goal is added successfully
    await update.message.reply_text(
        'تم تسجيل الهدف الفرعي تحت عنوان:\n'
        f"<blockquote>{sub_goal}</blockquote>\n"
        'الأهداف الحالية:\n'
        f"{context.user_data[user_id].get_goals_list()}\n\n"
        'اكتب(ي) "انتهاء" لإنهاء الإدخال\n'
        'أكتب(ي) "آخر" من أجل إضافة هدف رئيسي آخر',
        parse_mode='HTML'
    )

    return SUB_GOALS


async def show_demo(update, context):
    user_id = update.callback_query.from_user.id
    goals_list = show_demo_db(user_id)
    main_goals = list(goals_list.keys())  # Collect all main goals as options

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question="سجّل مهامك اليومية أثابك الله",
        options=main_goals,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    keyboard = [
        [InlineKeyboardButton("تعديل نص الأهداف", callback_data="edit_op")],
        [InlineKeyboardButton("تحديد وقت إرسال المهمات",
                              callback_data="set_cron_opt_call")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        '<blockquote>استعن بالله ولا تعجز 🍃</blockquote>\n',
        reply_markup=reply_markup,
        parse_mode='HTML'
    )



async def edit_op(update, context):
    user_id = update.callback_query.from_user.id
    goals_list = edit_prep(user_id)

    keyboard = [
        [InlineKeyboardButton(
            goal["text"], callback_data=f'{goal["type"]}***{goal["id"]}***{goal["text"]}')]
        for goal in goals_list
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        '<blockquote>اختر ما تريد تعديله</blockquote>\n',
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def edit_goal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if "***" in query.data:
        goal_type, goal_id, goal_text = query.data.split("***")
        context.user_data['goal_type'] = goal_type
        context.user_data['goal_id'] = goal_id
        context.user_data['old_goal_text'] = goal_text

        await query.edit_message_text(
            f'<blockquote>تم اختيار 🎯</blockquote>\n{goal_text}\n'
            '<b>أكتب نص الهدف الصحيح</b>',
            parse_mode='HTML'
        )
        return EDIT_GOAL


async def edit_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    new_goal_text = update.message.text
    goal_type = context.user_data.get('goal_type')
    goal_id = context.user_data.get('goal_id')
    old_goal_text = context.user_data.get('old_goal_text')

    result = updateGoal(update.message.from_user.id,
                        new_goal_text, goal_type, goal_id, old_goal_text)
    await update.message.reply_text(result, parse_mode='HTML')

    return ConversationHandler.END


async def set_cron_opt(update, context):
    keyboard = [
        [InlineKeyboardButton("يوميًا", callback_data="cronOption:daily")],
        # [InlineKeyboardButton(
        #     "أسبوعيًا", callback_data="cronOption:weekly")],
        # [InlineKeyboardButton("تخصيص", callback_data="cronOption:custom")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        '<blockquote>تحديد وقت الإرسال  ⏲️</blockquote>\n',
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return SET_CRON


async def set_cron(update, context):
    selected_option = update.callback_query.data.split(":")[1]
    if selected_option == "daily":
        await update.callback_query.message.reply_text(
            text="<blockquote>أكتب الساعة والدقيقة التي تُريد</blockquote><b>مثال: 22:30</b>",
            parse_mode="HTML"
        )
        cron_type = context.user_data['cron_settings'] = "daily"
        return SET_CRON_TIME
    elif selected_option == "weekly":
        days_of_week = [
            "الأحد",  # Sunday
            "الإثنين",  # Monday
            "الثلاثاء",  # Tuesday
            "الأربعاء",  # Wednesday
            "الخميس",  # Thursday
            "الجمعة",  # Friday
            "السبت"  # Saturday
        ]
        keyboard = [InlineKeyboardButton(
            day, callback_data="weekday") for day in days_of_week]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "اختر اليوم الذي تريد تحديده للموعد الأسبوعي:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return SET_CRON_WEEKDAY

    elif selected_option == "custom":
        await update.callback_query.message.reply_text("تم تحديد الإرسال حسب التخصيص.")
    else:
        await update.callback_query.message.reply_text("خيارات غير معروفة.")


async def set_cron_time(update, context):
    keyboard = [[  InlineKeyboardButton("تعديل", callback_data="edit_cron_launch")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    time = update.message.text
    user_id = update.message.from_user.id
    cron_type = context.user_data.get('cron_settings')
    res = cron_seed(user_id, cron_type, time)
    if res == True:
        await update.message.reply_text(
        "<blockquote>تم تحديد وقت الإرسال ⏰</blockquote>\n"
        f"<b>يومياً على الساعة:  {time}</b> ",
        reply_markup=reply_markup,
        parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
        "<blockquote>لا يمكن تحديد التوقيت</blockquote>\n"
        f"<b>خطأ داخلي</b> ",
        reply_markup=reply_markup,
        parse_mode='HTML'
        )
    return ConversationHandler.END

async def edit_cron(update, context):
    await update.callback_query.message.reply_text(
    "المرجو كتابة التوقيت بدقّة (مثال: 06:00)"
    )
    return EDIT_CRON_TIME

async def edit_cron_time(update, context):
    user_id = update.message.from_user.id
    new_cron_time = update.message.text
    cron_type = context.user_data.get('cron_settings')
    res = cron_seed(user_id, cron_type, new_cron_time)
    if res == True:
        cron_command(user_id,new_cron_time)
        await update.message.reply_text(f"تم التحديث إلى:  {new_cron_time}")
    else:
        await update.message.reply_text("لا يمكن تحديث التوقيت في الوقت الراهن")

    return ConversationHandler.END


async def cron_command(user_id, time):
    # PythonAnywhere API URL
    api_url = "https://www.pythonanywhere.com/api/v0/user/ElkhamlichiOussa/scheduled_tasks/"
    
    # Your PythonAnywhere API key
    api_key = "a41772ed5416f9eab35151f7ab443c797562ba6a"
    
    # Cron job details
    command = f"python3 /home/ElkhamlichiOussama/purpose_ally/scheduled/tasks.py {user_id}"
    # Schedule cron job to run daily at 8 AM

    time_obj = datetime.strptime(time, "%H:%M")
    
    # Extract hour and minute
    hour = time_obj.hour
    minute = time_obj.minute
    
    # Convert to cron format: minute hour * * *
    schedule = f"{minute} {hour} * * *"

    print(schedule)    
    # return cron_format
    
    # Create headers with API key for authentication
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    # Data to create a new cron job
    data = {
        "enabled": True,
        "command": command,
        "schedule": schedule,
    }
    
    # Make the API request to create the cron job
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    
    # Check if the cron job was created successfully
    if response.status_code == 201:
        print("Cron job created successfully.")
    else:
        print(f"Failed to create cron job: {response.status_code}")
        print(response.text)

    
async def learning_tracks(update, context):
    await update.callback_query.message.reply_text('مسارات')


async def contact_us(update, context):
    await update.callback_query.message.reply_text('اتصل بنا')


async def handle_default(update, context):
    await update.callback_query.message.reply_text(update.callback_query.data)


async def cancel(update, context):
    await update.callback_query.message.reply_text('Canceled')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:",
                  exc_info=context.error)

    if update.effective_chat:
        await update.effective_chat.send_message(text="حدث خطأ ما X__X")


def main():
    convo_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(set_goals, pattern='set_goals'),
            CallbackQueryHandler(edit_op, pattern='edit_op'),
            CallbackQueryHandler(edit_goal_selection, pattern=".*\*\*\*.*"),
            CallbackQueryHandler(set_cron_opt, pattern='set_cron_opt_call'),
            CallbackQueryHandler(edit_cron, pattern='edit_cron_launch'),
            CallbackQueryHandler(identification, pattern='identification'),
            CallbackQueryHandler(how_to_set_goals, pattern='how_to_set_goals'),
            CallbackQueryHandler(learning_tracks, pattern='learning_tracks'),
            CallbackQueryHandler(contact_us, pattern='contact_us'),
            CallbackQueryHandler(show_demo, pattern='show_demo'),
        ],
        states={
            MAIN_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_goal_req)],
            SUB_GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sub_goal_req)],
            EDIT_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_goal)],
            SET_CRON: [CallbackQueryHandler(set_cron, pattern='cronOption:*')],
            SET_CRON_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_cron_time)],
            EDIT_CRON_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_cron_time)],
            SET_CRON_WEEKDAY: [CallbackQueryHandler(set_cron, pattern='weekday')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(convo_handler)
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.run_polling()



if __name__ == "__main__":
    main()
