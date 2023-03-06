import datetime
import math
import pandas as pd
import random
import os
PORT = int(os.environ.get('PORT', 5000))

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

STATE = None
NAME = 1
TIME = 2
INGRID = 3
TYPE = 4
LINK = 5
START = 6
reply_keyboard = [['/get_yummy', '/add_yummy']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
time_markup = ReplyKeyboardMarkup([['<10', '15'], ['30', '>30']],
                                    one_time_keyboard=True)
type_markup = ReplyKeyboardMarkup([['Snack', 'Breakfast'], ['Lunch', 'Dinner']],
                                    one_time_keyboard=True)
link_markup = ReplyKeyboardMarkup([['N/A']],
                                    one_time_keyboard=True)

#-----DB------------------------------------------------------------------------
def read_csv_to_data():
    '''upload db data to a table'''
    #data = pd.DataFrame()
    data = pd.read_csv('Menu_Bot.csv')
    return data

def save_csv(data):
    '''save data to the db'''
    data.to_csv('Menu_Bot.csv', index=False)

def add_recipe(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Hi {first_name}, lets add!")
    start_getting_info(update, context)
#-----/DB-----------------------------------------------------------------------

#------Start--------------------------------------------------------------------
def start(update, context):
    global STATE
    STATE = None
    update.message.reply_text('Now if you press /get_yummy the bot will choose randomly one dish from global list or you can add to this list something.')
#-----/Start--------------------------------------------------------------------

#-----MENU----------------------------------------------------------------------
def one_random(update, context):
    '''randomly choose breackfast/diner/supper from all db'''
    data = pd.DataFrame()
    data = read_csv_to_data()
    r_num = data.index.max()
    num = random.randint(0, r_num)
    data = data.iloc[num]
    Name = data['Name']
    Link = data['Link']
    Time = data['Time']
    update.message.reply_text(f'See your yummy one:\n\n{Name}\nTime: {Time} min.\n{Link}\n')

def week(update, context):
    update.message.reply_text("This is your weekly menu: ...")

#-----/MENU---------------------------------------------------------------------

#-----BOT-----------------------------------------------------------------------
def start_getting_info(update, context):
    global STATE
    STATE = NAME
    update.message.reply_text("Give me the Name:")

def getting_name(update, context):
    global STATE
    try:
        name = update.message.text
        context.user_data['Name'] = name
        update.message.reply_text(
                                f"ok, got your name = {name}, now - Time",
                                reply_markup=time_markup)
        STATE = TIME
    except:
        update.message.reply_text(
            "it's funny but it doesn't seem to be correct...")

def getting_time(update, context):
    global STATE
    try:
        time = update.message.text
        context.user_data['Time'] = time
        update.message.reply_text(
                            f"ok, got your Time = {time}, ingridients, please")
        STATE = INGRID
    except:
        update.message.reply_text(
            "it's funny but it doesn't seem to be correct...")

def getting_ing(update, context):
    global STATE
    try:
        ingridients = update.message.text
        context.user_data['Ingrid'] = ingridients
        update.message.reply_text(
                        f'Got your ingridients: "{ingridients}", type, please.',
                        reply_markup=type_markup)
        STATE = TYPE
    except:
        update.message.reply_text(
            "it's funny but it doesn't seem to be correct...")

def getting_type(update, context):
    global STATE
    try:
        type = update.message.text
        context.user_data['Type'] = type
        update.message.reply_text(
                        f'Got your type: "{type}", do you have a link?',
                        reply_markup=link_markup)
        STATE = LINK
    except:
        update.message.reply_text(
            "it's funny but it doesn't seem to be correct...")

def getting_link(update, context):
    global STATE
    data = pd.DataFrame()
    data = read_csv_to_data()
    ID = data.index.max() + 1
    try:
        link = update.message.text
        context.user_data['Link'] = link
        data.loc[ID] = [update.message.chat_id,
                        context.user_data['Name'],
                        context.user_data['Time'],
                        context.user_data['Ingrid'],
                        context.user_data['Type'],
                        context.user_data['Link']]
        save_csv(data)
        STATE = START
        update.message.reply_text(
                        f'New recipt has been added. Retern to start.',
                        reply_markup=markup)
    except:
        update.message.reply_text(
            "it's funny but it doesn't seem to be correct...")
    if STATE == LINK:
        return getting_link(update, context)
def error(update, context):
    update.message.reply_text("There are some errors ...")

def text(update, context):
    global STATE
    if STATE == NAME:
        return getting_name(update, context)
    if STATE == TIME:
        return getting_time(update, context)
    if STATE == INGRID:
        return getting_ing(update, context)
    if STATE == TYPE:
        return getting_type(update, context)
    if STATE == LINK:
        return getting_link(update, context)
    if STATE == START:
        return start(update, context)

def close_keyboard(bot, update):
    update.message.reply_text('Ok', reply_markup=ReplyKeyboardRemove())

def main():

    TOKEN = "5415165066:AAGF0e4io5lbwdYzdMpGBkCjJNAw393M8Iw"
    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler('close', close_keyboard))
    dispatcher.add_handler(CommandHandler("get_yummy", one_random))
    dispatcher.add_handler(CommandHandler("week", week))
    dispatcher.add_handler(CommandHandler("add_yummy", add_recipe))
    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # add an handler for errors
    dispatcher.add_error_handler(error)
    # start your shiny new bot
    #updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://boiling-river-35184.herokuapp.com/' + TOKEN)
    # run the bot until Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
