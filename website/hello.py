from flask import Flask, render_template
from flask import request
from flask import jsonify

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/foo', methods=['GET', 'POST'])
def foo():
    if request.method == 'POST':
        print("It worked")
        raw_data = request.get_data()
        json_data = jsonify(request.get_json())
        print(raw_data)
    else:
        print("failed")
    return raw_data


if __name__ == "__main__":
    app.run(debug=True)
