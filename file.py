from flask import Flask, render_template, request,session,redirect,url_for
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import string
import secrets
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/id_cards'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root@123'
app.config['MYSQL_DB'] = 'pythonlogin'
app.secret_key = 'for_session'
mysql = MySQL(app)

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/main_dup')
def main_dup():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('login.html', msg='')

@app.route('/new_admin')
def new_admin():
    return render_template('register.html', msg='')

@app.route('/admin_registration', methods = ['GET', 'POST'])
def admin_registration():
    msg=''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['pass']
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = %s', [email])
        account = cursor.fetchone()
        if account:
            msg = 'Sorry, mail already exists!! please, register with new mail!'
            return render_template('id_style1.html',msg = msg)
        else:
            msg = "Hurray! You are now an admin."
            cursor.execute('INSERT INTO admin VALUES (NULL, %s, %s, %s,%s)', (username, email, password,"static/id_cards/"+filename))
            mysql.connection.commit()
    return render_template('register.html', msg=msg)

@app.route('/admin_user_view', methods = ['GET', 'POST'])
def admin_user_view():
    if request.method == 'POST':
        registration_id = request.form['register_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM event_registration WHERE registration_id = %s', [registration_id])
        account = cursor.fetchone()
        username = account['fname'] + " " + account["lname"]
        details_for_id_card = [username,account['mail'],account['mobile'],account['category'],account['tickets'],account['profile_pic'],account['gender'],account['registration_id']]
        return render_template('id_result.html',details = details_for_id_card, msg= 'Welcome,'+session['username'])

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('admin'))




def total_tickets(result):
    print(result,"came here")
    tickets_count = 0
    for i in range(len(result)):
        tickets_count += result[i]['tickets']
    return tickets_count

def get_modify(records):
    all_the_users = []
    for each_user in records:
        temp_storage = []
        temp_storage.append(each_user['registration_id'])
        temp_storage.append(each_user['fname']+each_user['lname'])
        temp_storage.append(each_user['category'])
        temp_storage.append(each_user['gender'])
        temp_storage.append(each_user['DATE'])
        temp_storage.append(each_user['tickets'])
        all_the_users.append(temp_storage)
    return all_the_users



@app.route('/admin_login', methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        details = []
        email = request.form['email']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = %s', [email])
        account = cursor.fetchone()
        if account:
            if account['email'] == email and account['password'] == password:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                details = []
                details.append(account['username'])
                details.append(account['profile_pic'])
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM event_registration")
                records = cursor.fetchall()
                modified_user_data = get_modify(records)
                details.append(cursor.rowcount)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT SUM(tickets) AS totalsum FROM event_registration")
                result = cursor.fetchall()
                details.append(result[0]["totalsum"])
                cursor.execute('SELECT * FROM event_registration WHERE category = %s', ["self"])
                result = cursor.fetchall()
                details.append([len(result),total_tickets(result)])
                cursor.execute('SELECT * FROM event_registration WHERE category = %s', ["group"])
                result = cursor.fetchall()
                details.append([len(result),total_tickets(result)])
                cursor.execute('SELECT * FROM event_registration WHERE category = %s', ["corporate"])
                result = cursor.fetchall()
                details.append([len(result),total_tickets(result)])
                cursor.execute('SELECT * FROM event_registration WHERE category = %s', ["others"])
                result = cursor.fetchall()
                details.append([len(result),total_tickets(result)])
                cursor.execute('SELECT * FROM `event_registration` WHERE DATE(`DATE`) = CURDATE();')
                result = cursor.fetchall()
                details.append(cursor.rowcount)
                
                return render_template('admin_home.html', details = details, results = modified_user_data)
            else:
                return render_template('login.html', msg ='Sorry. Details not found')
        else: 
            return render_template('login.html', msg ='Sorry. Details not found')
      
    return render_template('login.html', msg="Please fill in the details.")

@app.route('/registration_details')
def registration_details():
    return render_template('search.html',details = None)

@app.route('/card_details', methods = ['GET', 'POST'])
def card_details():
    account = None
    if request.method == 'POST':
        
        search_parameter = request.form['search_object']
        search_value = request.form['search_bar'].strip()
        print(search_parameter,"value here")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if search_parameter == "0":
            cursor.execute('SELECT * FROM event_registration WHERE registration_id = %s', [search_value])
            account = cursor.fetchone()
        elif search_parameter == "1":
            cursor.execute('SELECT * FROM event_registration WHERE mail = %s', [search_value])
            account = cursor.fetchone()
        else:
            cursor.execute('SELECT * FROM event_registration WHERE mobile = %s', [search_value])
            account = cursor.fetchone()
    if account:
        print(account["registration_id"],type(account["registration_id"]))
        username = account['fname'] + " " + account["lname"]
        msg = "Hi, "+ username+", This is your Event Id Card."
        details_for_id_card = [username,account['mail'],account['mobile'],account['category'],account['tickets'],account['profile_pic'],account['gender'],account['registration_id']]
        return render_template('id_result.html',details = details_for_id_card, msg= msg)
    else:
        msg = 'Sorry, Registration Details not found. If registered, Check your details again!!'
        return render_template('id_style1.html',msg = msg)



@app.route('/event_registration', methods = ['GET', 'POST'])
def event_registration():
    msg = ''
    if request.method == 'POST':
        alphabet = string.ascii_letters + string.digits
        registration_id = ''.join(secrets.choice(alphabet) for i in range(6))
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = first_name + " " + last_name
        mobile = request.form['phone']
        mail = request.form['email']
        gender = request.form['gender']
        category = request.form['subject']
        tickets = request.form['tickets']
        if category == "self":
            tickets = 1
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM event_registration WHERE mail = %s', [mail])
        account = cursor.fetchone()
        if account:
            msg = 'Sorry, mail already exists!! please, register with new mail!'
            return render_template('id_style1.html',msg = msg)
        else:
            msg = "Id Creation and Event Registration succesful"
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO event_registration VALUES (NULL, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)', (first_name, last_name, mail,mobile,gender,category,tickets,"static/id_cards/"+filename,registration_id,formatted_date))
            mysql.connection.commit()
        details_for_id_card = [username,mail,mobile,category,tickets,"static/id_cards/"+filename,gender,registration_id]
    return render_template('id_style.html',details = details_for_id_card,msg = msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)