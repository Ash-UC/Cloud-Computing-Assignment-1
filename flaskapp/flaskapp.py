from flask import Flask, render_template, redirect, url_for, request
from flaskext.mysql import MySQL
from werkzeug import secure_filename
from collections import Counter
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/ubuntu/flaskapp/uploads' 

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'ubuntu'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'CloudComputing'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/validatedata', methods=['POST'])
def validatedata():
    error = None
    conn = mysql.connect()
    cursor = conn.cursor()
    userName = request.form['username']
    password = request.form['password']
    query = ("SELECT user_password FROM user_table WHERE user_name = %s")
    cursor.execute(query,userName)
    data = cursor.fetchall()
    if len(data) is 0:
        return render_template('login.html', error = 'User Name not found. Please sign up as a new user.')
    dbPassword = data[0][0]
    cursor.close()
    conn.close()
    if request.method == 'POST':
        if password == dbPassword:
	    return showdetails()
        else:
    	    return render_template('login.html', error = 'Invalid Credentials. Please try again.')  

@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')

@app.route('/storedata', methods=['POST'])
def storedata():
    success = None
    error = None
    firstName = request.form['firstname']
    lastName = request.form['lastname']
    email = request.form['email']
    userName = request.form['username']
    password = request.form['password']
    passwordRepeat = request.form['passwordrepeat']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('sp_createUser',(firstName,lastName,email,userName,password))
    data = cursor.fetchall()
    if len(data) is 0:
    	conn.commit()
        cursor.close()
        conn.close()
    	return render_template('login.html', success = 'User Created Successfully! Please Login.')
    else:
    	return render_template('signup.html', error = 'Something Went Wrong! Please Retry.')
        cursor.close()
        conn.close()

def showdetails():
    conn = mysql.connect()
    cursor = conn.cursor()
    userName = request.form['username']
    password = request.form['password']
    query = ("SELECT * FROM user_table WHERE user_name = %s")
    cursor.execute(query,userName)
    data = cursor.fetchall()
    firstName = data[0][1]
    lastName = data[0][2]
    email = data[0][3]
    cursor.close()
    conn.close()
    return render_template('userdetails.html', firstName=firstName, lastName=lastName, email=email)

@app.route('/uploader', methods = ['GET','POST'])
def uploader():

   if request.method == 'POST':
      f = request.files['file']
      if f.filename == '':
         return redirect(request.url)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

      with open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)), 'r') as file:
         data = file.read().replace('\n', '')

      input_counter = Counter(data)
      response = []
      for letter, count in input_counter.most_common():
          response.append('"{}": {}'.format(letter, count))
      return '<br>'.join(response)

   return 'Please go back and choose a file before submitting'

if __name__ == '__main__':
  app.run(debug=True)
