from telebot import types
import telebot
from telegram_bot_pagination import InlineKeyboardPaginator
import threading
import time
from Main import ParseNews, Users, Tags, SendData
import schedule
import logging
from logger import logging

bot = telebot.TeleBot("6048452494:AAFUrrPp54qBkleQW7iMZqJA4KXI_0jQkD0", num_threads=20)


@bot.message_handler(commands=['start', 'help'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📰 Top news")
    btn2 = types.KeyboardButton("✅ My subscriptions")
    btn3 = types.KeyboardButton("📨 News without subscription")

    markup.add(btn1, btn2)
    markup.add(btn3)

    text = f"Hello !!!\nI'm a news bot who wants to share breaking news with you"

    bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def main(call):

    user = Users()
    tag = Tags()
    data = ParseNews()

    if call.data == "✅ Subscribe":

        user = Users()
        user.get_add_user(call.from_user.id)

        markup = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton("✅ Add tag", callback_data='✅ Add tag')

        markup.add(btn1)

        text = "Enter the tag for which you want to receive news"

        tag = bot.send_message(call.message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(tag, add_tags_in_base)

    elif call.data == "✅ Add tag":

        tag_add = bot.send_message(call.message.chat.id, ' Please enter a tag', parse_mode='HTML')

        bot.register_next_step_handler(tag_add, add_tags_in_base)

    elif call.data == "menu":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn1 = types.KeyboardButton("📰 Top news")
        btn2 = types.KeyboardButton("✅ My subscriptions")
        btn3 = types.KeyboardButton("📨 News without subscription")

        markup.add(btn1, btn2)
        markup.add(btn3)

        text = f"""You are back to the main menu"""

        bot.send_message(call.message.chat.id, text, parse_mode='html', reply_markup=markup)

    elif call.data == "❌ Delete tag":

        tag_dell = bot.send_message(call.message.chat.id, 'Please write the news you want to delete', parse_mode='HTML')
        bot.register_next_step_handler(tag_dell, delete_tag)

    elif call.data == "🚫 Unsubscribe":

        if user.get_check_user(call.from_user.id):

            tag.get_all_delete_tags(call.from_user.id)
            user.get_delete_user(call.from_user.id)

            bot.send_message(call.message.chat.id, '🚫 You have unsubscribed from the newsletter ', parse_mode='html')

        else:

            bot.send_message(call.message.chat.id, 'You are not subscribed', parse_mode='html')

    elif call.data.split('#')[0] in data.get_tags_in_base():

        page = int(call.data.split('#')[1])
        # bot.delete_message(call.message.chat.id, call.message.message_id)

        send_news_user(call.data.split('#')[0], page, call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['text'])
def get_user_text(message):

    user = Users()
    tag = Tags()

    if message.text == '✅ My subscriptions':

        if user.get_check_user(message.from_user.id):
            news = '\n'.join(tag.get_show_tags(message.from_user.id))

            if news:

                markup = types.InlineKeyboardMarkup()

                btn1 = types.InlineKeyboardButton('✅ Add tag', callback_data='✅ Add tag')
                btn2 = types.InlineKeyboardButton('❌ Delete tag', callback_data='❌ Delete tag')
                btn3 = types.InlineKeyboardButton('🚫 Unsubscribe', callback_data='🚫 Unsubscribe')

                markup.add(btn1, btn2)
                markup.add(btn3)

                bot.send_message(message.chat.id, f"You are subscribed to:\n{news}",
                                 parse_mode='HTML',
                                 reply_markup=markup)

            else:

                markup = types.InlineKeyboardMarkup()

                btn1 = types.InlineKeyboardButton('✅ Add tag', callback_data='✅ Add tag')

                markup.add(btn1)

                text = 'You have not added tags, to receive news, please add a tag'

                bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

        else:

            markup = types.InlineKeyboardMarkup()

            btn1 = types.InlineKeyboardButton('✅ Subscribe', callback_data='✅ Subscribe')
            btn2 = types.InlineKeyboardButton('🚫 Unsubscribe', callback_data='🚫 Unsubscribe')

            markup.add(btn1, btn2)

            text = 'You are not subscribed to the bot, to receive news, please subscribe'

            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

    elif message.text == "📰 Top news":

        send_news_user(tags_news="World", id_user=message.chat.id)

    elif message.text == "📨 News without subscription":

        news = bot.send_message(message.chat.id, 'Please enter the title of the news,\n'
                                                 'The request may take some time.', parse_mode='HTML')

        bot.register_next_step_handler(news, show_news_without_subscription)


def show_news_without_subscription(news):

    news.text = news.text.title()
    send_news_user(news.text, id_user=news.chat.id)


def send_news_user(tags_news=None, page=None, id_user=None, message_id=None):

    send_data = SendData()
    parse_news = ParseNews()
    tags = Tags()
    users = Users()

    data_in_db = send_data.send_data()

    if not tags_news:

        for i in data_in_db['Users_tag']:

            for tag in i['tag']:

                news = parse_news.get_show_news(tag)

                if not news:

                    bot.send_message(i['id'], f"No new news for your tag - <b>{tag}</b>", parse_mode='HTML')

                else:

                    pages = [f"<b>News by tag {tag}\n\n"
                             f"{x[0]}</b>\n\n<b>" 
                             f"<a href='{x[1]}'>Source</a></b>\n\n" for x in news]

                    paginator = InlineKeyboardPaginator(len(pages),
                                                        current_page=page,
                                                        data_pattern=f"{tag}#{{page}}")
                    try:

                        bot.send_message(i['id'], pages[0], reply_markup=paginator.markup, parse_mode='HTML')

                    except telebot.apihelper.ApiTelegramException as err:

                        if err.description == "Forbidden: bot was blocked by the user":
                            users.get_delete_user(i['id'])
                            tags.get_all_delete_tags(i['id'])

    else:

        if tags_news not in data_in_db['Tags_db']:

            parse_news.get_add_news(tags_news)
            data_in_db = send_data.send_data()

        news = parse_news.get_show_news(tags_news)

        if not news:

            bot.send_message(id_user, f"No new news for your tag - <b>{tags_news}</b>", parse_mode='HTML')

        else:

            pages = [f"<b>News by tag {tags_news}\n\n" 
                     f"{x[0]}</b>\n\n<b>" 
                     f"<a href='{x[1]}'>Source</a></b>\n\n" for x in parse_news.get_show_news(tags_news)]

            paginator = InlineKeyboardPaginator(len(pages),
                                                current_page=page,
                                                data_pattern=f"{tags_news}#{{page}}")

            try:

                if not page:

                    bot.send_message(id_user, pages[0], reply_markup=paginator.markup, parse_mode='HTML')

                else:

                    bot.edit_message_text(chat_id=id_user,
                                          message_id=message_id,
                                          text=pages[page - 1],
                                          reply_markup=paginator.markup,
                                          parse_mode='HTML')

            except telebot.apihelper.ApiTelegramException as err:

                if err.description == "Forbidden: bot was blocked by the user":

                    users.get_delete_user(id)
                    tags.get_all_delete_tags(id)


def add_tags_in_base(tag_add):

    tag = Tags()

    if tag.get_check_tags(tag_add.from_user.id, tag_add.text):

        tag.get_add_tags(tag_add.from_user.id, tag_add.text)

        markup = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton("✅ Add another tag", callback_data='✅ Add tag')
        btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='menu')

        markup.add(btn1, btn2)

        bot.send_message(tag_add.chat.id, 'You have already added a tag', parse_mode='HTML', reply_markup=markup)

    else:

        tag.get_add_tags(tag_add.from_user.id, tag_add.text)

        markup = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton("✅ Add another tag", callback_data='✅ Add tag')
        btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='menu')

        markup.add(btn1, btn2)

        bot.send_message(tag_add.chat.id, f"Tag added successfully", parse_mode="HTML", reply_markup=markup)


def delete_tag(tag_dell):

    tag = Tags()
    tag.get_delete_tags(tag_dell.from_user.id, tag_dell.text)

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("❌ Delete another tag", callback_data='✅ Add tag')
    btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='menu')

    markup.add(btn1, btn2)

    bot.send_message(tag_dell.chat.id, f"Tagr removed", parse_mode="HTML", reply_markup=markup)


def get_parse_news_from_tag():

    unique_tags = Tags()
    parse_news = ParseNews()

    for tags in unique_tags.get_show_tags():

        parse_news.get_add_news(tags)

    parse_news.get_add_news('world')


def delete_old_news():

    parse_news = ParseNews()
    parse_news.get_delete_old_news()


def thread():

    schedule.every(45).minutes.do(get_parse_news_from_tag)
    schedule.every(45).minutes.do(delete_old_news)

    # Tasks by UTC
    schedule.every().day.at("10:00").do(send_news_user)
    schedule.every().day.at("18:00").do(send_news_user)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':

    thr = threading.Thread(target=thread, name='Daemon', daemon=True).start()
    logging.info("Telebot started")
    thr1 = threading.Thread(target=bot.polling, args=(True,)).start()
    logging.info("Telegram poller started")
