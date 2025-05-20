from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from win32ctypes.pywin32.pywintypes import datetime

from llm.LLM import LLMClient
from src.files import FileHandler
from src.login_manager import LoginManager
from src.shopping_list import ShoppingDateBase
from src.task_process import TaskProcess
from src.schedule_event_manager import ScheduleEventDB
from config.db import SessionLocal

app = Flask(__name__)
app.secret_key = "my-secret=key"

protect_pages = ["main_dashboard","shopping_list"]

@app.before_request
def check_login():
    if request.endpoint in protect_pages and "user_id" not in session:
        return redirect(url_for("home"))

@app.route('/')
def home():
    """
    כאן יהיה מי שינסה להיכנס לאתר
    צריך לממש בדיקה האם הוא כבר משתמש קיים או לא
    אם קיים שייכנס מיד לעמוד הראשי
    אם לא שייכנס לעמוד התחברות
    לבינתיים נכנס מיד לעמוד התחברות
    :return:
    """
    return redirect(url_for('login'))

@app.route('/main_dashboard',methods=["GET","POST"])
def main_dashboard():
    if request.method == 'POST':
        task_text = request.form['task']
        user_id = session["user_id"] if session["user_id"] else 0
        response = task.get_task_response(task_text,user_id)
        # בהמשך ננתח את הטקסט ונשמור אותו
        return render_template("main_dashboard.html",message={"task" : response})

    return render_template('main_dashboard.html')

@app.route("/shopping_list",methods=["GET","POST"])
def shopping_list():
    items = shopping_manager.get_shopping_tasks(session["user_id"])
    return render_template("shopping_list.html",items=items)

@app.route("/events")
def events():
    events = event_manager.get_events(session["user_id"])
    return render_template("calender_event.html",events=events)

@app.route("/note")
def note():
    pass

@app.route("/plans")
def plans():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        is_success,response = login_manager.login_check(email,password)
        if is_success:
            session["user_id"] = response
            # כאן תכניס לוגיקה של אימות בהמשך
            return redirect(url_for("main_dashboard"))
        else:
           return render_template('login.html',error=response)
    return render_template('login.html')


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # ווידוא שהשדות לא ריקים
        if not username or not email or not password:
            return render_template('new_user.html', error="כל השדות הם חובה")

        (success,user_id) = login_manager.new_user(email,password,username)
        if success:
            session["user_id"] = user_id
            return redirect(url_for("main_dashboard"))
        else:
            return render_template("new_user.html",error=user_id)

    return render_template("new_user.html")

@app.route("/shopping_list/complete_task",methods=["POST"])
def complete_shopping_list_task():
    time = datetime.strftime(datetime.now(),"%d-%m-%Y %H:%M")
    content = request.get_json()
    is_active = content.get("completed",False)
    shopping_manager.complete_task({"is_active" : not is_active,"completed_at" : time,"content" : content, "user_id" : session["user_id"]})

    return jsonify({"success": True})

@app.route("/shopping_list/remove_task",methods=["POST"])
def remove_shopping_list_task():
    content = request.get_json()
    time = datetime.now()
    shopping_manager.remove_task({"removed_at": time,"content":content,"user_id" : session["user_id"]})

    return jsonify({"success": True})


if __name__ == '__main__':
    client = LLMClient()
    file_handler = FileHandler()
    db_session = SessionLocal()
    login_manager = LoginManager(db_session)
    shopping_manager = ShoppingDateBase(db_session)
    event_manager = ScheduleEventDB(db_session)
    task = TaskProcess(client,file_handler,
                       login_manager=login_manager,
                       shopping_manager=shopping_manager,
                       event_manager=event_manager)

    app.run(debug=True)
