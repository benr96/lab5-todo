from flask import Flask
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
from flask_prometheus import monitor 
mysql = MySQL()
app = Flask(__name__)
# My SQL Instance configurations 
# Change the HOST IP and Password to match your instance configurations
 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'myroot'
app.config['MYSQL_DB'] = 'todo'
app.config['MYSQL_HOST'] = '35.195.36.57'
mysql.init_app(app)


@app.route('/')
def home():
	return render_template('index.html')

@app.route('/list')
def list():
	con = connect()
	con.execute('''select * from tasks''')
	res = con.fetchall()
	return render_template('list.html', data = str(res))

@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/add-db', methods=['POST'])
def add2():
	con = mysql.connection.cursor()
	title = request.form['taskTitle']
	body = request.form['taskBody']
	name = request.form['userName']
	con.execute('''insert into tasks(taskTitle, taskBody, userName) values(%s,%s,%s)''', (title, body, name))
	mysql.connection.commit()
	return list()

@app.route('/delete')
def delete():
	return render_template('delete.html')

@app.route('/delete-db', methods=['POST'])
def delete2():
	con = mysql.connection.cursor()
	id = request.form['taskID']
	con.execute('''delete from tasks where taskID = %s''',(id))
	mysql.connection.commit()
	return list()

@app.route('/update')
def update():
	con = connect()
	return render_template('update.html')

def connect():
	con = mysql.connection.cursor()
	return con

if __name__ == "__main__":
        monitor(app, port=8000)
        app.run(host='0.0.0.0', port='5000')
