from telebot import types
import telebot
from telegram_bot_pagination import InlineKeyboardPaginator
import threading
import time
from Main import ParseNews , Users , Tags, Send_Data
import schedule


bot = telebot.TeleBot('6048452494:AAFUrrPp54qBkleQW7iMZqJA4KXI_0jQkD0', num_threads=20)


@bot.message_handler(commands=['start', 'help'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
    btn1 = types.KeyboardButton("📰 Top news")
    btn2 = types.KeyboardButton("✅ My subscriptions")
    btn3 = types.KeyboardButton("📨 News without subscription")
    markup.add(btn1, btn2)
    markup.add(btn3)

    text = f"""Hello !!!\nI'm a news bot who wants to share breaking news with you"""
    bot.send_message(message.chat.id, text, parse_mode='html',reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def main(call):

    data = Send_Data()

    if call.data == "✅ Subscribe":
        user = Users()
        user.get_add_user(call.from_user.id)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("✅ Add tag", callback_data='✅ Add tag')
        markup.add(btn1)
        text = "Enter the tag for which you want to receive news"
        mesg = bot.send_message(call.message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(mesg, add_tags_in_base)

    elif call.data == "✅ Add tag":

        tag_add = bot.send_message(call.message.chat.id, ' Please enter a tag', parse_mode='HTML')
        bot.register_next_step_handler(tag_add, add_tags_in_base)

    elif call.data == "menu":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📰 Top news")
        btn2 = types.KeyboardButton("✅ My subscriptions")
        markup.add(btn1, btn2)

        text = f"""You are back to the main menu"""
        bot.send_message(call.message.chat.id, text, parse_mode='html', reply_markup=markup)

    elif call.data == "❌ Delete tag":

        tag_dell = bot.send_message(call.message.chat.id, 'Please write the news you want to delete', parse_mode='HTML')
        bot.register_next_step_handler(tag_dell, delete_tag)

    elif call.data.split('#')[0] == "world":

        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_page_top(call.message, page)

    elif call.data.split('#')[0] in data.send_tags():

        page = int(call.data.split('#')[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_news_user(call.data.split('#')[0],page, call)

@bot.message_handler(content_types=['text'])
def get_user_text(message):

    user = Users()
    tag = Tags()


    if message.text == '✅ My subscriptions':

        if user.get_check_user(message.from_user.id):
            news = '\n'.join(tag.get_show_tags(message.from_user.id))

            if news:

                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton('✅ Add tag', callback_data= '✅ Add tag')
                btn2 = types.InlineKeyboardButton('❌ Delete tag', callback_data= '❌ Delete tag')
                markup.add(btn1,btn2)
                bot.send_message(message.chat.id,f"You are subscribed to:\n{news}", parse_mode='HTML', reply_markup=markup)

            else:

                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton('✅ Add tag', callback_data= '✅ Add tag')
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


    elif message.text == "🚫 Unsubscribe":

        if user.get_check_user(message.from_user.id):
            tag.get_all_delete_tags(message.from_user.id)
            user.get_delete_user(message.from_user.id)

            bot.send_message(message.chat.id, '🚫 You have unsubscribed from the newsletter ', parse_mode='html')

        else:
            bot.send_message(message.chat.id, 'You are not subscribed', parse_mode='html')

    elif message.text == "📰 Top news":

        # send_page_top(message)
        send_news_user()
    elif message.text == "📨 News without subscription":

        news = bot.send_message(message.chat.id, 'Please enter the title of the news', parse_mode='HTML')
        bot.register_next_step_handler(news, delete_tag)


def show_news_without_subscription(news):
    pass


def add_tags_in_base(tag_add):

    tag = Tags()

    if tag.get_check_tags(tag_add.from_user.id,tag_add.text):

        tag.get_add_tags(tag_add.from_user.id, tag_add.text)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("✅ Add another tag", callback_data='✅ Add tag')
        btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='menu')
        markup.add(btn1, btn2)
        bot.send_message(tag_add.chat.id , 'You have already added a tag', parse_mode= 'HTML', reply_markup = markup)

    else:

        tag.get_add_tags(tag_add.from_user.id,tag_add.text)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("✅ Add another tag", callback_data='✅ Add tag')
        btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='menu')
        markup.add(btn1,btn2)
        bot.send_message(tag_add.chat.id, f"Tag added successfully", parse_mode="HTML",reply_markup=markup)

def delete_tag(tag_dell):

    tag = Tags()
    tag.get_delete_tags(tag_dell.from_user.id,tag_dell.text)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("❌ Delete another tag", callback_data='✅ Add tag')
    btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='menu')
    markup.add(btn1, btn2)
    bot.send_message(tag_dell.chat.id, f"Tagr removed", parse_mode="HTML", reply_markup=markup)


# def send_page_top(message, page=1):
#
#     parse_news = ParseNews()
#     pages = [f"<b>News:  </b>{x[0]}\n<b><a href='{x[1]}'>Source</a></b>" for x in parse_news.get_show_news('world')]
#     paginator = InlineKeyboardPaginator(len(pages), current_page=page, data_pattern='world#{page}')
#
#     bot.send_message(message.chat.id, pages[page-1], reply_markup=paginator.markup,parse_mode='HTML')

def dict_news():

    send_data = Send_Data()
    parse_news = ParseNews()
    news = send_data.send_data()

    dict_news = {}

    for i in news:

        for tag in i['tag']:

            pages = [f"<b>News by tag {tag}\n\nNews: {x[0]}</b>\n\n<b><a href='{x[1]}'>Source</a></b>\n\n" for x in parse_news.get_show_news(tag)]

            dict_news[tag] = pages
    return dict_news
def send_news_user(tags_news= None, page=1 , call = None):

        send_data = Send_Data()
        parse_news = ParseNews()
        tags = Tags()
        users = Users()
        news = send_data.send_data()

        link_news = dict_news()

        if not tags_news:

            for i in news:

                for tag in i['tag']:

                    try:
                            pages = [f"<b>News by tag {tag}\n\nNews: {x[0]}</b>\n\n<b><a href='{x[1]}'>Source</a></b>\n\n" for x in parse_news.get_show_news(tag)]

                            paginator = InlineKeyboardPaginator(len(pages), current_page=page,data_pattern=f"{tag}#{{page}}")
                            bot.send_message(i['id'], pages[page - 1], reply_markup=paginator.markup, parse_mode='HTML')
                            pass

                    except telebot.apihelper.ApiTelegramException as err:

                        if err.description == "Forbidden: bot was blocked by the user":
                            users.get_delete_user(i['id'])
                            tags.get_all_delete_tags(i['id'])
                            pass
        else:
            paginator = InlineKeyboardPaginator(len(link_news[tags_news]), current_page=page, data_pattern=f"{tags_news}#{{page}}")
            bot.send_message(call.message.chat.id, link_news[tags_news][page - 1], reply_markup=paginator.markup, parse_mode='HTML' )





def parse_news_from_tag():

    send_data = Send_Data()
    news = send_data.send_data()
    parse_news = ParseNews()

    for i in news:
        for tags in i['tag']:
            parse_news.get_add_news(tags)

    parse_news.get_add_news('world')

def dellete_old_news():

    parse_news = ParseNews()
    parse_news.get_delete_old_news()


def test():

    # schedule.every(25).seconds.do(send_news_user)
    schedule.every(10).seconds.do(parse_news_from_tag)
    # schedule.every(10).seconds.do(dellete_old_news)


    while True:
        schedule.run_pending()
        time.sleep(1)


# print(dict_news())
if __name__ == '__main__':

    # thr = threading.Thread(target=test, name='Daemon', daemon=True).start()
    thr1 = threading.Thread(target=bot.polling, args=(True,)).start()






