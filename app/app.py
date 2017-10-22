from flask import Flask
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
from flask_prometheus import monitor 
from slackclient import SlackClient
import http.client

#used for sending data to slack bot when task is added
BOT_NAME = ''
SLACK_TOKEN = ''
BOT_ID = ''
slack_client = SlackClient(SLACK_TOKEN)

#Used for send message to discord webhook when a task is added 
DC_WEBHOOK = ''

conn = http.client.HTTPSConnection("discordapp.com")
payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n Task Added \r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
headers = {
    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    'cache-control': "no-cache",
    'postman-token': "cf7dc5f7-c1bf-597c-6e74-2394d3aa3343"
    }


#used for accessing the sql server
mysql = MySQL()
app = Flask(__name__) 
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_HOST'] = ''
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
	con = connect()
	title = request.form['taskTitle']
	body = request.form['taskBody']
	name = request.form['userName']
	con.execute('''insert into tasks(taskTitle, taskBody, userName) values(%s,%s,%s)''', (title, body, name))
	mysql.connection.commit()

	#used to send the message to the discord webhook
	conn.request("POST", DC_WEBHOOK, payload, headers)
	res = conn.getresponse()
	data = res.read()
	print(data.decode("utf-8"))

	#used to send the message to the slack bot
	#slack_client.rtm_connect()
	#slack_client.api_call("chat.postMessage", channel="#general", text="Task Added", as_user=True) 
	return list()

@app.route('/delete')
def delete():
	return render_template('delete.html')

@app.route('/delete-db', methods=['POST'])
def delete2():
	con = connect()
	id = request.form['taskID']
	con.execute('''delete from tasks where taskID = %s''',(id))
	mysql.connection.commit()

	return list()

@app.route('/update')
def update():
	return render_template('update.html')

@app.route('/update-db', methods=['POST'])
def update2():
	con = connect()
	title = request.form['taskTitle']
	body = request.form['taskBody']
	user = request.form['userName']
	id = request.form['taskID']

	con.execute('''update tasks set taskTitle = %s, taskBody = %s, userName = %s where taskID = %s''',(title,body,user,id))
	mysql.connection.commit()
	return list()

def connect():
	con = mysql.connection.cursor()
	return con

if __name__ == "__main__":
	monitor(app, port=8000)
	app.run(host='0.0.0.0', port='5000')
