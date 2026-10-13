from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename

from app.database import (
    initialize_database,
    create_user,
    get_user,
    verify_password,
    save_timetable,
    get_timetable
)

from app.pdf_reader import extract_text_from_pdf

from app.study_ai import (
    generate_summary,
    extract_key_topics,
    generate_questions
)


# =========================================================
# FLASK APPLICATION
# =========================================================


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
    static_url_path="/static"
)

app.secret_key = "AIStudyPlanner-Secret-Key-2026"


# =========================================================
# PROJECT DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_FOLDER = BASE_DIR / "uploads"

SCOPE_FOLDER = UPLOAD_FOLDER / "scope"
NOTES_FOLDER = UPLOAD_FOLDER / "notes"
PAST_PAPERS_FOLDER = UPLOAD_FOLDER / "past_papers"


# Create upload folders if they do not exist

SCOPE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

NOTES_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

PAST_PAPERS_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# DATABASE
# =========================================================

initialize_database()


# =========================================================
# LOGIN CHECK
# =========================================================

def login_required():

    return "user_id" in session


# =========================================================
# HOME / START PAGE
# =========================================================

@app.route("/")
def index():

    if "user_id" in session:

        return redirect(
            url_for("home")
        )

    return redirect(
        url_for("login")
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # CHECK REQUIRED FIELDS
        # -------------------------------------------------

        if not full_name:

            return render_template(
                "register.html",
                error="Please enter your full name."
            )

        if not email:

            return render_template(
                "register.html",
                error="Please enter your email."
            )

        if not password:

            return render_template(
                "register.html",
                error="Please enter a password."
            )

        # -------------------------------------------------
        # CHECK PASSWORD MATCH
        # -------------------------------------------------

        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user_created = create_user(
            full_name,
            email,
            password
        )

        if not user_created:

            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        # -------------------------------------------------
        # LOGIN USER AUTOMATICALLY
        # -------------------------------------------------

        user = get_user(email)

        if user:

            session["user_id"] = user["id"]

            session["full_name"] = (
                user["full_name"]
            )

            session["email"] = (
                user["email"]
            )

            return redirect(
                url_for("home")
            )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = get_user(email)

        # -------------------------------------------------
        # VERIFY PASSWORD
        # -------------------------------------------------

        # IMPORTANT:
        #
        # database.py expects:
        #
        # verify_password(
        #     stored_password,
        #     entered_password
        # )
        #
        # Therefore the database password MUST come first.

        if (
            user
            and verify_password(
                user["password"],
                password
            )
        ):

            session["user_id"] = user["id"]

            session["full_name"] = (
                user["full_name"]
            )

            session["email"] = (
                user["email"]
            )

            return redirect(
                url_for("home")
            )

        # -------------------------------------------------
        # LOGIN FAILED
        # -------------------------------------------------

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# UPCOMING ACTIVITIES (built from the saved timetable)
# =========================================================

DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]


def format_minutes(total_minutes):

    total_minutes = total_minutes % 1440

    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def get_upcoming_activities(user_id, limit=6):

    rows = get_timetable(user_id)

    now = datetime.now()
    today = now.weekday()
    now_minutes = now.hour * 60 + now.minute

    ordered = []

    for row in rows:

        days_ahead = (row["day_index"] - today) % 7

        # A session earlier today is shown again next week
        if days_ahead == 0 and row["start_minutes"] < now_minutes:
            days_ahead = 7

        ordered.append(
            (days_ahead, row["start_minutes"], row)
        )

    ordered.sort(key=lambda item: (item[0], item[1]))

    activities = []

    for days_ahead, _, row in ordered[:limit]:

        if days_ahead == 0:
            day_label = "Today"
        elif days_ahead == 1:
            day_label = "Tomorrow"
        else:
            day_label = row["day_name"]

        activities.append({
            "module": row["module"],
            "day": day_label,
            "time": (
                format_minutes(row["start_minutes"])
                + " - "
                + format_minutes(row["end_minutes"])
            ),
            "type": row["assessment"] or "Study session"
        })

    return activities


# =========================================================
# HOME DASHBOARD
# =========================================================

@app.route("/home")
def home():

    if not login_required():

        return redirect(
            url_for("login")
        )

    # -------------------------------------------------
    # UPCOMING ACTIVITIES FROM THE SAVED TIMETABLE
    # -------------------------------------------------

    upcoming_activities = get_upcoming_activities(
        session["user_id"]
    )

    return render_template(
        "home.html",
        full_name=session.get(
            "full_name",
            "Student"
        ),
        upcoming_activities=upcoming_activities
    )


