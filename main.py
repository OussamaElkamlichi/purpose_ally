from datetime import datetime, timezone
import logging
import os
import json
import requests
import pytz
from timezonefinder import TimezoneFinder
from dotenv import load_dotenv
from telegram import (BotCommand, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)
from classes.userGoals import UserGoals
from telegram.error import BadRequest, TelegramError
from validators.timeValidator import is_valid_24_hour_time
from dbAgent.agent import essential_seed, show_demo_db, edit_prep, updateGoal, cron_seed, deleteGoal, get_cron_time, location_seed, get_user

TOKEN = "7858277817:AAGt_RDeo8KcoIpu1ZOXZ8Lm2T7S1aQ9ca0"
app = Application.builder().token(TOKEN).build()
dir_path = os.getcwd()
IDENTIFICATION, HOW_TO_SET_GOALS, SET_GOALS, SEEK_KNOWLEDGE, CONTACT_US, MAIN_GOAL, SUB_GOALS, EDIT_GOAL, USER_TIMEZONE, SET_CRON, SET_CRON_TIME, SET_CRON_WEEKDAY , EDIT_CRON_TIME, VALIDATE_CRON, CONFIRM_CRON_TIME= range(
    15)

commands = [
    BotCommand("start", '🤖 تعريف شريك الهمة'),
    BotCommand("learn_how", "🤔 كيف أحدّد أهدافي"),
    BotCommand("goal", '📋 تسجيل أهدافي الخاصة'),
    BotCommand("study", '📚 الاطلاع على مسارات طلب العلم'),
    BotCommand("contact", '📥 الاتصال بنا')
]

bot = Bot(token=TOKEN)
description = """🎯 مساعدك الشخصي لتحقيق أهدافك!

هل تبحث عن طريقة سهلة لتتبع أهدافك وتحقيق طموحاتك؟

🔹 مع هذا البوت يمكنك:
• وضع أهداف جديدة بكل سهولة
• تتبع تقدمك خطوة بخطوة
• استلام تذكيرات منتظمة في الأوقات التي تحددها
• مراجعة إنجازاتك بشكل دوري

✨ مميزات خاصة:
• واجهة سهلة الاستخدام
• تذكيرات ذكية
• تقارير دورية عن تقدمك
• دعم فني متواصل

📱 للتواصل مع المطور:
@OussamaElkhamlichi

🚀 ابدأ رحلة تحقيق أهدافك الآن!"""

async def set_bot_description():
    try:
        # Try setting short description
        await bot.set_my_short_description(
            short_description="🎯 مساعدك الشخصي لتحقيق أهدافك!",
            language_code="ar"
        )
        
        # Try setting full description
        await bot.set_my_description(
            description=description,
            language_code="ar"
        )
        return "Successfully set bot description"
    except TelegramError as e:
        return f"Error setting description: {str(e)}"

# def estimate_timezone(update, context):
#     utc_time = update.message.date
#     local_time = datetime.now(timezone.utc)
#     difference = (local_time - utc_time).total_seconds() / 3600
#     print(f"Estimated timezone offset: UTC{difference:+.0f}")

