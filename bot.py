import psycopg2
import telebot
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

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()

cur.execute("LISTEN new_id;")
print("Waiting for notifications on channel 'new_id'")

while True:
    if select.select([con], [], [], 10) == ([], [], []):
        print("More than 10 seconds passed...")
    else:
        con.poll()
        while con.notifies:
            notify = con.notifies.pop(0)
            print(f"Got NOTIFY: {notify.channel} - {notify.payload}")
            postgresql_select_query = f'select * from main_incomingmessage where id = {notify.payload}'
            print(type(notify.payload))
            cur.execute(postgresql_select_query)
            mobile_records = cur.fetchall()
            for row in mobile_records:
                bot_message = f"Message from {row[1]}\nemail: {row[2]}\n---\n{row[4]}"
                bot.send_message(USER_ID, bot_message)