# =========================================================
# STUDY MATERIALS PAGE
# =========================================================

@app.route("/materials")
def materials():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "materials.html"
    )


# =========================================================
# UPLOAD STUDY MATERIAL
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    if not login_required():

        return redirect(
            url_for("login")
        )

    # -------------------------------------------------
    # GET FORM INFORMATION
    # -------------------------------------------------
    #
    # The materials form has three file inputs:
    #   scope_file, notes_file and past_paper_file.

    module_name = request.form.get(
        "module_name",
        ""
    ).strip()

    upload_fields = [
        ("scope_file", SCOPE_FOLDER),
        ("notes_file", NOTES_FOLDER),
        ("past_paper_file", PAST_PAPERS_FOLDER)
    ]

    uploaded_files = []
    extracted_texts = {}
    analysis = []

    for field_name, save_folder in upload_fields:

        uploaded_file = request.files.get(field_name)

        # Skip inputs the student left empty

        if not uploaded_file or uploaded_file.filename == "":
            continue

        # Only PDF files are accepted

        if not uploaded_file.filename.lower().endswith(".pdf"):

            return render_template(
                "materials.html",
                error="Only PDF files are currently supported."
            )

        # Create a safe file name

        filename = secure_filename(
            uploaded_file.filename
        )

        if module_name:

            filename = (
                secure_filename(module_name)
                + "_"
                + filename
            )

        file_path = save_folder / filename

        uploaded_file.save(file_path)

        # Extract the text and run the local study analysis

        extracted_text = extract_text_from_pdf(
            file_path
        )

        uploaded_files.append(filename)

        extracted_texts[filename] = extracted_text[:3000]

        analysis.append({
            "name": filename,
            "summary": generate_summary(extracted_text),
            "key_topics": extract_key_topics(extracted_text),
            "questions": generate_questions(extracted_text)
        })

    if not uploaded_files:

        return render_template(
            "materials.html",
            error="Please select at least one PDF file."
        )

    return render_template(
        "materials.html",
        module_name=module_name,
        uploaded_files=uploaded_files,
        extracted_texts=extracted_texts,
        analysis=analysis
    )


# =========================================================
# TIMETABLE PAGE
# =========================================================

@app.route("/timetable")
def timetable():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "timetable.html"
    )


# =========================================================
# GENERATE TIMETABLE
# =========================================================
#
# NOTE:
# The current timetable interface uses JavaScript to
# generate the timetable.
#
# We will later move the scheduling algorithm into Python
# and connect it to the database so that each student's
# timetable is saved permanently.
#
# This route is kept temporarily so the application
# structure remains stable.
# =========================================================

@app.route(
    "/generate-timetable",
    methods=["POST"]
)
def generate_timetable():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("timetable")
    )


# =========================================================
# SAVE GENERATED TIMETABLE
# =========================================================
#
# The timetable is generated in the browser (timetable.html).
# The page then sends the result here, so it is stored in the
# database and can be shown on the dashboard.
# =========================================================

@app.route(
    "/save-timetable",
    methods=["POST"]
)
def save_generated_timetable():

    if not login_required():

        return jsonify(error="Not logged in."), 401

    data = request.get_json(silent=True) or {}

    schedule = data.get("schedule", [])

    if not isinstance(schedule, list):

        return jsonify(error="Invalid timetable."), 400

    sessions = []

    for day_index, day in enumerate(schedule[:7]):

        if not isinstance(day, dict):
            continue

        for item in day.get("sessions", []):

            if not isinstance(item, dict) or item.get("break"):
                continue

            try:
                start = int(item["start"])
                end = int(item["end"])
            except (KeyError, TypeError, ValueError):
                continue

            module = str(item.get("module", "")).strip()[:100]

            if not module or not 0 <= start < end <= 2880:
                continue

            sessions.append({
                "day_index": day_index,
                "day_name": DAY_NAMES[day_index],
                "module": module,
                "assessment": str(item.get("assessment", ""))[:50],
                "start": start,
                "end": end
            })

    save_timetable(session["user_id"], sessions)

    return jsonify(saved=len(sessions))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("       AI STUDY PLANNER")
    print("==========================================")
    print()
    print("Website running at:")
    print("http://127.0.0.1:5000")
    print()
    print("Press CTRL+C to stop the server.")
    print()

    app.run(
        debug=True
    )