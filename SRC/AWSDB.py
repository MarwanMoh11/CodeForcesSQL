import pymysql
from pymysql import MySQLError

DB_CONFIG = {
    'host': 'databaseprojectm3.cfuockog8tb5.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'adminadmi',
    'database': 'newschema',
    'port': 3306,
}

def fetch_attempts_by_name(screen_name):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT A.ProblemName, A.Verdict, A.Languageused, A.Duration_ms, A.MemoryUsage_bytes
        FROM Attempts A
        WHERE A.ScreenName = %s;
        """

        cursor.execute(query, (screen_name,))
        attempts = cursor.fetchall()

        if not attempts:
            print(f"No attempts found for screen_name: {screen_name}")
            return None

        print(f"Attempts for screen_name: {screen_name}")
        for attempt in attempts:
            print(f"Problem Name: {attempt[0]}, Verdict: {attempt[1]}, Language Used: {attempt[2]}, Duration (ms): {attempt[3]}, Memory Usage (bytes): {attempt[4]}")

        return attempts

    except MySQLError as e:
        print(f"Database error: {e}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_competitions_by_writer(writer):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT C.ContestName, C.Dateofcontest, C.Division
        FROM contests C
        JOIN contestwriters CW ON C.ContestName = CW.ContestName AND C.Division = CW.Division
        JOIN Users U ON CW.WriterName = U.ScreenName
        WHERE U.ScreenName = %s;
        """

        cursor.execute(query, (writer,))
        competitions = cursor.fetchall()

        if not competitions:
            print(f"No competitions found for writer: {writer}")
            return None

        print(f"Competitions by writer: {writer}")
        for competition in competitions:
            print(f"Contest Name: {competition[0]}, Date: {competition[1]}, Division: {competition[2]}")

        return competitions
    except MySQLError as e:
        print(f"Database error: {e}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_problem_sets_by_tag(tag):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT PS.ProblemName, PS.Time_limit, PS.Memory_limit, PS.Descriptionn
        FROM ProblemSets PS
        JOIN problemset_tags PST ON PS.ProblemName = PST.ProblemName
        WHERE PST.Tag = %s;
        """

        cursor.execute(query, (tag,))
        problem_sets = cursor.fetchall()

        if not problem_sets:
            print(f"No problem sets found for tag: {tag}")
            return None

        print(f"Problem sets for tag: {tag}")
        for problem_set in problem_sets:
            print(f"Problem Name: {problem_set[0]}, Time Limit: {problem_set[1]}, Memory Limit: {problem_set[2]}, Description: {problem_set[3]}")

        return problem_sets
    except MySQLError as e:
        print(f"Database error: {e}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_5_languages_by_efficiency():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT A.Languageused, 
               AVG(A.Duration_ms) AS avg_duration, 
               AVG(A.MemoryUsage_bytes) AS avg_memory
        FROM Attempts A
        GROUP BY A.Languageused
        ORDER BY avg_duration ASC, avg_memory ASC
        LIMIT 5;
        """

        cursor.execute(query)
        languages = cursor.fetchall()

        if not languages:
            print(f"No languages found.")
            return

        print("Top 5 Languages by Efficiency (Avg Time & Memory):")
        for lang in languages:
            print(f"Language: {lang[0]}, Avg Time Spent: {lang[1]:.2f}, Avg Memory Spent: {lang[2]:.2f}")

    except MySQLError as e:
        print(f"Database error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_10_users_by_activity():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT U.ScreenName, U.DaysInRow, U.ProblemsSolved
        FROM Users U
        ORDER BY U.DaysInRow DESC, U.ProblemsSolved DESC
        LIMIT 10;
        """

        cursor.execute(query)
        users = cursor.fetchall()

        if not users:
            print(f"No users found.")
            return

        print("Top 10 Users by Days in Row and Problems Solved:")
        for user in users:
            screen_name, days_in_row, problems_solved_num = user
            print(f"Screen Name: {screen_name}, Days in Row: {days_in_row}, Problems Solved: {problems_solved_num}")

    except MySQLError as e:
        print(f"Database error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_10_users_scores():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = """
        SELECT S.ScreenName, SUM(S.Standing) AS total_score
        FROM ContestStanding S
        WHERE S.Division IN ('Div1', 'Div2')
        GROUP BY S.ScreenName
        ORDER BY total_score DESC
        LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()

        print("Top 10 Users by Total Score:")
        for row in data:
            print(f"Screen Name: {row[0]}, Total Score: {row[1]}")

    except MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_5_organizations_by_ratings_and_country(country):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT U.Organization, AVG(S.Standing) AS avg_rating
        FROM ContestStanding S
        JOIN Users U ON S.ScreenName = U.ScreenName
        WHERE S.Division IN ('Div1', 'Div2')
        AND U.Country = %s
        GROUP BY U.Organization
        ORDER BY avg_rating DESC
        LIMIT 5;
        """

        cursor.execute(query, (country,))
        organizations = cursor.fetchall()

        if not organizations:
            print(f"No organizations found.")
            return

        print(f"Top 5 Organizations by Average Rating in {country}:")
        for org in organizations:
            organization_name, avg_rating = org
            print(f"Organization: {organization_name}, Average Rating: {avg_rating:.2f}")

    except MySQLError as e:
        print(f"Database error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_5_users_by_contest_participation_frequency():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT U.ScreenName, COUNT(DISTINCT CS.ContestName) / U.Reg_duration AS participation_frequency
        FROM Users U
        JOIN ContestStanding CS ON U.ScreenName = CS.ScreenName
        GROUP BY U.ScreenName, U.Reg_duration
        ORDER BY participation_frequency DESC
        LIMIT 5;
        """

        cursor.execute(query)
        users = cursor.fetchall()

        if not users:
            print(f"No users found.")
            return

        print("Top 5 Users by Contest Participation Frequency:")
        for user in users:
            screen_name, participation_frequency = user
            print(f"User: {screen_name}, Participation Frequency: {participation_frequency:.4f}")

    except MySQLError as e:
        print(f"Database error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_10_users_by_rating_in_divs():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT S.ScreenName, SUM(S.Standing) AS total_score
        FROM ContestStanding S
        JOIN Users U ON S.ScreenName = U.ScreenName
        WHERE S.Division IN ('Div1', 'Div2') 
        AND U.Organization LIKE %s
        GROUP BY S.ScreenName
        ORDER BY total_score DESC
        LIMIT 10;
        """

        cursor.execute(query, ('%American University in Cairo%',))
        users = cursor.fetchall()

        if not users:
            print(f"No users found.")
            return

        print("Top 10 Users from The American University in Cairo by Rating:")
        for user in users:
            screen_name, total_score = user
            print(f"User: {screen_name}, Total Score: {total_score}")

    except MySQLError as e:
        print(f"Database error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def fetch_top_5_attempted_problem_sets_from_egypt():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT PS.ProblemName, COUNT(A.AttemptID) AS attempt_count
        FROM Attempts A
        JOIN Users U ON A.ScreenName = U.ScreenName
        JOIN ProblemSets PS ON A.ProblemName = PS.ProblemName
        WHERE U.Country = %s
        GROUP BY PS.ProblemName
        ORDER BY attempt_count DESC
        LIMIT 5;
        """

        cursor.execute(query, ('Egypt',))
        problem_sets = cursor.fetchall()

        if not problem_sets:
            print(f"No problem sets found.")
            return

        print("Top 5 Most Attempted Problem Sets from Egypt:")
        for problem_set in problem_sets:
            problem_set_name, attempts_count = problem_set
            print(f"Problem Set: {problem_set_name}, Attempts Count: {attempts_count}")

    except MySQLError as e:
        print(f"Database error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def main_menu():
    while True:
        print("\nMenu:")
        print("1. Fetch attempts by name")
        print("2. Fetch competitions by writer")
        print("3. Fetch problem sets by tag")
        print("4. Fetch top 5 languages by efficiency")
        print("5. Fetch top 10 users by activity")
        print("6. Fetch top 10 users scores")
        print("7. Fetch top 5 organizations by ratings and country")
        print("8. Fetch top 5 users by contest participation frequency")
        print("9. Fetch top 10 users by rating in divs")
        print("10. Fetch top 5 attempted problem sets from Egypt")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            screen_name = input("Enter screen name: ")
            fetch_attempts_by_name(screen_name)
        elif choice == '2':
            writer = input("Enter writer name: ")
            fetch_competitions_by_writer(writer)
        elif choice == '3':
            tag = input("Enter tag: ")
            fetch_problem_sets_by_tag(tag)
        elif choice == '4':
            fetch_top_5_languages_by_efficiency()
        elif choice == '5':
            fetch_top_10_users_by_activity()
        elif choice == '6':
            fetch_top_10_users_scores()
        elif choice == '7':
            country = input("Enter country: ")
            fetch_top_5_organizations_by_ratings_and_country(country)
        elif choice == '8':
            fetch_top_5_users_by_contest_participation_frequency()
        elif choice == '9':
            fetch_top_10_users_by_rating_in_divs()
        elif choice == '10':
            fetch_top_5_attempted_problem_sets_from_egypt()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()