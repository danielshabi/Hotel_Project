from flask import Flask

app = Flask(__name__)


@app.route("/")
def root():
    return "<h1 style='color:blue'>Hello There!</h1>"


app.run(host='0.0.0.0')
