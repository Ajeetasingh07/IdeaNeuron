from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from reportlab.pdfgen import canvas

import os

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)

app.secret_key = 'Ajeeta_AI_Project_2026'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# LOGIN MANAGER
# =========================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

login_manager.session_protection = "strong"

# =========================
# DATABASE MODELS
# =========================

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


class Project(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200)
    )

    description = db.Column(
        db.Text
    )

    category = db.Column(
        db.String(100)
    )

    similarity = db.Column(
        db.Integer
    )

    originality = db.Column(
        db.Integer
    )

# =========================
# CREATE DATABASE
# =========================

with app.app_context():

    db.create_all()

# =========================
# USER LOADER
# =========================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():

    return render_template('index.html')

# =========================
# SIGNUP
# =========================

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            return "Username already exists"

        hashed_password = generate_password_hash(password)

        new_user = User(

            username=username,

            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

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

            login_user(user, remember=True)

            return redirect(url_for('projects'))

        return "Invalid Username or Password"

    return render_template('login.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('home'))

# =========================
# ANALYZE PROJECT
# =========================

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():

    title = request.form['title']

    description = request.form['description']

    text = description.lower()

    # =========================
    # SMART CATEGORY DETECTION
    # =========================

    # AI

    if (

        'ai' in text or
        'machine learning' in text or
        'deep learning' in text or
        'chatbot' in text or
        'neural network' in text

    ):

        category = 'Artificial Intelligence'

        similarity = 15

        originality = 85

    # BLOCKCHAIN

    elif (

        'blockchain' in text or
        'crypto' in text or
        'bitcoin' in text or
        'ethereum' in text

    ):

        category = 'Blockchain'

        similarity = 20

        originality = 80

    # IOT

    elif (

        'iot' in text or
        'sensor' in text or
        'automation' in text or
        'arduino' in text or
        'raspberry pi' in text or
        'smart irrigation' in text or
        'smart home' in text

    ):

        category = 'IoT'

        similarity = 25

        originality = 75

    # CYBER SECURITY

    elif (

        'cybersecurity' in text or
        'security' in text or
        'hacking' in text or
        'encryption' in text

    ):

        category = 'Cyber Security'

        similarity = 30

        originality = 70

    # WEB DEVELOPMENT

    else:

        category = 'Web Development'

        similarity = 35

        originality = 65

    # =========================
    # SAVE PROJECT
    # =========================

    new_project = Project(

        title=title,

        description=description,

        category=category,

        similarity=similarity,

        originality=originality
    )

    db.session.add(new_project)

    db.session.commit()

    # =========================
    # AI SUGGESTIONS
    # =========================

    suggestions = [

        "Add machine learning features",

        "Improve user experience",

        "Use cloud integration",

        "Add real-time analytics"

    ]

    return render_template(

        'result.html',

        title=title,

        category=category,

        similarity=similarity,

        originality=originality,

        suggestions=suggestions
    )

# =========================
# DASHBOARD
# =========================

@app.route('/projects')
@login_required
def projects():

    projects = Project.query.all()

    total_projects = len(projects)

    ai_count = Project.query.filter_by(
        category='Artificial Intelligence'
    ).count()

    blockchain_count = Project.query.filter_by(
        category='Blockchain'
    ).count()

    iot_count = Project.query.filter_by(
        category='IoT'
    ).count()

    cyber_count = Project.query.filter_by(
        category='Cyber Security'
    ).count()

    web_count = Project.query.filter_by(
        category='Web Development'
    ).count()

    if total_projects > 0:

        avg_originality = int(

            sum(
                p.originality for p in projects
            ) / total_projects
        )

    else:

        avg_originality = 0

    return render_template(

        'projects.html',

        projects=projects,

        total_projects=total_projects,

        ai_count=ai_count,

        blockchain_count=blockchain_count,

        iot_count=iot_count,

        cyber_count=cyber_count,

        web_count=web_count,

        avg_originality=avg_originality
    )

# =========================
# DELETE PROJECT
# =========================

@app.route('/delete/<int:id>')
@login_required
def delete_project(id):

    project = Project.query.get_or_404(id)

    db.session.delete(project)

    db.session.commit()

    return redirect(url_for('projects'))

# =========================
# DOWNLOAD PDF
# =========================

@app.route('/download_pdf')
@login_required
def download_pdf():

    file_name = 'AI_Project_Report.pdf'

    c = canvas.Canvas(file_name)

    c.setFont("Helvetica-Bold", 22)

    c.drawString(
        150,
        800,
        "IdeaNeuron AI Report"
    )

    c.setFont("Helvetica", 14)

    c.drawString(
        100,
        740,
        f"Generated by: {current_user.username}"
    )

    c.drawString(
        100,
        710,
        "AI Innovation Analytics Report"
    )

    c.drawString(
        100,
        680,
        "Project originality successfully analyzed."
    )

    c.drawString(
        100,
        650,
        "Future recommendation: Integrate AI + IoT."
    )

    c.save()

    return send_file(

        file_name,

        as_attachment=True
    )

# =========================
# RUN APP
# =========================

if __name__ == '__main__':

    app.run(

        host='0.0.0.0',

        port=5000

    )