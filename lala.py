from telegram import *
from telegram.ext import *
from telegram.ext.filters import MessageFilter
import locale
import datetime
import threading
import sqlite3
import asyncio


class Date:
    start_date = None
    refresh_date = None

    def update_date(self, start=None, refresh=None):
        if start is None:
            pass
        else:
            self.start_date = start
        if refresh is None:
            self.refresh_date = self.start_date + datetime.timedelta(days=active_colivers)
        else:
            self.refresh_date = refresh

    def get_date(self):
        return [self.start_date, self.refresh_date]


def check_database():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute("create table if not exists cleaning_calendar (key text, value integer);")
    cursor.execute("""SELECT count(*) FROM cleaning_calendar""")
    data = cursor.fetchall()
    if (data[0])[0] == 0:
        return False
    else:
        return True


def restore_data():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute("select * from cleaning_calendar;")
    restored = cursor.fetchall()
    cursor.close()
    connection.close()

    cleaning_calendar.clear()
    date_data.update_date(start=datetime.datetime.strptime((restored[0])[0], '%Y-%m-%d').date())
    for day, user in restored:
        day = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        if day.weekday() == 0:
            users = user.split(',')
            conv = lambda i: i or None
            users = [conv(i) for i in users]

            cleaning_calendar.update({day: users})
        else:
            cleaning_calendar.update({day: user})

# async def get_colivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     lol = await context.bot.get_chat(chat_id=groupchat_id)
#     current_date = datetime.date.today()
#     print(Message(chat=lol, date=datetime.datetime(current_date), message_id=update.effective_message.id).new_chat_members)

def save_data():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM cleaning_calendar;')
    connection.commit()

    cursor.execute("create table if not exists cleaning_calendar (date text, username text);")
    connection.commit()

    for date, username in cleaning_calendar.items():
        if type(username) is list:
            new_username = []
            separator = ','
            for i in username:
                if i is None:
                    new_username.append('')
                else:
                    new_username.append(i)
            new_username = separator.join(new_username)
            cursor.execute("INSERT INTO cleaning_calendar (date, username) VALUES (?, ?)",
                           (date.strftime('%Y-%m-%d'), new_username))
            connection.commit()
        else:
            cursor.execute("INSERT INTO cleaning_calendar (date, username) VALUES (?, ?)",
                           (date.strftime('%Y-%m-%d'), username))
            connection.commit()

    connection.commit()
    cursor.close()
    connection.close()


async def clean_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for i in cleaning_calendar:
        if i.weekday() == 0:
            cleaning_calendar[i] = [None, None, None]
        else:
            cleaning_calendar[i] = None
    await start(update, context)


async def new_cycle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cleaning_calendar.clear()
    date_data.update_date(start=datetime.date.today())
    for i in range(active_colivers):
        date = datetime.date.today() + datetime.timedelta(days=i)
        if date.weekday() == 0:
            cleaning_calendar.update({date: [None, None, None]})
        else:
            cleaning_calendar.update({date: None})
    await start(update, context)


async def daily_task():
    if datetime.datetime.today().weekday() == 0:
        user = cleaning_calendar[datetime.datetime.today().date()]
        try:
            await application.bot.sendMessage(chat_id=groupchat_id,
                                              text=f"Сьогодні драять кухню: @{user[0]}, @{user[1]}, @{user[2]}")
        except:
            await application.bot.sendMessage(chat_id=groupchat_id,
                                              text=f"Сьогодні драять кухню: @{user[0]}, @{user[1]}, @{user[2]}")
    else:
        user = cleaning_calendar[datetime.datetime.today().date()]
        try:
            await application.bot.sendMessage(chat_id=groupchat_id, text=f"Сьогодні драє кухню: @{user}")
        except:
            await application.bot.sendMessage(chat_id=groupchat_id, text=f"Сьогодні драє кухню: @{user}")
    if datetime.date.today() == date_data.get_date()[1]:
        cleaning_calendar.clear()
        for i in range(active_colivers):
            date = datetime.date.today() + datetime.timedelta(days=i + 1)
            if date.weekday() == 0:
                cleaning_calendar.update({date: [None, None, None]})
            else:
                cleaning_calendar.update({date: None})


async def schedule_task_daily():
    while True:
        now = datetime.datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += datetime.timedelta(days=1)  # Schedule for the next day

        time_until_target = (target_time - now).total_seconds()

        await asyncio.sleep(time_until_target)
        await daily_task()

        # await asyncio.sleep(5)  # Wait for 5 seconds
        # await daily_task()


def start_scheduled_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_task_daily())


