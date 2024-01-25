import telebot
from telebot import custom_filters


bot = telebot.TeleBot("6106699482:AAHBxhx1GF4GVD8CgaUrhXCebVzmcpeJrDU")



# Chat id can be private or supergroups.
# @bot.message_handler(chat_id=[-867485648], commands=['start']) # chat_id checks id corresponds to your list or not.
# def admin_reply(message):
#     bot.send_message(message.chat.id, "You are allowed to use this command.")
#     while(True):
#         bot.send_message(message.chat.id, "Allowed to receive an auto-message every 30 seconds.", time.sleep(30))
def start_over():
        bot.send_message(chat_id='@Vsrt_vinykBot', text='/start')
        bot.close()

def usual(user):
        bot.send_message(chat_id='-867485648', text=f"Сьогодні драє кухню: @{user}")
        bot.close()
def monday(user):
        bot.send_message(chat_id='-867485648', text=f"Сьогодні драять кухню: @{user[0]}, @{user[1]}, @{user[2]}")
        bot.close()
# Do not forget to register
bot.add_custom_filter(custom_filters.ChatFilter())
bot.polling(none_stop=True)