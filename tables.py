import mysql.connector
from mysql.connector import errorcode

# Database connection configuration
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'purpose_ally',
}

# SQL commands for creating the tables
TABLES = {}

TABLES['users'] = (
    "CREATE TABLE IF NOT EXISTS users ("
    "  username VARCHAR(255) NOT NULL,"
    "  username_id BIGINT NOT NULL PRIMARY KEY,"  # Changed INT to BIGINT
    "  user_type VARCHAR(60) NOT NULL,"
    "  joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
    ")"
)

TABLES['courses'] = (
    "CREATE TABLE IF NOT EXISTS courses ("
    "  course_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  title VARCHAR(60),"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE"
    ")"
)

TABLES['lessons'] = (
    "CREATE TABLE IF NOT EXISTS lessons ("
    "  lesson_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  course_id INT NOT NULL,"
    "  title VARCHAR(60),"
    "  link VARCHAR(300),"
    "  FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE"
    ")"
)

TABLES['lesson_course'] = (
    "CREATE TABLE IF NOT EXISTS lesson_course ("
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  course_id INT NOT NULL,"
    "  lesson_id INT NOT NULL,"
    "  status VARCHAR(60),"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE"
    ")"
)

TABLES['goals'] = (
    "CREATE TABLE IF NOT EXISTS goals ("
    "  goal_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  goal_title VARCHAR(255) NOT NULL,"
    "  goal_description TEXT,"
    "  status VARCHAR(50) DEFAULT 'not_started',"
    "  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    "  target_date DATETIME,"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE"
    ")"
)

TABLES['subgoals'] = (
    "CREATE TABLE IF NOT EXISTS subgoals ("
    "  subgoal_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  goal_id INT NOT NULL,"
    "  subgoal_title VARCHAR(255) NOT NULL,"
    "  subgoal_description TEXT,"
    "  duration INT,"
    "  status VARCHAR(50) DEFAULT 'not_started',"
    "  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    "  target_date DATETIME,"
    "  FOREIGN KEY (goal_id) REFERENCES goals(goal_id) ON DELETE CASCADE"
    ")"
)

TABLES['sessions'] = (
    "CREATE TABLE IF NOT EXISTS sessions ("
    "  session_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  goal_id INT NOT NULL,"
    "  session_title VARCHAR(255) NOT NULL,"
    "  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    "  FOREIGN KEY (goal_id) REFERENCES goals(goal_id) ON DELETE CASCADE"
    ")"
)

TABLES['daily_sessions'] = (
    "CREATE TABLE IF NOT EXISTS daily_sessions ("
    "  daily_session_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  goal_id INT NOT NULL,"
    "  status VARCHAR(50) DEFAULT 'incomplete',"
    "  completed_at DATETIME,"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (goal_id) REFERENCES goals(goal_id) ON DELETE CASCADE"
    ")"
)

TABLES['achievements'] = (
    "CREATE TABLE IF NOT EXISTS achievements ("
    "  achievement_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  goal_id INT NOT NULL,"
    "  completed_at DATETIME NOT NULL,"
    "  type VARCHAR(50) NOT NULL,"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (goal_id) REFERENCES goals(goal_id) ON DELETE CASCADE"
    ")"
)

TABLES['stats'] = (
    "CREATE TABLE IF NOT EXISTS stats ("
    "  stat_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  total_goals INT DEFAULT 0,"
    "  total_sub_goals INT DEFAULT 0,"
    "  total_completed_sessions INT DEFAULT 0,"
    "  total_uncompleted_sessions INT DEFAULT 0,"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE"
    ")"
)

TABLES['questions'] = (
    "CREATE TABLE IF NOT EXISTS questions ("
    "  question_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id BIGINT NOT NULL,"  # Changed INT to BIGINT
    "  question TEXT NOT NULL,"
    "  answer TEXT,"
    "  FOREIGN KEY (user_id) REFERENCES users(username_id) ON DELETE CASCADE"
    ")"
)

# Function to create tables
def create_tables(cursor):
    for table_name, table_sql in TABLES.items():
        try:
            print(f"Creating table {table_name}: ", end="")
            cursor.execute(table_sql)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table already exists.")
            else:
                print(err.msg)
        else:
            print(f"Table {table_name} created successfully.")

def main():
    try:
        # Connect to the MySQL database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create the tables
        create_tables(cursor)

        # Commit the changes
        cnx.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the connection
        cursor.close()
        cnx.close()

if __name__ == '__main__':
    main()