def add_new_slave(date, username):
    if datetime.date.weekday(date) == 0:
        temp = cleaning_calendar.get(date)
        appearing = temp.count(None)
        temp[3 - appearing] = username
        cleaning_calendar[date] = temp
    else:
        cleaning_calendar[date] = username


class Filter_start(MessageFilter):
    def filter(self, message):
        return 'Записатись' in message.text

class stncfn(MessageFilter):
    def filter(self, message):
        return 'stncfn' in message.text

class claun(MessageFilter):
    def filter(self, message):
        return 'claun' in message.text

class See_filter(MessageFilter):
    def filter(self, message):
        return 'Глянуть' in message.text

class Filter_all(MessageFilter):
    def filter(self, message):
        return not ('Записатись' in message.text and 'Глянуть' in message.text)

class User_data:
    def __init__(self):
        self.username = None
        self.date = None

    def get(self):
        return [self.username, self.date]

    def update(self, username, date):
        self.username = username
        self.date = date


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    yes_no_buttons = [[InlineKeyboardButton(text='Дада', callback_data='yes')], [InlineKeyboardButton(text='Треба '
                                                                                                           'зразу '
                                                                                                           'думати!',
                                                                                                      callback_data='no')]]

    await query.edit_message_text(text=f"Точно ця дата?", reply_markup=InlineKeyboardMarkup(yes_no_buttons))

async def see(update: Update, context: ContextTypes.DEFAULT_TYPE):
    table = ''
    for i in cleaning_calendar:
        table = table + str(i.strftime('%a %d %B'))
        table = table + ' : '
        table = table + str(cleaning_calendar[i])
        table = table + '\n' + '\n'
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text=f"Осьо розклад:\n\n{table}")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='Тут так не можна')
    await start(update, context)

async def success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text(text=f"Всьо, тепер ти чергуєш у {user_data.get()[0].strftime('%A %d %B')}")


async def option_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_message.chat.username

    if query.data == 'yes':
        add_new_slave(user_data.get()[0], user_data.get()[1])
        save_data()
        await success(update, context)
    elif query.data == 'no':
        await adding(update, context)
    elif datetime.datetime.strptime(query.data, '%Y-%m-%d').date() in cleaning_calendar.keys():
        user_data.update(datetime.datetime.strptime(query.data, '%Y-%m-%d').date(), user)
        await confirm(update, context)


async def adding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []

    def split(arr, size):
        arrs = []
        while len(arr) > size:
            pice = arr[:size]
            arrs.append(pice)
            arr = arr[size:]
        arrs.append(arr)
        return arrs

    for date in cleaning_calendar:
        if date.weekday() == 0 and cleaning_calendar.get(date).count(None) > 0:
            buttons.append(InlineKeyboardButton(text=date.strftime('%a %d %B'), callback_data=str(date)))
        elif cleaning_calendar.get(date) is None:
            buttons.append(InlineKeyboardButton(text=date.strftime('%a %d %B'), callback_data=str(date)))

    buttons = split(buttons, 3)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вибирай",
                                   reply_markup=InlineKeyboardMarkup(buttons), read_timeout=60)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton("Записатись")], [KeyboardButton("не хочу")], [KeyboardButton("Глянуть")]]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пора записатись в чергу чергування",
                                   reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,
                                                                    one_time_keyboard=True))


if __name__ == '__main__':
    groupchat_id = '-1001947980528'
    active_colivers = 8
    cleaning_calendar = {}
    date_data = Date()
    user_data = User_data()

    locale.setlocale(locale.LC_TIME, 'uk_UA')
    date_format = locale.nl_langinfo(locale.D_FMT)

    if check_database() is True:
        restore_data()
    else:
        temp = datetime.datetime.today() + datetime.timedelta(days=active_colivers)
        date_data.update_date(start=datetime.datetime.today().date(), refresh=temp.date())

    application = ApplicationBuilder().token('6106699482:AAHBxhx1GF4GVD8CgaUrhXCebVzmcpeJrDU').build()
    # Start the thread


    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(option_button))
    application.add_handler(MessageHandler(Filter_start(), adding))
    application.add_handler(MessageHandler(See_filter(), see))
    application.add_handler(MessageHandler(stncfn(), new_cycle))
    application.add_handler(MessageHandler(claun(), clean_users))
    application.add_handler(MessageHandler(Filter_all(), error))

    t = threading.Thread(target=start_scheduled_task)
    t.start()
    # task_thread = threading.Thread(target=run_daily_task)
    # task_thread.start()
    application.run_polling()

    # updater.dispatcher.add_handler(MessageHandler(Filters.text, adding))
    # updater.dispatcher.add_handler(KeyboardButton(text=" LAla", request_location=pol()))
    # updater.start_polling()
