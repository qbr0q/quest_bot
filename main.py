import telebot
from funcs import *
from config import API

bot = telebot.TeleBot(API)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    user_data = read_data('JSON/users_data.json')
    if user_id not in user_data:
        user = user_data[user_id]
        user['location'] = "location1"
        load_data(user_data, 'JSON/users_data.json')
    first_name = message.from_user.first_name
    username = message.from_user.username
    name = first_name if first_name else username

    bot.send_message(message.chat.id, f'привет, {name}')
    quest(message, str(message.chat.id))


def quest(message, user_id):
    user_data = read_data('JSON/users_data.json')
    user = user_data[user_id]
    locations = read_data('JSON/locations.json')
    location = locations[user['location']]
    location_image = open(location['image'], 'rb')
    location_options = location['options']
    location_text = location['text']
    markup = types.InlineKeyboardMarkup()
    for option in location_options:
        markup.add(types.InlineKeyboardButton(option, callback_data=option))
    msg = bot.send_photo(user_id, location_image, location_text, reply_markup=markup)
    user['message_id'] = msg.id
    load_data(user_data, 'JSON/users_data.json')

@bot.message_handler(commands=['restart'])
def restart(message):
    user_data = read_data('JSON/users_data.json')
    user_id = str(get_user_id(message))
    user = user_data[user_id]
    user['location'] = 'location1'
    load_data(user_data, 'JSON/users_data.json')
    quest(message, user_id)

@bot.callback_query_handler(func = lambda call: True)
def call_data(call):
    if call.data == 'restart-bot':
        restart(call.from_user)
    else:
        user_data = read_data('JSON/users_data.json')
        user = user_data[str(call.message.chat.id)]
        locations = read_data('JSON/locations.json')
        user_location = user['location']
        try:
            user['location'] = locations[user_location]['options'][call.data]
        except:
            bot.send_message(call.message.chat.id, 'Ваш запрос уже обрабатывается...')
        else:
            user['location'] = locations[user_location]['options'][call.data]
            load_data(user_data, 'JSON/users_data.json')
            edit_quest_mess(call.message)

def edit_quest_mess(message):
    user_data = read_data('JSON/users_data.json')
    user = user_data[str(message.chat.id)]
    locations = read_data('JSON/locations.json')
    location = locations[user['location']]
    message_id = user['message_id']
    location_options = location['options']
    location_text = location['text']
    location_image = types.InputMediaPhoto(open(location['image'], 'rb'),
                                           caption=location_text)
    markup = types.InlineKeyboardMarkup()
    for option in location_options:
        markup.add(types.InlineKeyboardButton(option, callback_data=option))
    if markup.keyboard:
        bot.edit_message_media(message_id=message_id, chat_id=message.chat.id,
                               media=location_image, reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
            'Перезапуск', callback_data='restart-bot')
        )
        bot.edit_message_media(message_id=message_id, chat_id=message.chat.id,
                               media=location_image, reply_markup=markup)

bot.polling()