import asyncio
import mysql.connector
import sys
from telegram import Bot
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
    # Collect main goals as options
    main_goals = list(my_list.keys())
    
    # Send the poll to the user
    await bot.send_poll(
        chat_id=user_id,
        question="سجّل مهامك اليومية أثابك الله",
        options=main_goals,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

async def task(user_id):
    conn, cursor = create_connection()
    if not conn:
        return

    try:
        my_list = {}
        show_sql = "SELECT goal_id, goal_title FROM goals WHERE user_id = %s"
        cursor.execute(show_sql, (user_id,))
        res = cursor.fetchall()

        for main_goal in res:
            goal_id, goal_title = main_goal
            subgoals = []

            # Fetch sub-goals for the current main goal
            sql_sub = "SELECT subgoal_title, status FROM subgoals WHERE goal_id = %s"
            cursor.execute(sql_sub, (goal_id,))
            result = cursor.fetchall()

            # Append each sub-goal as a dictionary to the subgoals list
            for sub_goal in result:
                subgoals.append({"subgoal_title": sub_goal[0], "status": sub_goal[1]})

            # Store the list of sub-goals under the main goal title
            my_list[goal_title] = subgoals
        bot = Bot(token=TOKEN)
        await send_poll(bot, user_id, my_list)
        print("Tasks loaded:", my_list)
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        asyncio.run(task(user_id))
    else:
        print("No user ID provided.")
