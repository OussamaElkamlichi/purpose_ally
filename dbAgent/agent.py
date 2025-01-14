import os
from dotenv import load_dotenv
import mysql.connector
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from classes.dbConnection import dbConnect

def essential_seed(username, user_id, user_type, course_id):
    cursor, conn = dbConnect.connect()
    result = None  
    if cursor is None or conn is None:
        print("failed!!!!")
    try:
        sql1 = "SELECT username FROM users WHERE username_id = %s"
        val = (user_id,)
        cursor.execute(sql1, val)
        username_user = cursor.fetchone()
        if cursor.rowcount > 0:
            username = username_user[0] 
            sql2 = "SELECT goal_title FROM goals WHERE user_id = %s"
            val = (user_id,)
            cursor.execute(sql2, val)
            cursor.fetchall()
            if cursor.rowcount > 0:
                result = {
                    "message": f"<blockquote>🍃<b>{username}</b> ،مرحباً</blockquote>\n\n"
                              "لقد سجّلت معنا أهدافًا في السابق. هل تُحب أن تتابع؟",
                    "reply_markup": InlineKeyboardMarkup([
                        [InlineKeyboardButton('أجل !', callback_data='indeed')],
                        [InlineKeyboardButton('أريد بداية جديدة', callback_data='new_start')]
                    ])
                }
                return 200, result  
            sql3 = "SELECT title FROM courses WHERE user_id= %s"
            val = (user_id,)
            cursor.execute(sql3, val)
            cursor.fetchall()
            if cursor.rowcount > 0:
                result = {
                    "message": f"<blockquote> 🍃 <b>{username}</b> ،مرحباً</blockquote>\n\n"
                              "لقد سجّلت معنا في أحد المسارات سابقاً. هل تريد أن تتابع؟",
                    "reply_markup": InlineKeyboardMarkup([
                        [InlineKeyboardButton('أجل !', callback_data='indeed')],
                        [InlineKeyboardButton('أريد بداية جديدة', callback_data='new_start')]
                    ])
                }
                return 200, result  

        else:
            sql4 = "INSERT INTO users (username, username_id, user_type) VALUES (%s,%s,%s)"
            vals = (username, user_id, user_type)
            cursor.execute(sql4, vals)
            cursor.fetchall()
            conn.commit()
            result = {
                "message":"done"
            }

        return 201, result 
    except mysql.connector.Error as err:
        return {"message": f"Error: {err}", "reply_markup": None}
    finally:
        dbConnect.close()

def goals_seeding(goals_list, user_id):
    cursor, conn = dbConnect.connect()
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
    finally:
        dbConnect.close()

def show_demo_db(user_id):
    cursor, conn = dbConnect.connect()
    my_list = {}
    try:
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
    except mysql.connector.Error as err:
        print("Error:", err)
        return f"Error: {err}"
    finally:
        dbConnect.close()

def edit_prep(user_id):
    cursor, conn = dbConnect.connect()
    # Get main goals
    try:
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

        return main_list
    except mysql.connector.Error as err:
        print("Error:", err)
        return f"Error: {err}"
    finally:
        dbConnect.close()

def updateGoal(user_id, new_goal_text, goal_type, goal_id, old_goal_text):
    cursor, conn = dbConnect.connect()
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
    finally:
        dbConnect.close()

def deleteGoal(user_id, new_goal_text, goal_type, goal_id, old_goal_text):
    cursor, conn = dbConnect.connect()
    try:
        if goal_type == "main":
            query = "DELETE FROM goals WHERE goal_id = %s"
        elif goal_type == "sub":
            query = "DELETE FROM subgoals WHERE subgoal_id = %s"
        else:
            return "نوع الهدف غير معروف."

        values = (goal_id,)
        cursor.execute(query, values)
        conn.commit()
        return "تم حذف الهدف بنجاح."
    except Exception as e:
        return f"فشل الحذف: {str(e)}"
    finally:
        dbConnect.close()

def cron_seed(user_id, type, params):
    cursor, conn = dbConnect.connect()
    try:
        request_sql = "SELECT user_id FROM scheduled WHERE user_id = %s"
        request_values = (user_id,)
        cursor.execute(request_sql, request_values)
        cursor.fetchall()
        if cursor.rowcount > 0:  # Check rowcount immediately after SELECT
            request_sql = "UPDATE scheduled SET type = %s, cron_pattern = %s WHERE user_id = %s"
            request_values = (type, params, user_id)
            print((type, params, user_id))
            cursor.execute(request_sql, request_values)
            conn.commit()
            print(cursor.rowcount)
            return cursor.rowcount > 0 # Return True if any rows were updated, False otherwise
        else:
            cron_sql = "INSERT INTO scheduled (user_id, type, cron_pattern) VALUES (%s, %s, %s)"
            cron_vals = (user_id, type, params)
            cursor.execute(cron_sql, cron_vals)
            conn.commit()
            print("ok3")
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        dbConnect.close()

def get_cron_time(user_id):
    cursor, conn = dbConnect.connect()
    try:
        request = "SELECT cron_pattern FROM scheduled WHERE user_id=%s"
        request_values = (user_id,)
        cursor.execute(request,request_values)
        time = cursor.fetchone()
        if time:
            return 200, time[0]
        else:
            return 404, None
    except Exception as e:
        print(f"Erro: {e} ")
        conn.rollback()
        return 500, False
    finally:
        dbConnect.close()