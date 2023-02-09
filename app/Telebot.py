from flask import Flask, request

telebot = Flask(__name__)

@telebot.route('/', methods=['GET'])
def root():
    return "Processing", 200

@telebot.route('/getnews', methods=['GET'])
def main():
    from Main import ParseNews
    if request.args and 'q' in request.args:
        q = request.args.get("q")
        a = ParseNews()
        return f'{a.get_show_news(q)}', 200
    else:
        return f'Go f*ck yourself!', 403

if __name__ == "__main__":
    telebot.run(debug=False, host='0.0.0.0', port=8081)
