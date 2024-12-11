from telebot import types

import telebot
bot = telebot.TeleBot('8117985808:AAEPmdm94_aAXIkQ7EY3A96HtDX1JD6cuyc')

initial_products = {
    1: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 1", "description": "Описание товара 1"},
    2: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 2", "description": "Описание товара 2"},
    3: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 3", "description": "Описание товара 3"},
}

current_product_index = 0

@bot.message_handler(commands=['start'])
def handle_start(message):
    global current_product_index
    show_product(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global current_product_index
    if call.data == 'yes' or call.data == 'no':
        current_product_index += 1
        if current_product_index < len(initial_products):
            show_product(call.message)

def show_product(message):
    global current_product_index
    product_id, product_data = list(initial_products.items())[current_product_index]

    image_path = product_data['image']
    with open(image_path, 'rb') as image_file:
        bot.send_photo(message.chat.id, image_file)

    text_message = f"<b>Name:</b> {product_data['name']}\n"
    text_message += f"<b>Description:</b> {product_data['description']}\n"
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Нравится', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Не нравится', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.chat.id, text_message, parse_mode="HTML", reply_markup=keyboard)
if __name__ == '__main__':
    bot.polling()