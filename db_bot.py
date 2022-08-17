import psycopg2
from psycopg2 import Error
from settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from message import Message

def db_results(sql):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                  password=DB_PASSWORD,
                                  host=DB_HOST,
                                  port=DB_PORT,
                                  database=DB_NAME)

        cursor1 = connection.cursor()
        cursor1.execute(sql)
        messages_records = cursor1.fetchall()
 
        messages = []
        for row in messages_records:
            mes = Message(message_id=row[0], name=row[1], email=row[2], date=row[3].strftime('%Y-%m-%d %H:%M'),message=row[4])
            messages.append(mes)
        return messages
    except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor1.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
