import os
from datetime import datetime, timedelta, date

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(
    SESSION_COOKIE_NAME='session_db',
    SESSION_COOKIE_PATH='/dashboard/'
)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mylibrary.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Library(db.Model):
    book_id = db.Column(db.String(80), primary_key=True)
    user_id_card_number = db.Column(db.String(100), db.ForeignKey('user.idcard_number'))
    book_name = db.Column(db.String(80))
    issued_date = db.Column(db.String(120))
    return_date = db.Column(db.String(120))

    def __init__(self, user_id_card_number, book_name, issued_date, return_date, book_id):
        self.user_id_card_number = user_id_card_number
        self.book_name = book_name
        self.issued_date = issued_date
        self.return_date = return_date
        self.book_id = book_id


class User(db.Model):
    idcard_number = db.Column(db.String(100), primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(80))
    library = db.relationship('Library', backref='idcard_number')

    def __init__(self, idcard_number, first_name, last_name, email, password):
        self.idcard_number = idcard_number
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('idcard_number', 'first_name', 'last_name', 'email', 'password')


user_schema = UserSchema()
user_schema = UserSchema(many=True)


@app.route("/logincheck", methods=["POST"])
def loginCheck():
    idcard_number = request.json["idcard_number"]
    password = request.json["password"]

    login = User.query.filter_by(idcard_number=idcard_number, password=password).first()
    if login is not None:
        return jsonify(isError=False,
                       message="Login Success")

    return jsonify(isError=True,
                   message="Invalid Credentials")


@app.route("/registeruser", methods=['POST'])
def registeruser():
    idcard_number = request.json['idcard_number']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    password = request.json['password']
    new_user = User(idcard_number, first_name, last_name, email, password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(isError=False,
                       message="Successfully created")
    except:
        return jsonify(isError=True,
                       message="Failed to create")


class LibrarySchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('user_id_card_number', 'book_name', 'issued_date', 'return_date', 'Pending_due', 'book_id')


library_schema = LibrarySchema()
library_schema = LibrarySchema(many=True)


@app.route("/addbook", methods=['POST'])
def insertbook():
    user_id_card_number = request.json['user_id_card_number']
    book_name = request.json['book_name']
    book_id = request.json['book_id']
    # issued_date = request.json['issued_date']
    # date_time_obj = datetime.strptime(issued_date, '%d-%m-%Y')
    # new_date = date_time_obj.date() + timedelta(7)
    # return_date = new_date.strftime("%d-%m-%Y")
    x = date.today()
    issued_date = x.strftime("%d-%m-%Y")
    new_date = date.today() + timedelta(7)
    return_date = new_date.strftime("%d-%m-%Y")
    new_library = Library(user_id_card_number, book_name, issued_date, return_date, book_id)
    try:
        db.session.add(new_library)
        db.session.commit()
        return jsonify(isError=False,
                       message="Successfully created")
    except:
        return jsonify(isError=True,
                       message="Failed to create")


@app.route("/userdetails/<id>", methods=['GET'])
def getUserDetails(id):
    lib = Library.query.filter_by(user_id_card_number=id)
    result = library_schema.dump(lib)
    pending_dueV = 0
    for user in result:
        _return_time_str = user['return_date']
        _return_date = datetime.strptime(_return_time_str, '%d-%m-%Y')
        _return_millis = int(round(_return_date.timestamp() * 1000))
        _current_date = datetime.today()
        _current_millis = int(round(_current_date.timestamp() * 1000))
        if (_current_millis > _return_millis):
            diff = dateDiffInDays(_current_date, _return_date)
            pending_dueV = pending_dueV + (diff * 5)

    return jsonify(Pending_due=pending_dueV, result=result)


def dateDiffInDays(today_date, _return_date):
    delay = today_date - _return_date
    return delay.days


@app.route("/viewbook/<id>", methods=['GET'])
def viewbook(id):
    lib = Library.query.filter_by(user_id_card_number=id)
    result = library_schema.dump(lib)
    return jsonify(result)

@app.route("/viewbookid/<id>", methods=['GET'])
def viewbookid(id):
    lib = Library.query.filter_by(book_id=id)
    result = library_schema.dump(lib)
    return jsonify(result)



@app.route("/viewuser", methods=['GET'])
def viewuser():
    user = User.query.all()
    result = user_schema.dump(user)
    return jsonify(result)


@app.route("/renewal", methods=['POST'])
def renewal_book():
    user_id_card_number = request.json["user_id_card_number"]
    book_id = request.json["book_id"]
    lib = Library.query.filter_by(user_id_card_number=user_id_card_number, book_id=book_id)
    result = library_schema.dump(lib)
    lib.update(
        dict(issued_date=date.today().strftime("%d-%m-%Y"),
             return_date=(date.today() + timedelta(7)).strftime("%d-%m-%Y")))
    db.session.commit()
    return jsonify(result)
    # return result


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='127.0.0.1', port=1234)
