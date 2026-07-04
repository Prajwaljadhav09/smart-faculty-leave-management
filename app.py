from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# Secret Key

app.secret_key = 'secretkey'

# MySQL Configuration

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Praja@7891'
app.config['MYSQL_DB'] = 'smart_autofaculty_system'

mysql = MySQL(app)

# HOME PAGE

@app.route('/')
def home():
return render_template('login.html')

# LOGIN

@app.route('/login', methods=['POST'])
def login():

```
email = request.form['email']
password = request.form['password']

cur = mysql.connection.cursor()

cur.execute("""
    SELECT *
    FROM faculty
    WHERE email=%s AND password=%s
""", (email, password))

user = cur.fetchone()

cur.close()

if user:

    session['loggedin'] = True
    session['faculty_id'] = user[0]
    session['name'] = user[1]
    session['email'] = user[2]

    return redirect('/dashboard')

return "Invalid Email or Password"
```

# DASHBOARD

@app.route('/dashboard')
def dashboard():

```
if 'loggedin' not in session:
    return redirect('/')

return render_template(
    'dashboard.html',
    faculty_name=session['name']
)
```

# APPLY LEAVE PAGE

@app.route('/apply_leave')
def apply_leave():

```
if 'loggedin' not in session:
    return redirect('/')

return render_template('apply_leave.html')
```

# SUBMIT LEAVE

@app.route('/submit_leave', methods=['POST'])
def submit_leave():

```
if 'loggedin' not in session:
    return redirect('/')

faculty_name = session['name']
leave_date = request.form['leave_date']
reason = request.form['reason']

day_name = datetime.strptime(
    leave_date,
    "%Y-%m-%d"
).strftime("%A")

cur = mysql.connection.cursor()

# Save Leave Request
cur.execute("""
    INSERT INTO leave_requests
    (faculty_name, leave_date, reason, status)
    VALUES (%s,%s,%s,%s)
""", (
    faculty_name,
    leave_date,
    reason,
    'Pending'
))

mysql.connection.commit()

# Find Faculty Lectures
cur.execute("""
    SELECT time_slot, subject_name
    FROM timetable
    WHERE faculty_name=%s
    AND day=%s
""", (
    faculty_name,
    day_name
))

lectures = cur.fetchall()

suggestions = []

# Find Free Faculty
for lecture in lectures:

    time_slot = lecture[0]
    subject_name = lecture[1]

    cur.execute("""
        SELECT name
        FROM faculty
        WHERE name NOT IN
        (
            SELECT faculty_name
            FROM timetable
            WHERE day=%s
            AND time_slot=%s
        )
        LIMIT 1
    """, (
        day_name,
        time_slot
    ))

    free_faculty = cur.fetchone()

    if free_faculty:

        suggestions.append({
            'time_slot': time_slot,
            'subject': subject_name,
            'available_faculty': free_faculty[0]
        })

cur.close()

return render_template(
    'adjustment_result.html',
    faculty_name=faculty_name,
    day_name=day_name,
    suggestions=suggestions
)
```

# MY TIMETABLE

@app.route('/my_timetable')
def my_timetable():

```
if 'loggedin' not in session:
    return redirect('/')

faculty_name = session['name']

cur = mysql.connection.cursor()

cur.execute("""
    SELECT
        day,
        time_slot,
        subject_name,
        class_name,
        lecture_type
    FROM timetable
    WHERE faculty_name=%s
""", (faculty_name,))

timetable = cur.fetchall()

cur.close()

return render_template(
    'my_timetable.html',
    timetable=timetable
)
```

# FREE FACULTY TEST

@app.route('/free_faculty')
def free_faculty():

```
if 'loggedin' not in session:
    return redirect('/')

day_name = 'Monday'
time_slot = '10:00-11:00'

cur = mysql.connection.cursor()

cur.execute("""
    SELECT name
    FROM faculty
    WHERE name NOT IN
    (
        SELECT faculty_name
        FROM timetable
        WHERE day=%s
        AND time_slot=%s
    )
""", (
    day_name,
    time_slot
))

faculties = cur.fetchall()

cur.close()

return render_template(
    'free_faculty.html',
    faculties=faculties
)
```

# LOGOUT

@app.route('/logout')
def logout():

```
session.clear()

return redirect('/')
```

# RUN APP

if **name** == '**main**':
app.run(debug=True)
