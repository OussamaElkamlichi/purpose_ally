import os
from dotenv import load_dotenv
import mysql.connector
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
conn = None
cursor = None
config = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_DATABASE', 'purpose_ally'),
}

def create_connection():
    global conn, cursor
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    


def essential_seed(username, user_id, user_type, course_id):
    create_connection()
    result = None  # Initialize result to ensure it's always defined
    try:
        sql1 = "SELECT username FROM users WHERE username_id = %s"
        val = (user_id,)
        cursor.execute(sql1, val)
        username_user = cursor.fetchone()
        if cursor.rowcount > 0: 
            sql2 = "SELECT goal_title FROM goals WHERE user_id = %s"
            val = (user_id,)
            cursor.execute(sql2, val)
            if cursor.rowcount > 0:
                result = {
                    "message": f"<blockquote>🍃<b>{username_user}</b> مرحباً</blockquote>\n\n"
                               "لقد سجّلت معنا أهدافًا في السابق. هل تُحب أن تتابع؟",
                    "reply_markup": InlineKeyboardMarkup([
                        [InlineKeyboardButton('!أجل', callback_data='indeed')],
                        [InlineKeyboardButton('أريد بداية جديدة', callback_data='new_start')]
                    ])
                }
                return result  # Return if result is set
            
            # Remove cursor.fetchall() since you want to check rowcount only
            sql3 = "SELECT title FROM courses WHERE user_id= %s"
            val = (user_id,)
            cursor.execute(sql3, val)
            if cursor.rowcount > 0:
                result = {
                    "message": f"<blockquote>🍃<b>{username_user}</b> مرحباً</blockquote>\n\n"
                               "لقد سجّلت معنا في أحد المسارات سابقاً. هل تريد أن تتابع؟",
                    "reply_markup": InlineKeyboardMarkup([
                        [InlineKeyboardButton('!أجل', callback_data='indeed')],
                        [InlineKeyboardButton('أريد بداية جديدة', callback_data='new_start')]
                    ])
                }
                return result  # Return if result is set
            
        else:
            sql4 = "INSERT INTO users (username, username_id, user_type) VALUES (%s,%s,%s)"
            vals = (username, user_id, user_type)
            cursor.execute(sql4, vals)
            conn.commit()
            result = {"message": "don't send", "reply_markup": None}

        return result  # Ensure we return a result at the end
    except mysql.connector.Error as err:
        return {"message": f"Error: {err}", "reply_markup": None}

def goals_seeding(goals_list, user_id):
    create_connection()
    try:
        sql = "INSERT INTO goals (user_id, goal_title, goal_description, status, target_date) VALUES (%s, %s, %s, %s, %s)"
        for main_goal, sub_goals in goals_list.items():
            # Insert main goal
            main_goal_vals = (user_id, main_goal, None, "not_started", None)
            cursor.execute(sql, main_goal_vals)
            main_goal_id = cursor.lastrowid
            # Insert each sub-goal
            for sub_goal in sub_goals:
                subgoals_sql = "INSERT INTO subgoals (goal_id, subgoal_title, subgoal_description, duration, status, target_date) VALUES (%s, %s, %s, %s, %s, %s)"
                sub_goal_vals = (main_goal_id, sub_goal, "None", "None", "not_started", "None")
                # print(sub_goal_vals)
                cursor.execute(subgoals_sql, sub_goal_vals)
                cursor.fetchall()
        
        conn.commit()          
        return "تم الإدخال"
    except mysql.connector.Error as err:
        print("Error:", err)
        return f"Error: {err}"

def show_demo_db(user_id):
    my_list = {}
    show_sql = "SELECT goal_id, goal_title FROM goals WHERE user_id = %s"
    show_val = (user_id,)
    cursor.execute(show_sql, show_val)
    res = cursor.fetchall()
    
    for main_goal in res:
        goal_id = main_goal[0]
        goal_title = main_goal[1]
        
        # Initialize a list to store sub-goals for each main goal
        subgoals = []
        
        # Fetch sub-goals for the current main goal
        sql_sub = "SELECT subgoal_title, status FROM subgoals WHERE goal_id = %s"
        val_sub = (goal_id,)
        cursor.execute(sql_sub, val_sub)
        result = cursor.fetchall()
        
        # Append each sub-goal as a dictionary to the subgoals list
        for sub_goal in result:
            subgoals.append({"subgoal_title": sub_goal[0], "status": sub_goal[1]})
        
        # Store the list of sub-goals under the main goal title
        my_list[goal_title] = subgoals
    
    return my_list

def edit_prep(user_id):
    # Get main goals
    show_sql = "SELECT goal_id, goal_title FROM goals WHERE user_id = %s"
    show_val = (user_id,)
    cursor.execute(show_sql, show_val)
    res = cursor.fetchall()

    # Collect goals and sub-goals
    main_list = []
    for main_goal in res:
        main_goals_list = {"type": "main", "id": main_goal[0], "text": main_goal[1]}
        main_list.append(main_goals_list)

        # Get sub-goals linked to the main goal
        sql_sub = "SELECT subgoal_id, subgoal_title, status FROM subgoals WHERE goal_id = %s"
        val_sub = (main_goal[0],)
        cursor.execute(sql_sub, val_sub)
        result = cursor.fetchall()

        for sub_goal in result:
            sub_goals_list = {"type": "sub", "id": sub_goal[0], "text": sub_goal[1]}
            main_list.append(sub_goals_list)

    # print("***************************")
    # print(main_list)
    # print("***************************")
    return main_list

def updateGoal(user_id, new_goal_text, goal_type, goal_id, old_goal_text):
    try:
        if goal_type == "main":
            query = "UPDATE goals SET goal_title = %s WHERE goal_id = %s"
        elif goal_type == "sub":
            query = "UPDATE subgoals SET subgoal_title = %s WHERE subgoal_id = %s"
        else:
            return "نوع الهدف غير معروف."

        values = (new_goal_text, goal_id)
        cursor.execute(query, values)
        conn.commit()

        return "تم تحديث الهدف بنجاح."
    except Exception as e:
        return f"فشل التحديث: {str(e)}"
def cron_seed(user_id, type, params):
    try:
        cron_sql = "INSERT INTO scheduled (user_id, type, cron_pattern) VALUES (%s,%s,%s)"
        cron_vals = (user_id, type, params)
        cursor.execute(cron_sql, cron_vals)
        conn.commit()

        if cursor.rowcount > 0:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback() 
        return False

