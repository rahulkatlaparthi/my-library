from flask import Flask
from flask import render_template
from flask import request
import models as dbHandler
import library as lib

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        idcard_number=request.form['idcard_number']
        email = request.form['email']
        password = request.form['password']
        # lib.insertuser()
        dbHandler.insertUser(idcard_number,email, password)
        user = dbHandler.retrieveUsers()
        return render_template('index.html', user=user)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