async def set_command_menu():
    await app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # result = await set_bot_description()
    # await update.message.reply_text(f"Description setup result: {result}")
    # estimate_timezone(update, context)
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user_type = update.message.chat.type
    course_id = 0
    response_code, result = essential_seed(username, user_id, user_type, course_id)
    if response_code == 200:
        message = result.get("message", "An error occurred.")
        reply_markup = result.get("reply_markup")
        await update.message.reply_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup,
        )
    elif response_code == 201:
        projectName = 'شريك الهمّة'

        keyboard = [
            [InlineKeyboardButton('🤖 تعريف شريك الهمة',
                                  callback_data='identification')],
            [InlineKeyboardButton('🤔 كيف أحدّد أهدافي',
                                  callback_data='how_to_set_goals')],
            [InlineKeyboardButton('📋 تسجيل أهدافي الخاصة',
                                  callback_data='set_goals')],
            # [InlineKeyboardButton('📚 الاطلاع على مسارات طلب العلم',
            #                       callback_data='learning_tracks')],
            # [InlineKeyboardButton('📥 الاتصال بنا', callback_data='contact_us')]
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
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
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
    await update.callback_query.answer()
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
        [InlineKeyboardButton("تعديل/حذف نص الأهداف", callback_data="edit_op")],
        [InlineKeyboardButton("تحديد وقت إرسال المهمات",
                              callback_data="get_location_call")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        '<blockquote>استعن بالله ولا تعجز 🍃</blockquote>\n',
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def edit_op(update, context):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    goals_list = edit_prep(user_id)

    keyboard = [
        [InlineKeyboardButton(
            goal["text"], callback_data=f'{goal["type"]}***{goal["id"]}***{goal["text"]}')]
        for goal in goals_list
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        '<blockquote>اختر ما تريد حذفه أو تعديله</blockquote>\n',
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
            f'<blockquote>تم اختيار 🎯</blockquote>\n{goal_text}\n\n'
            'اكتب(ي) نص الهدف صحيحاً \n'
            'اكتب(ي) "حذف" لحذف الهدف\n\n'
            '<b>ملاحظة: </b> حذف الهدف الرئيسي يتبعه حذف الأهداف الفرعية \n',
            parse_mode='HTML'
        )
        return EDIT_GOAL

async def edit_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    new_goal_text = update.message.text
    goal_type = context.user_data.get('goal_type')
    goal_id = context.user_data.get('goal_id')
    old_goal_text = context.user_data.get('old_goal_text')

    if new_goal_text in ["حذف","حدف"]:
        res = deleteGoal(update.message.from_user.id,
                        new_goal_text, goal_type, goal_id, old_goal_text)
        await update.message.reply_text(res, parse_mode="HTML")
    else:
        result = updateGoal(update.message.from_user.id,
                        new_goal_text, goal_type, goal_id, old_goal_text)
        await update.message.reply_text(result, parse_mode='HTML')

    return ConversationHandler.END

async def get_location(update, context):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        '<blockquote>المرجو إرسال موقعكم لمعرفة التوقيت المحلي</blockquote>\n',
        parse_mode='HTML'
    )
    return USER_TIMEZONE

async def get_user_timezone(update, context):
    if update.message.location:
        user_id = update.message.from_user.id
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        # await update.message.reply_text(f"Your timezone appears to be: {timezone_str}")
        if timezone_str:
            local_timezone = pytz.timezone(timezone_str)
            local_time = datetime.now(local_timezone)
            utc_offset = local_time.strftime('%z')  # Returns something like '+0100', '-0500'
            if utc_offset[0] == "+":
                utc_offset_str = f"GMT+{utc_offset[1:3]}:{utc_offset[3:]}"
            else:
                utc_offset_str = f"GMT{utc_offset[:3]}:{utc_offset[3:]}"
            stt_code = location_seed(user_id, timezone_str,utc_offset_str)
            if stt_code in (200, 204):
                await update.message.reply_text(f"التوقيت المحلي هو: {utc_offset_str}")
                keyboard = [
                [InlineKeyboardButton("يوميًا", callback_data="cronOption:daily")],
                # [InlineKeyboardButton(
                #     "أسبوعيًا", callback_data="cronOption:weekly")],
                # [InlineKeyboardButton("تخصيص", callback_data="cronOption:custom")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    '<blockquote>تحديد وقت الإرسال  ⏲️</blockquote>\n',
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                return SET_CRON
            else:
                await update.message.reply_text(f"خطأ X__X {stt_code}")

        else:
            await update.message.reply_text("خطأ داخلي X__X")
    else:
        update.message.reply_text("المرجو إرسال موقعك. كل بياناتك محفوظة✅")

async def set_cron(update, context):
    await update.callback_query.answer()
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
    keyboard = [[  InlineKeyboardButton("تعديل", callback_data="edit_cron_launch")],
    [  InlineKeyboardButton("موافق", callback_data="ok_response")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    result = is_valid_24_hour_time(update.message.text)
    if result is True:
        context.user_data['cron_time'] = update.message.text
        await update.message.reply_text(
                "<blockquote>تم تحديد وقت الإرسال ⏰</blockquote>\n"
                f"<b>يومياً على الساعة:  {context.user_data.get('cron_time')}</b> ",
                reply_markup=reply_markup,
                parse_mode='HTML'
        )
        return CONFIRM_CRON_TIME
    else:
        await update.message.reply_text(
                "<blockquote>خطأ في كتابة الوقت ❌</blockquote>\n"
                f"<b>مثال: 22:05</b> ",
                parse_mode='HTML'
        )
        return SET_CRON_TIME

async def edit_cron_time(update, context):
    user_id = update.message.from_user.id
    new_cron_time = update.message.text
    cron_type = context.user_data.get('cron_settings')
    status_code, cron_time, job_Id = get_cron_time(user_id)
    stt, message, jobId = await cron_command(user_id,new_cron_time,job_Id)
    print(stt)
    print(message)
    print(jobId)
    if stt == 200:
        res = cron_seed(user_id, cron_type, new_cron_time, jobId)
        if res == True:
            await update.message.reply_text(f"تم التحديث إلى:  {new_cron_time}")
        else:
            await update.message.reply_text(f" حدث خطأ : { status_code}")
    else:
        await update.message.reply_text("لا يمكن تحديث التوقيت في الوقت الراهن")

    return ConversationHandler.END

async def cron_command(user_id, time, job_id):
    stt_code, result= get_user(user_id)
    user_timezone = result[0][5]
    if stt_code == 200:
       
       if job_id is None:
        api_url = "https://api.cron-job.org/jobs"

        api_key = "y7C+Yb8a55Zgb6883Q88eUfyEIUNYZhOJhIlyIfbhUI="

        command_url = f"https://ElkhamlichiOussama.pythonanywhere.com/task/{user_id}"  # Replace with the actual URL for your task

        time_obj = datetime.strptime(time, "%H:%M")

        hour = time_obj.hour
        minute = time_obj.minute

        schedule = {
            "job": {
            "url": command_url,
            "enabled": True,
            "saveResponses": True,
            "schedule": {
                "timezone": user_timezone,
                "expiresAt": 0,
                "hours": [hour],      # Specific hour
                "minutes": [minute],  # Specific minute
                "mdays": [-1],        # Every day of the month
                "months": [-1],       # Every month
                "wdays": [-1]         # Every day of the week
            }
            }
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.put(api_url, headers=headers, data=json.dumps(schedule))
        response_data = response.json()
        if response.status_code == 200:
            print("THE RESPONSE DATA IS HERE BABY!",response_data)
            job_id = response_data['jobId']
            if job_id:
                return 200, "Cron job success", job_id
            else:
                return 500, "No job_id is provided", None
        else:
            # print(f"Failed to create cron job: {response.status_code}")
            return response.status_code, "Cron job denied 1"
       else:
        api_url = f"https://api.cron-job.org/jobs/{job_id}"  # Replace with your actual job ID
        api_key = "y7C+Yb8a55Zgb6883Q88eUfyEIUNYZhOJhIlyIfbhUI="

        command_url = f"https://ElkhamlichiOussama.pythonanywhere.com/task/{user_id}"  # Replace with the actual URL for your task

        time_obj = datetime.strptime(time, "%H:%M")

        hour = time_obj.hour
        minute = time_obj.minute

        schedule = {
            "job": {
                "url": command_url,
                "enabled": True,
                "saveResponses": True,
                "schedule": {
                    "timezone": user_timezone,
                    "expiresAt": 0,  # Adjust if needed
                    "hours": [hour],  # Specific hour
                    "minutes": [minute],  # Specific minute
                    "mdays": [-1],  # Every day of the month
                    "months": [-1],  # Every month
                    "wdays": [-1]  # Every day of the week
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.patch(api_url, headers=headers, data=json.dumps(schedule))  # Changed to PATCH
        # print(f"Response Status Code: {response.status_code}")
        # print(f"Response Text: {response.text}")


        if response.status_code == 200:
            response_data = response.json() 
            print(response_data)
            return 200, "Cron job success", job_id
            # return 200, "Cron job success", job_id
        else:
            # Print the error if failed
            # print(f"Failed to create cron job: {response.status_code} - {response.text}")
            return response.status_code, "Cron job denied 2", None

async def old_goals(update, context):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    goals_list = show_demo_db(user_id)
    main_goals = list(goals_list.keys())  # Collect all main goals as options

    await update.callback_query.message.reply_text(
        '<blockquote>هكذا ستبدو أهدافك 🍃</blockquote>\n',
        parse_mode='HTML'
    )
    unformatted_list = edit_prep(user_id)
    
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question="سجّل مهامك اليومية أثابك الله",
        options=main_goals,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    keyboard = [
        [InlineKeyboardButton("تعديل/حذف نص الأهداف", callback_data="edit_op")],
        [InlineKeyboardButton("تحديد وقت إرسال المهمات",
                              callback_data="get_location_call")]
    ]
    formatted_text = ""
    main_goal_indent = "" 
    sub_goal_indent = "    • "

    for item in unformatted_list:
        if item["type"] == "main":
            formatted_text += main_goal_indent + item['text'] + "\n"
        elif item["type"] == "sub":
            formatted_text += sub_goal_indent + item['text'] + "\n"
    status_code, cron_time, job_Id = get_cron_time(user_id)
    if status_code == 200:
        time = cron_time
    else:
        time = "لم يتحدد بعد"
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        '<blockquote>تفاصيل الأهداف🍃</blockquote>\n'
        f"\n{formatted_text}\n"
        f"<b>الإرسال اليومي على الساعة:</b> {time} ",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def handle_confirm_cron(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "edit_cron_launch":
        # Transition to edit state
        await query.message.reply_text(
            "المرجو كتابة التوقيت بدقّة (مثال: 06:00)"
        )
        return EDIT_CRON_TIME
    elif query.data == "ok_response":
        user_id = query.from_user.id
        cron_type = context.user_data.get('cron_settings')
        time = context.user_data.get('cron_time')
        status_code, cron_time, job_Id = get_cron_time(user_id)
        stt_code, message, jobId = await cron_command(user_id, time, job_Id)
        print(stt_code, message, jobId)
        if stt_code == 200:
            res = cron_seed(user_id, cron_type, time, jobId)   
            if res:
                await query.message.reply_text(
                    "<blockquote>وفقكم الله وأعانكم 🍃</blockquote>\n",
                    parse_mode='HTML'
                )
            else:
                await query.message.reply_text(f"حدث خطأ: {status_code}")
        else:
            await query.message.reply_text(
                "<blockquote>لا يمكن تحديد التوقيت</blockquote>\n"
                f"<b>خطأ داخلي</b>",
                parse_mode='HTML'
            )
        return ConversationHandler.END

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

    # if update.effective_chat:
    #     await update.effective_chat.send_message(text="حدث خطأ ما X__X")

def main():
    convo_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(set_goals, pattern='set_goals'),
            CallbackQueryHandler(edit_op, pattern='edit_op'),
            CallbackQueryHandler(edit_goal_selection, pattern=".*\*\*\*.*"),
            CallbackQueryHandler(get_location, pattern='get_location_call'),
            # CallbackQueryHandler(edit_cron, pattern='edit_cron_launch'),
            CallbackQueryHandler(old_goals, pattern='indeed'),
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
            USER_TIMEZONE: [MessageHandler(filters.LOCATION & ~filters.COMMAND, get_user_timezone)],
            SET_CRON: [CallbackQueryHandler(set_cron, pattern='cronOption:*')],
            CONFIRM_CRON_TIME: [CallbackQueryHandler(handle_confirm_cron, pattern="edit_cron_launch|ok_response")],
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
