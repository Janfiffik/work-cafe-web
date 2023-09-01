import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import StringField, SubmitField
from flask_bootstrap import Bootstrap

db_path = "instance/cafes.db"

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "hfdav4a5dfvsafdgSD4VSDVASZXCSDFBVsgsdfv"
Bootstrap(app)

db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    map_url = db.Column(db.String(200), unique=True)
    img_url = db.Column(db.String(200), unique=True)
    location = db.Column(db.String(200), unique=True)
    has_sockets = db.Column(db.Integer, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "map_url": self.map_url, "img_url": self.img_url,
                "location": self.location, "has_sockets": self.has_sockets, "has_toilet": self.has_toilet,
                "has_wifi": self.has_wifi, "can_take_calls": self.can_take_calls, "seats": self.seats,
                "coffee_price": self.coffee_price}

db.create_all()


class NewCafe(FlaskForm):
    name = StringField("name:")
    map_url = StringField("Google maps address:")
    img_url = StringField("Image address:")
    location = StringField("Location: ")
    has_sockets = StringField("Has sockets:")
    has_toilet = StringField("Has toilet: ")
    has_wifi = StringField("Has WiFi: ")
    can_take_calls = StringField("Can take calls: ")
    seats = StringField("Number of seats:")
    coffee_price = StringField("Average price:")
    submit = SubmitField("Add new cafe")


def str_to_bool(arg_from_url):
    if arg_from_url in ["True", "true", "T", 't', "yes", "Yes", "y", "Y", "1", "Ano", "ano", 'ma', "Ma"]:
        return True
    else:
        return False


@app.route("/", methods=["POST", "GET"])
def home():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = "SELECT * FROM cafe"
    cursor.execute(query)
    results = cursor.fetchall()
    year = datetime.now().year

    return render_template("index.html", cafes=results, year=year)


@app.route("/new_cafe", methods=["POST", "GET"])
def add_cafe():
    form = NewCafe()
    if form.validate_on_submit():
        name = form.name.data
        map_url = form.map_url.data
        img_url = form.img_url.data
        location = form.location.data
        sockets = str_to_bool(form.has_sockets.data)
        toilets = str_to_bool(form.has_toilet.data)
        wifi = str_to_bool(form.has_wifi.data)
        calls = str_to_bool(form.can_take_calls.data)
        seats = form.seats.data
        price = form.coffee_price.data
        new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location,
                        has_sockets=sockets, has_toilet=toilets, has_wifi=wifi,
                        can_take_calls=calls, seats=seats, coffee_price=price)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect("/")

    return render_template("new_cafe.html", form=form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    cafe_id = request.args.get("id")
    cafe = Cafe.query.get(cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect("/")


@app.route("/filter", methods=["GET", "POST"])
def filter_cafe():
    filter_param = request.args.get("filter")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = f"SELECT * FROM cafe ORDER BY {filter_param} DESC NULLS LAST"
    cursor.execute(query)
    results = cursor.fetchall()

    return render_template("index.html", cafes=results)

if __name__ == "__main__":
    app.run(debug=True)
