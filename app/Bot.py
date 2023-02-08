from telebot import types
import telebot
from Main import ParseNews , Users , Tags
from telegram_bot_pagination import InlineKeyboardPaginator
from telebot.types import InlineKeyboardButton
import data
# def get_check_news(value):
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             # Read all record
#             sql = "SELECT `Date`,`Tags` FROM `News` WHERE `Tags` = '{}'".format(value)
#             cursor.execute(sql)
#             result = cursor.fetchall()
#
#             if result:
#                 if  result[0]['Date'] < get_time_now():
#                     return 'new'
#                 else:
#                     return 'new'
#             else:
#                 return False
# def get_show_news(value):
#     '''Show news  DataBase'''
#     global connection
#
#     if get_check_news(value) == 'new':
#
#         with connection:
#             with connection.cursor() as cursor:
#                 sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
#                 cursor.execute(sql)
#                 result = cursor.fetchall()
#                 news = []
#                 for i in result:
#                     news.append((i['News'], i['Link']))
#                     connection.commit()
#                 return news
#
#     else:
#
#         with connection:
#             with connection.cursor() as cursor:
#                 get_delete_news(value)
#                 get_add_news(value)
#
#                 sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
#                 cursor.execute(sql)
#                 result = cursor.fetchall()
#                 news = []
#                 for i in result:
#                     news.append((i['News'], i['Link']))
#                     connection.commit()
#                 return news
# def get_search_news(value):
#
#     value = value.title()
#     list_news = []
#
#     # взять данные из базы сайтов
#     file = open('search.json', 'r')
#     filer = file.read()
#     dict_news = json.loads(filer)
#
#     # Установка аргументов для Chrome
#     chrome_options = Options()
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--headless")
#
#     webdriver_service = Service("chromedriver/chromedriver")
#     browser = webdriver.Chrome(service=webdriver_service,options=chrome_options)
#
#     for news in dict_news:
#
#         # Проверка кол-ва вводимых слов
#         if len(value.split()) > 1:
#             browser.get(news['site'].format('%20'.join(value.split())))
#         else:
#             browser.get(news['site'].format(value))
#
#         soup = bs(browser.page_source, 'lxml')
#
#         # browser.quit()
#         tags = news['text'].split('class_=')
#         datatags = news['date'].split('class_=')
#         res = soup.find_all(tags[0], class_=tags[1], limit=1)
#
#         for i in res:
#
#             data = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator= ' ')
#             data = datetime.strptime(data,news['formatdate']).strftime('%Y-%m-%d')
#
#             if 'http' in i.a.get('href'):
#                 list_news.append([i.a.get_text(strip=True, separator= ' '),i.a.get('href'), value,data])
#             else:
#                 link = re.match('^h.*\.(com|uk|org)', news["site"] ).group()
#                 list_news.append([i.a.get_text(strip=True, separator= ' '), link + i.a.get('href'), value,data])
#
#     return list_news
#
# def get_add_news(value):
#     list = get_search_news(value)
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             #Isert new values
#             for i in list:
#                 insert = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Date`) VALUES (%s, %s, %s, %s)"
#                 cursor.execute(insert, (i[0],i[1],i[2],i[3]))
#             connection.commit()
# def get_delete_news(value):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             sql = "DELETE FROM `News` WHERE `Tags` = '{}'".format(value)
#             cursor.execute(sql)
#             connection.commit()
#
# def get_time_now():
#     data = datetime.now().date().strftime('%Y-%m-%d')
#     return data
#
#
#
#
# def get_add_tags(value,user):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#
#             if get_check_tags(value):
#                 return False
#
#             else:
#                 sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
#                 result = cursor.execute(sql)
#                 result = cursor.fetchall()
#                 if result:
#                     result[0]['Tags'] = f"{result[0]['Tags']} {value.lower()}"
#                     print(result)
#                     sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(user[0],user[1],result[0]['Tags'])
#                     cursor.execute(sql)
#                     connection.commit()
# def get_check_tags(value, user):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
#             result = cursor.execute(sql)
#             result = cursor.fetchall()
#             if value in result[0]['Tags']:
#                 return True
#             else:
#                 return False
# def get_delete_tags(value,user):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
#             result = cursor.execute(sql)
#             result = cursor.fetchall()
#             result[0]['Tags'] = result[0]['Tags'].replace(value,"")
#             sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(user[0], user[1], result[0]['Tags'])
#             cursor.execute(sql)
#             connection.commit()
#
#
# connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
#                                  charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
#
#
bot = telebot.TeleBot('6048452494:AAFUrrPp54qBkleQW7iMZqJA4KXI_0jQkD0')

