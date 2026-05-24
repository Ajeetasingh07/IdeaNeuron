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

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

import random

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ideaneuronsecret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

# STORE LATEST REPORT

latest_report = {}

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
        unique=True
    )

    password = db.Column(
        db.String(200)
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
        db.Float
    )

    originality = db.Column(
        db.Float
    )

# =========================
# LOGIN MANAGER
# =========================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))

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

        hashed_password = generate_password_hash(password)

        new_user = User(

            username=username,

            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect('/login')

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

            login_user(user)

            return redirect('/projects')

    return render_template('login.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')

@login_required
def logout():

    logout_user()

    return redirect('/')

# =========================
# ANALYZE PROJECT
# =========================

@app.route('/analyze', methods=['POST'])

@login_required
def analyze():

    global latest_report

    title = request.form['title']

    description = request.form['description']

    desc = description.lower()

    # CATEGORY DETECTION

    if 'ai' in desc or 'machine learning' in desc:

        category = 'Artificial Intelligence'

    elif 'blockchain' in desc:

        category = 'Blockchain'

    elif 'iot' in desc:

        category = 'IoT'

    elif 'web' in desc:

        category = 'Web Development'

    else:

        category = 'Software Project'

    # SIMILARITY ANALYSIS

    common_projects = [

        'AI Chatbot for students',

        'Weather App',

        'Blockchain Voting System',

        'IoT Smart Home',

        'Student Management System'
    ]

    most_similar = random.choice(common_projects)

    similarity_score = round(
        random.uniform(10, 80),
        2
    )

    originality_score = round(
        100 - similarity_score,
        2
    )

    # AI SUGGESTIONS

    suggestions = []

    if "chatbot" in desc:

        suggestions.append(
            "Add voice assistant integration"
        )

        suggestions.append(
            "Use NLP for smarter conversations"
        )

    if "ai" in desc:

        suggestions.append(
            "Add Machine Learning prediction system"
        )

    if "blockchain" in desc:

        suggestions.append(
            "Integrate smart contracts"
        )

    if "iot" in desc:

        suggestions.append(
            "Add real-time sensor analytics"
        )

    if "health" in desc:

        suggestions.append(
            "Add disease prediction AI"
        )

    if "student" in desc:

        suggestions.append(
            "Add personalized recommendation engine"
        )

    # DEFAULT SUGGESTIONS

    if len(suggestions) == 0:

        suggestions = [

            "Add AI-powered analytics",

            "Improve UI/UX experience",

            "Add real-time dashboard",

            "Use cloud deployment"
        ]

    # SAVE PROJECT

    new_project = Project(

        title=title,

        description=description,

        category=category,

        similarity=similarity_score,

        originality=originality_score
    )

    db.session.add(new_project)

    db.session.commit()

    # SAVE REPORT DATA

    latest_report = {

        "category": category,

        "similarity_score": similarity_score,

        "originality_score": originality_score,

        "most_similar": most_similar,

        "suggestions": suggestions
    }

    # RESULT PAGE

    return render_template(

        'result.html',

        category=category,

        similarity_score=similarity_score,

        originality_score=originality_score,

        most_similar=most_similar,

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

    web_count = Project.query.filter_by(
        category='Web Development'
    ).count()

    if total_projects > 0:

        avg_originality = round(

            sum(
                p.originality for p in projects
            ) / total_projects,

            2
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

        web_count=web_count,

        avg_originality=avg_originality
    )

# =========================
# DOWNLOAD REPORT
# =========================

@app.route('/download-report')

@login_required
def download_report():

    global latest_report

    doc = SimpleDocTemplate(
        "AI_Project_Report.pdf"
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(

        "<b>IdeaNeuron AI Analysis Report</b>",

        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1,20))

    # CATEGORY

    elements.append(

        Paragraph(

            f"<b>Project Category:</b> {latest_report['category']}",

            styles['BodyText']
        )
    )

    elements.append(Spacer(1,12))

    # SIMILARITY

    elements.append(

        Paragraph(

            f"<b>Similarity Score:</b> {latest_report['similarity_score']}%",

            styles['BodyText']
        )
    )

    elements.append(Spacer(1,12))

    # ORIGINALITY

    elements.append(

        Paragraph(

            f"<b>Originality Score:</b> {latest_report['originality_score']}%",

            styles['BodyText']
        )
    )

    elements.append(Spacer(1,12))

    # MOST SIMILAR

    elements.append(

        Paragraph(

            f"<b>Most Similar Project:</b> {latest_report['most_similar']}",

            styles['BodyText']
        )
    )

    elements.append(Spacer(1,20))

    # AI SUGGESTIONS

    elements.append(

        Paragraph(

            "<b>AI Suggestions:</b>",

            styles['Heading2']
        )
    )

    elements.append(Spacer(1,10))

    for suggestion in latest_report['suggestions']:

        elements.append(

            Paragraph(

                f"• {suggestion}",

                styles['BodyText']
            )
        )

        elements.append(Spacer(1,8))

    doc.build(elements)

    return send_file(

        "AI_Project_Report.pdf",

        as_attachment=True
    )

# =========================
# RUN APP
# =========================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)