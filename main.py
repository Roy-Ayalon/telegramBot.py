import flask
import telegramBot

app = flask.Flask(__name__)

@app.route('/')
def index():
    telegramBot.do()

if __name__ == '__main__':
    app.run()
