from flask import Flask, request

telebot = Flask(__name__)

@telebot.route('/', methods=['GET'])
def root():
    return "Processing", 200

@telebot.route('/getnews', methods=['GET'])
def main():
    from ParseNews import NewsPars
    a = NewsPars()
    return f'{a.getnews()}', 200

if __name__ == "__main__":
    telebot.run(debug=False, host='0.0.0.0', port=8081)
