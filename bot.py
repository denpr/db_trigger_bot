import psycopg2
import telebot
from threading import Thread
from settings import TG_TOKEN, USER_ID, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import select

bot = telebot.TeleBot(TG_TOKEN)

con = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cur = con.cursor()

# =============================================================
# cur.execute(f"""CREATE OR REPLACE FUNCTION add_task_notify()
# RETURNS trigger AS
# $BODY$

# BEGIN
# PERFORM pg_notify('new_id', NEW.ID::text);
# RETURN NEW;
# END;
# $BODY$
# LANGUAGE plpgsql VOLATILE
# COST 100;
# ALTER FUNCTION add_task_notify()
# OWNER TO frank;

# CREATE TRIGGER add_task_event_trigger
# AFTER INSERT
# ON main_incomingmessage
# FOR EACH ROW
# EXECUTE PROCEDURE add_task_notify();"""
# )
# con.commit()
# ===========================================================

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()

def db_trigger():
    cur.execute("LISTEN new_id;")
    print("Waiting a new message")
    while True:
        if select.select([con], [], [], 10) == ([], [], []):
            print("More than 10 seconds passed...")
        else:
            con.poll()
            while con.notifies:
                notify = con.notifies.pop(0)
                cur.execute(f'select * from main_incomingmessage where id = {notify.payload}')
                message = cur.fetchall()
                for row in message:
                        
                    d = row[3].strftime('%Y-%M-%d %H:%M')
                        
                    bot_message = f"""Message from Site \n
                    date: {d}\n
                    name: {row[1]}\n
                    email: {row[2]}\n
                    ---\n
                    {row[4]}"""
                    bot.send_message(USER_ID, bot_message)   

Thread(target=db_trigger, args=()).start()

# Bot dialogs
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Привет ✌️ ")






bot.infinity_polling()