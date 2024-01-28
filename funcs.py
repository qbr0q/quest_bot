import json
from telebot import types

def read_data(file_name):
    with open(file_name, encoding='utf-8') as file:
        data = file.read()
        return json.loads(data)

def load_data(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file)

def get_user_id(message):
    if isinstance(message, types.User):
        return message.id
    elif isinstance(message, types.Message):
        return message.chat.id