user = Users()
parse_news = ParseNews()
tag = Tags()


@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
    btn1 = types.KeyboardButton("📰 Top news")
    btn2 = types.KeyboardButton("✅ My subscriptions")
    markup.add(btn1,btn2)

    text = f"""Hello !!!\nI'm a news bot who wants to share breaking news with you"""
    bot.send_message(message.chat.id, text, parse_mode='html',reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == '✅ Subscribe')
def subscribe(call):
    user.get_add_user(call.from_user.id)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("✅ Add tag", callback_data='✅ Add tag')
    markup.add(btn1)
    text = "Enter the tag for which you want to receive news"
    mesg = bot.send_message(call.message.chat.id, text, parse_mode='html')
    bot.register_next_step_handler(mesg, add_tags_in_base)

@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def menu(call):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📰 Top news")
        btn2 = types.KeyboardButton("✅ My subscriptions")
        markup.add(btn1, btn2)

        text = f"""You are back to the main menu"""
        bot.send_message(call.message.chat.id, text, parse_mode='html', reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data == '✅ Add tag')
def add_tags(call):
    tag_add = bot.send_message(call.message.chat.id , ' Please enter a tag', parse_mode= 'HTML')
    bot.register_next_step_handler(tag_add , add_tags_in_base)
def add_tags_in_base(tag_add):
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

@bot.message_handler(func=lambda message: message.text == '📰 Top news')
def get_news(message):
    send_news_page(message)
@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='character')
def characters_page_callback(call):
    page = int(call.data.split('#')[1])
    bot.delete_message(call.message.chat.id,call.message.message_id)
    send_news_page(call.message, page)
def send_news_page(message, page=1):
    # f"<b>News:  </b>{news[0]}\n" + '<a href="{}">Source</a>'
    character_pages = [f"<b><a href='{x[1]}'>Source</a></b>" for x in parse_news.get_show_news('Germany')]
    paginator = InlineKeyboardPaginator(len(character_pages),current_page=page,data_pattern='character#{page}')
    bot.send_message(message.chat.id, character_pages[page-1],reply_markup=paginator.markup,parse_mode='HTML')



@bot.message_handler(content_types=['text'])
def get_user_text(message, page = 1):

    # if message.text == '📰 Top news':
    #     for news in parse_news.get_show_news('Germany'):
    #         text = f"<b>News:  </b>{news[0]}\n" + '<a href="{}">Source</a>'.format(news[1])
    #         bot.send_message(message.chat.id, text, parse_mode="HTML")

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



    # elif message.text == '✅ Subscribe':
    #     if user.get_check_user(message.from_user.id):
    #
    #         bot.send_message(message.chat.id, 'You are already subscribed', parse_mode='html')
    #
    #     else:
    #
    #         user.get_add_user(message.from_user.id)
    #         bot.send_message(message.chat.id, 'Subscription completed successfully,\n', parse_mode='html')
    #
    #     markup = types.InlineKeyboardMarkup()
    #     btn1 = types.InlineKeyboardButton("🏢 Personal account", callback_data='🏢 Personal account')
    #     markup.add(btn1)
    #
    #     bot.send_message(message.chat.id, 'please go to your account', parse_mode='html', reply_markup=markup)
    #
    # elif message.text == "🚫 Unsubscribe":
    #     if user.get_check_user(message.from_user.id):
    #         tag.get_all_delete_tags(message.from_user.id)
    #         user.get_delete_user(message.from_user.id)
    #
    #         bot.send_message(message.chat.id, '🚫 You have unsubscribed from the newsletter ', parse_mode='html')
    #
    #     else:
    #         bot.send_message(message.chat.id, 'You are not subscribed', parse_mode='html')



bot.polling(none_stop=True)


