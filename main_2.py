import os
from dotenv import load_dotenv
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DB_NAME')
app.config["SECRET_KEY"] = os.getenv('FLASK_SECRET_KEY')
japw = os.getenv('USER_JA_PW')
jspw = os.getenv('USER_JS_PW')

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy()

class users(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(250), unique=True, nullable=False)
	password = db.Column(db.String(250), nullable=False)
	
class gastos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fecha = db.Column(db.Date())
	costo = db.Column(db.Float())
	tipo = db.Column(db.String(100))
	persona = db.Column(db.String(20))

db.init_app(app)

with app.app_context():
	
	db.create_all()

	admin = users(username='James', password=japw)
	guest = users(username='Javi', password=jspw)
	
	exists = bool(db.session.query(users).filter_by(username='James').first())
	exists_guest = bool(db.session.query(users).filter_by(username='Javi').first())
	
	if exists != True:
		db.session.add(admin)
		db.session.commit()
	
	if exists_guest != True:
		db.session.add(guest)
		db.session.commit()

@app.route("/")
def home():
	return render_template("home_2.html", current_user=current_user, title="Home")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		user = users.query.filter_by(
			username=request.form.get("username")).first()
		if user.password == request.form.get("password"):
			login_user(user)
			return redirect(url_for("home"))
	return render_template("login_2.html", title="Login")

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))

@login_manager.user_loader
def loader_user(user_id):
	return users.query.get(user_id)

@app.route("/registered_gasto")
def registered_gasto():
	return render_template("registered_gasto_2.html", title="Gasto Registrado")

@app.route('/escribir_gasto', methods=['GET', 'POST']) 
def escribir(): 
	if request.method == 'POST':
		fecha_ = request.form['fecha']
		fecha_python = datetime.strptime(fecha_, "%d/%m/%Y").date()
		costo_ = request.form['costo']
		tipo_ = request.form['tipo']
		persona_ = request.form['persona']
		# if current_user.username == "James":
		# 	persona_ = "James"
		# elif current_user.username == "Javi":
		# 	persona_ = "Javi"
		new_gasto = gastos(fecha=fecha_python, costo=costo_, tipo=tipo_, persona=persona_)
		db.session.add(new_gasto)
		db.session.commit()
		return redirect(url_for("registered_gasto")) 
	return render_template("escribir_gasto_2.html", title="Registrar Gasto")


@app.route('/leer_gastos', methods=["GET"])
def leer():
	all_gastos = gastos.query.all()
	# Format data for the Plotly table
	column_names = ['Fecha', 'Costo', 'Tipo', 'Persona']  # Adjust column names as per your model
	data = [[gasto.fecha, gasto.costo, gasto.tipo, gasto.persona] for gasto in all_gastos]
	df = pd.DataFrame(data, columns=column_names)
	
	return render_template("leer_gastos_2.html", gastos=all_gastos, title="Consultar Gastos")

@app.route('/deleted_gasto')
def deleted_gasto():
	return render_template("deleted_gasto_success.html")

@app.route('/unsuccesful_delete_gasto')
def unsuccesful_delete_gasto():
	return render_template("deleted_gasto_unsuccessful.html")

@app.route('/delete_row/<int:gasto_id>', methods=['GET','POST'])
def delete_row(gasto_id):
    # Delete the row from the database based on the row_id
	record = gastos.query.get(gasto_id)
    # Check if the record exists
	if record:
		db.session.delete(record)
		db.session.commit()
		return redirect(url_for("deleted_gasto")) 
	else: 
		return redirect(url_for("unsuccesful_delete_gasto")) 

if __name__ == "__main__":
	app.run()
