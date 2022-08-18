from ast import Import
import psycopg2
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from threading import Thread
from settings import TG_TOKEN, USER_ID, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from psycopg2 import Error
from message import Message


from db_bot import db_results

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import select

fire = u'\U0001F525'
user = u'\U0001F64D'
clock = u'\U0001F570'
email = u'\U0001F4E7'
incom = u'\U0001F4E9'


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
                        
                    d = row[3].strftime('%Y-%m-%d %H:%M')
                        
                    bot_message = f"Message from Site \ndate: {d}\nname: {row[1]}\nemail: {row[2]}\n---\n{row[4]}"
                    bot.send_message(USER_ID, bot_message)   

Thread(target=db_trigger, args=()).start()

@bot.message_handler(commands=['app'])
def staff_app(message):
    if message.chat.id != USER_ID:
        print('Доступ закрыт')
    else:
        print('Доступ разрешён')
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = KeyboardButton('Меню')
        keyboard.add(button1)
        step0 = bot.send_message(message.chat.id, 'Приветствуем!!!', reply_markup=keyboard)
        bot.register_next_step_handler(step0, step1)

def step1(message):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton('10 последних сообщений')
    button2 = KeyboardButton('Все сообщения')
    keyboard.add(button1, button2)
    step1 = bot.send_message(message.chat.id, 'Menu', reply_markup=keyboard)
    bot.register_next_step_handler(step1, step2)

def step2(message):
    sql = ''
    if message.text == "10 последних сообщений":
        sql = 'SELECT * FROM (SELECT * FROM main_incomingmessage ORDER BY id DESC LIMIT 10) t ORDER BY id;'
    elif message.text == 'Все сообщения':
        sql = 'SELECT * FROM main_incomingmessage'
    elif(message.text == 'Сообщения за месяц'):
        pass

    messages = db_results(sql)
    if messages:
        for el in messages:
            bot.send_message(USER_ID, f'id = {el.message_id}\n-------\n{clock} {el.date}\n{user} {el.name}\n{email} {el.email}\n{incom} {el.message}')
    else:
        bot.send_message(USER_ID, 'Сообщений не найдено.')

bot.infinity_polling()