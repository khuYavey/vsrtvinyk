import locale
import datetime
import schedule
import threading
import time

import sqlite3
import pprint


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


# def restore_data():
#     file = open('data.txt', 'r')
#     for i in file.readlines():
#         if i.find("Start date=") != -1:
#             temp = i.split("=")
#             temp[1] = temp[1].replace('\n','')
#             date_data.update_date(start=datetime.datetime.strptime(temp[1], '%Y-%m-%d').date())
#         else:
#             calendar_temp = i.split('=')
#             calendar_temp[1] = calendar_temp[1].replace('\n', '')
#             cleaning_calendar.update({datetime.datetime.strptime(calendar_temp[0], '%Y-%m-%d').date(): calendar_temp[1]})
#
#
# def save_data():
#     file = open("data.txt", 'w')
#     for i in cleaning_calendar:
#         file.write(str(i.strftime('%Y-%m-%d')))
#         file.write("=")
#         file.write('' if cleaning_calendar.get(i) is None else cleaning_calendar.get(i))
#         file.write("\n")
#     file.close()
#

def weekly_task():
    # Send message in chat
    print("Running weekly task...")
    if datetime.date.today() == date_data.get_date()[1]:
        cleaning_calendar.clear()
        for i in range(active_colivers):
            date = datetime.date.today() + datetime.timedelta(days=i)
            if date.weekday() == 0:
                cleaning_calendar.update({date.strftime('%a %d %B'): [None, None, None]})
            cleaning_calendar.update({date.strftime('%a %d %B'): None})


def run_weekly_task():
    # Schedule the weekly_task function to run every Monday at 9:00 AM
    # schedule.every().day.at("09:00").do(weekly_task)
    schedule.every(10).seconds.do(weekly_task)
    # Keep running scheduled tasks until the program is terminated
    while True:
        schedule.run_pending()
        time.sleep(50)


active_colivers = 22
cleaning_calendar = {}
date_data = Date()

locale.setlocale(locale.LC_TIME, 'uk_UA')
date_format = locale.nl_langinfo(locale.D_FMT)


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
            cleaning_calendar.update({day: users})
        else:
            cleaning_calendar.update({day: user})

def save_data():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()


    cursor.execute('DELETE FROM cleaning_calendar;')
    connection.commit()

    cursor.execute("create table if not exists cleaning_calendar (key text, value integer);")
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

# if open('data.txt', 'r').read().find("Start date=") != -1:
#     restore_data()
# else:
temp = datetime.datetime(year=2023, month=6, day=27) + datetime.timedelta(days=active_colivers)
date_data.update_date(start=datetime.datetime(year=2023, month=6, day=27).date(), refresh=temp.date())

# Create a new thread for running the weekly task
task_thread = threading.Thread(target=run_weekly_task)

# Start the thread
task_thread.start()

buttons = []
for i in range(active_colivers):
    date = date_data.get_date()[0] + datetime.timedelta(days=i)
    if cleaning_calendar.get(date) is None:
        buttons.append(date.strftime('%a %d %B'))

for i in range(active_colivers):
    names = ["Nick",  "Colin",  "Ava",  "Ethan",  "Olivia",  "Liam",  "Sophia",  "Benjamin",  "Emma",  "Mason",
               "Isabella",  "Logan",  "Mia",  "Lucas",  "Harper",  "Henry",  "Amelia",  "Jackson",  "Charlotte",
               "Samuel", "Grace",  "Michael"]
    date = datetime.date.today() + datetime.timedelta(days=i)
    if date.weekday() == 0:
        cleaning_calendar.update({date: [None, None, None]})
    else:
        cleaning_calendar.update({date: None})
save_data()
pprint.pprint(cleaning_calendar)
# Create the table
