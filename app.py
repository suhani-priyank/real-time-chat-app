from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_socketio import (
    SocketIO,
    emit,
    join_room
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import os

# ---------------- APP ----------------

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

socketio = SocketIO(
    app,
    async_mode='threading'
)

# ---------------- LOGIN ----------------

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

# ---------------- DATABASE ----------------

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    profile_pic = db.Column(
        db.String(200),
        default='default.png'
    )

# ---------------- USER LOADER ----------------

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )

# ---------------- HOME ----------------

@app.route('/')
@login_required
def home():

    return render_template(
        'index.html',
        username=current_user.username
    )

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    error = None

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        # CHECK EXISTING USER
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            error = "Username already exists"

            return render_template(
                'register.html',
                error=error
            )

        hashed_password = generate_password_hash(
            password
        )

        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)

        db.session.commit()

        return redirect('/login')

    return render_template(
        'register.html',
        error=error
    )

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect('/')

        else:

            error = "Invalid username or password"

    return render_template(
        'login.html',
        error=error
    )

# ---------------- LOGOUT ----------------

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')

# ---------------- PROFILE PIC UPLOAD ----------------

@app.route('/upload', methods=['POST'])
@login_required
def upload():

    file = request.files['profile_pic']

    if file:

        filename = secure_filename(
            file.filename
        )

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(filepath)

        current_user.profile_pic = filename

        db.session.commit()

    return redirect('/')

# ---------------- SOCKET EVENTS ----------------

# JOIN ROOM
@socketio.on('join_room')
def handle_join(data):

    room = data['room']

    join_room(room)

    emit(
        'notification',
        f"{data['username']} joined {room}",
        room=room
    )

@socketio.on('send_message')
def handle_message(data):

    # USER MESSAGE
    emit(
        'receive_message',
        {
            'username': data['username'],
            'message': data['message'],
            'time': data['time']
        },
        room=data['room']
    )

    user_msg = data['message'].lower()

    # AI BOT REPLIES
    if "hello" in user_msg or "hi" in user_msg:

        ai_reply = "Hello 👋 How are you?"

    elif "how are you" in user_msg:

        ai_reply = "I'm doing great 🚀"

    elif "python" in user_msg:

        ai_reply = "Python is amazing for backend development 🐍"

    elif "project" in user_msg:

        ai_reply = "Your chat application looks awesome 🔥"

    elif "college" in user_msg:

        ai_reply = "College projects help build strong skills 💡"

    elif "bye" in user_msg:

        ai_reply = "Goodbye 👋 Have a great day!"

    elif "react" in user_msg:

        ai_reply = "React creates beautiful modern UIs ⚛️"

    elif "internship" in user_msg:

        ai_reply = "This project is perfect for internship showcase 💼"

    else:

        ai_reply = "That's interesting 😄 Tell me more."

    # SEND AI MESSAGE
    emit(
        'receive_message',
        {
            'username': 'AI Bot',
            'message': ai_reply,
            'time': data['time']
        },
        room=data['room']
    )

# TYPING
@socketio.on('typing')
def typing(data):

    emit(
        'show_typing',
        f"{data['username']} is typing...",
        room=data['room'],
        include_self=False
    )

# ---------------- RUN ----------------


if __name__ == "__main__":
    app.run()