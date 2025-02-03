import asyncio
import mysql.connector
import sys
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dbAgent.agent import progress_bar, fetch_weekly_data
TOKEN = "7858277817:AAGt_RDeo8KcoIpu1ZOXZ8Lm2T7S1aQ9ca0"

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="purpose_ally"
        )
        # conn = mysql.connector.connect(
        #     host="ElkhamlichiOussama.mysql.pythonanywhere-services.com",
        #     user="ElkhamlichiOussa",
        #     password="Alhamdulillah",
        #     database="ElkhamlichiOussa$purpose_ally"
        # )
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as err:
        print(f"Error while connecting to MySQL: {err}")
        return None, None

async def send_poll(bot, user_id, my_list):
    if not my_list:
        keyboard = [[InlineKeyboardButton("موافق", callback_data="stop_cron")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(user_id,
            "<blockquote>🎉بارك الله! لقد أنجزت جميع أهدافك!</blockquote>\n\n"
            "<b>هل تريد أن توقف التنبيهات اليومية؟</b>\n",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        conn, cursor = create_connection()
        if not conn:
            print("Failed to connect to the database.")
            return
    try:
        for goal_title, goal_data in my_list.items():
            goal_id = goal_data["goal_id"]
            sub_goals = goal_data["subgoals"]
            options = [sub_goal["subgoal_title"] for sub_goal in sub_goals]
            if len(options) < 2:
                options.extend(["لا يمكن إرسال تصويت", "بخيار واحد فقط، لذا نضيف هذين"]) 
            sent_poll = await bot.send_poll(
                chat_id=user_id,
                question=goal_title,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=True,
            )
            insert_sql = " INSERT INTO poll_mappings (poll_id, goal_id, user_id) VALUES (%s, %s, %s)"
            insert_vals = (sent_poll.poll.id, goal_id, user_id)
            cursor.execute(insert_sql, insert_vals)
            conn.commit()
    except Exception as e:
        print(f"Failed to send poll for {goal_title}: {e}")

async def task(user_id):
    conn, cursor = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return

    try:
        my_list = {}
        show_sql = "SELECT goal_id, goal_title FROM goals WHERE user_id = %s AND status!=%s"
        cursor.execute(show_sql, (user_id,'done'))
        res = cursor.fetchall()
        for goal in res:
            goal_id, goal_title = goal
            # daily_session_sql = "INSERT INTO daily_sessions (user_id, goal_id, status) VALUES (%s, %s, %s)"
            # daily_session_vals = (user_id, goal_id, "started")
            # cursor.execute(daily_session_sql, daily_session_vals)
            # conn.commit()

            # if cursor.rowcount > 0:
            subgoals = []
            sql_sub = "SELECT subgoal_title, status, subgoal_id FROM subgoals WHERE goal_id = %s AND status!=%s"
            cursor.execute(sql_sub, (goal_id,'done'))
            result = cursor.fetchall()

            for sub_goal in result:
                subgoals.append({"subgoal_title": sub_goal[0], "status": sub_goal[1]})
                daily_session_sql = "INSERT INTO daily_sessions (user_id, goal_id, status) VALUES (%s, %s, %s)"
                daily_session_vals = (user_id, sub_goal[2], "started")
                cursor.execute(daily_session_sql, daily_session_vals)
                conn.commit()
            my_list[goal_title] = {
                    "goal_id": goal_id,
                    "subgoals": subgoals,
                }
            
            # else:
            #     print('DOOMED!')

        # Move poll sending outside the loop
        bot = Bot(token=TOKEN)
        await send_poll(bot, user_id, my_list)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

async def weekly_cron(user_id):
    bot = Bot(token=TOKEN)
    try:
        # Fetch data from the database
        total_goals, total_assigned_subgoals, completed_subgoals, completed_sessions, total_sessions = fetch_weekly_data(user_id)
        
        # Calculate progress percentages (handle division by zero)
        goal_progress = (completed_subgoals / total_assigned_subgoals * 100) if total_assigned_subgoals > 0 else 0
        session_progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

        # Generate the report message
        report_message = (
            "📊 *تقرير التقدم الأسبوعي* 📊\n\n"
            f"🏆 *الأهداف الرئيسية:* {total_goals} هدف\n"
            f"🎯 *الأهداف الفرعية المكتملة:* {completed_subgoals} هدف فرعي\n"
            f"🕒 *الجلسات اليومية المكتملة:* {completed_sessions}/{total_sessions}\n\n"
            "🚀 *تقدم الأهداف:*\n"
            f"{progress_bar(goal_progress)}\n\n"
            "📅 *تقدم الجلسات اليومية:*\n"
            f"{progress_bar(session_progress)}\n\n"
            "✅ *استمر في العمل الجيد!* 💪"
        )

        # Send the report message
        await bot.send_message(chat_id=user_id, text=report_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in weekly_cron: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        asyncio.run(task(user_id))
    else:
        print("No user ID provided.")
