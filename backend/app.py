# backend/app.py
# ProTodo v2.0 - Auto-Complete with Recurrence Support

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from dateutil.tz import gettz as ZoneInfo

from config import Config
from models import db, User, Todo
from auth import auth_bp
from todos import todos_bp 
from mailer import send_reminder_email

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["*"], supports_credentials=True)
    db.init_app(app)
    jwt = JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(todos_bp, url_prefix='/api')

    # === STATIC FILES ===
    FRONTEND_FOLDER = os.path.join(os.getcwd(), '..', 'frontend')
    FRONTEND_FOLDER = os.path.abspath(FRONTEND_FOLDER)

    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_FOLDER, 'app.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory(FRONTEND_FOLDER, filename)

    # === SCHEDULER ===
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task('interval', id='check_reminders', minutes=1)
    def check_due_reminders():
        with app.app_context():
            now_utc = datetime.now(timezone.utc)
            
            # Fetch active tasks
            active_todos = Todo.query.filter(Todo.completed == False).all()

            if not active_todos: return

            for todo in active_todos:
                user = db.session.get(User, todo.user_id)
                if not user or not todo.due_date: continue

                # Handle Timezones
                user_tz_str = user.timezone if user.timezone else 'UTC'
                try: user_tz = ZoneInfo(user_tz_str)
                except: user_tz = timezone.utc

                # Normalize Dates
                db_date = todo.due_date
                if db_date.tzinfo is None:
                    task_time_local = db_date.replace(tzinfo=user_tz)
                else:
                    task_time_local = db_date.astimezone(user_tz)

                task_time_utc = task_time_local.astimezone(timezone.utc)
                time_remaining = task_time_utc - now_utc
                minutes_remaining = time_remaining.total_seconds() / 60

                # === 1. AUTO-COMPLETE LOGIC ===
                if minutes_remaining < 0:
                    print(f"   ✅ Auto-Completing: {todo.title}")
                    todo.completed = True
                    
                    # Mark subtasks as done
                    if todo.subtasks:
                        new_subtasks = []
                        for sub in todo.subtasks:
                            sub_copy = sub.copy()
                            sub_copy['completed'] = True
                            new_subtasks.append(sub_copy)
                        todo.subtasks = new_subtasks

                    # === RECURRENCE GENERATION (FIX) ===
                    if todo.recurrence != 'never':
                        next_date = None
                        if todo.recurrence == 'daily':
                            next_date = todo.due_date + timedelta(days=1)
                        elif todo.recurrence == 'weekly':
                            next_date = todo.due_date + timedelta(weeks=1)
                        elif todo.recurrence == 'monthly':
                            next_date = todo.due_date + timedelta(days=30)
                        
                        if next_date:
                            next_task = Todo(
                                user_id=todo.user_id,
                                title=todo.title,
                                notes=todo.notes,
                                priority=todo.priority,
                                category=todo.category,
                                tags=todo.tags,
                                recurrence=todo.recurrence,
                                reminder_minutes=todo.reminder_minutes,
                                due_date=next_date,
                                completed=False,
                                reminder_sent=False,
                                subtasks=todo.subtasks # Clone the (now completed) list structure? 
                                # Better: Clone structure but mark false. 
                                # For simplicity, we clone as is, user can uncheck.
                            )
                            # Reset subtasks to incomplete for new task
                            if next_task.subtasks:
                                reset_subs = []
                                for s in next_task.subtasks:
                                    s_reset = s.copy()
                                    s_reset['completed'] = False
                                    reset_subs.append(s_reset)
                                next_task.subtasks = reset_subs

                            db.session.add(next_task)
                            print(f"   🔄 Recurring Task Created: {todo.title}")

                    db.session.commit()
                    continue 

                # === 2. REMINDER LOGIC ===
                if not todo.reminder_sent and minutes_remaining <= (todo.reminder_minutes + 1) and minutes_remaining > 0:
                    formatted_time = task_time_local.strftime('%Y-%m-%d %I:%M %p')
                    if user.email:
                        print(f"   🔔 Sending email to {user.email}")
                        send_reminder_email(user.email, todo.title, formatted_time)
                    todo.reminder_sent = True
                    db.session.commit()

    try: scheduler.start()
    except Exception: pass

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)