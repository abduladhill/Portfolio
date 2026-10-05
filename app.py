from flask import Flask, render_template, request, redirect, url_for
import os
import uuid
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection, init_db

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    raise RuntimeError("SECRET_KEY is not configured.")

app.config["SECRET_KEY"] = secret_key

csrf = CSRFProtect(app)

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "resume"
)

# Project image uploads
PROJECT_IMAGE_FOLDER = os.path.join(
    app.root_path,
    "static",
    "images",
    "projects"
)

os.makedirs(PROJECT_IMAGE_FOLDER, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

# Make sure the resume folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(file):
    if not file or not file.filename:
        return False

    if (
        "."
        not in file.filename
        or file.filename.rsplit(".", 1)[1].lower() != "pdf"
    ):
        return False

    header = file.stream.read(5)
    file.stream.seek(0)

    return header == b"%PDF-"

def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )

# Secret key used by Flask sessions
# Session security
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Initialize database
init_db()


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"


class Admin(UserMixin):

    def __init__(self, admin_id, username):
        self.id = admin_id
        self.username = username


@login_manager.user_loader
def load_user(admin_id):

    connection = get_db_connection()

    admin = connection.execute(
        "SELECT * FROM admin WHERE id = ?",
        (admin_id,)
    ).fetchone()

    connection.close()

    if admin:
        return Admin(admin["id"], admin["username"])

    return None


# -------------------------
# PUBLIC PORTFOLIO
# -------------------------

# PUBLIC PORTFOLIO


@app.route("/")
def home():
    connection = get_db_connection()

    projects = connection.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    settings = connection.execute(
        "SELECT * FROM site_settings WHERE id = 1"
    ).fetchone()

    skills = connection.execute(
        "SELECT * FROM skills ORDER BY id DESC"
    ).fetchall()

    # Group skills by category
    skill_groups = {}

    for skill in skills:
        category = skill["category"] or "Other"
        skill_groups.setdefault(category, []).append(skill)

    experiences = connection.execute(
        "SELECT * FROM experience ORDER BY id DESC"
    ).fetchall()

    education = connection.execute(
        "SELECT * FROM education ORDER BY id DESC"
    ).fetchall()

    certifications = connection.execute(
        "SELECT * FROM certifications ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return render_template(
    "index.html",
    projects=projects,
    settings=settings,
    skills=skills,
    skill_groups=skill_groups,
    experiences=experiences,
    education=education,
    certifications=certifications
    )
    # -------------------------
# ADMIN LOGIN
# -------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()

        admin = connection.execute(
            "SELECT * FROM admin WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if admin and check_password_hash(
            admin["password"],
            password
        ):

            user = Admin(
                admin["id"],
                admin["username"]
            )

            login_user(user)

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin/login.html",
            error="Invalid username or password."
        )

    return render_template("admin/login.html")

@app.route("/admin/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    connection = get_db_connection()

    admin = connection.execute(
        "SELECT * FROM admin WHERE id = ?",
        (current_user.id,)
    ).fetchone()

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Verify current password
        if not check_password_hash(
            admin["password"],
            current_password
        ):
            connection.close()

            return render_template(
                "admin/change_password.html",
                error="Current password is incorrect."
            )

        # Check password confirmation
        if new_password != confirm_password:
            connection.close()

            return render_template(
                "admin/change_password.html",
                error="New passwords do not match."
            )

        # Minimum password length
        if len(new_password) < 8:
            connection.close()

            return render_template(
                "admin/change_password.html",
                error="New password must be at least 8 characters long."
            )

        # Generate secure password hash
        hashed_password = generate_password_hash(
            new_password
        )

        connection.execute(
            """
            UPDATE admin
            SET password = ?
            WHERE id = ?
            """,
            (hashed_password, current_user.id)
        )

        connection.commit()
        connection.close()

        return render_template(
            "admin/change_password.html",
            success="Password changed successfully."
        )

    connection.close()

    return render_template(
        "admin/change_password.html"
    )
# -------------------------
# ADMIN DASHBOARD
# -------------------------

@app.route("/admin")
@login_required
def admin_dashboard():

    connection = get_db_connection()

    projects = connection.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    skills = connection.execute(
        "SELECT * FROM skills ORDER BY id DESC"
    ).fetchall()

    experiences = connection.execute(
        "SELECT * FROM experience ORDER BY id DESC"
    ).fetchall()

    education = connection.execute(
        "SELECT * FROM education ORDER BY id DESC"
    ).fetchall()

    certifications = connection.execute(
        "SELECT * FROM certifications ORDER BY id DESC"
    ).fetchall()

    messages = connection.execute(
        "SELECT * FROM messages ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/dashboard.html",
        projects=projects,
        skills=skills,
        experiences=experiences,
        education=education,
        certifications=certifications,
        messages=messages
    )

@app.route("/admin/projects/add", methods=["GET", "POST"])
@login_required
def add_project():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        technologies = request.form.get("technologies", "").strip()
        features = request.form.get("features", "").strip()
        github_url = request.form.get("github_url", "").strip()
        demo_url = request.form.get("demo_url", "").strip()
        status = request.form.get("status", "Completed").strip()
        category = request.form.get("category", "Other").strip()

        # Get uploaded project image
        image = request.files.get("image")

        # Validate required fields
        if not title or not description:
            return render_template(
                "admin/add_project.html",
                error="Title and description are required."
            )

        # Default: no image
        image_url = None

        # Handle image upload
        if image and image.filename:

            if not allowed_image(image.filename):
                return render_template(
                    "admin/add_project.html",
                    error="Invalid image format. Use PNG, JPG, JPEG, or WebP."
                )

            original_filename = secure_filename(image.filename)

            filename = (
                f"{uuid.uuid4().hex}_"
                f"{original_filename}"
            )

            image_path = os.path.join(
                PROJECT_IMAGE_FOLDER,
                filename
            )

            image.save(image_path)

            image_url = f"/images/projects/{filename}"

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO projects
            (
                title,
                description,
                features,
                technologies,
                github_url,
                demo_url,
                status,
                category,
                image_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                features,
                technologies,
                github_url,
                demo_url,
                status,
                category,
                image_url
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template("admin/add_project.html")
# =========================
# PROJECT MANAGEMENT
# =========================

@app.route("/admin/projects")
@login_required
def manage_projects():

    connection = get_db_connection()

    projects = connection.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/projects.html",
        projects=projects
    )
# -------------------------
# EDIT PROJECT
# -------------------------

@app.route("/project/<int:project_id>")
def project_detail(project_id):

    connection = get_db_connection()

    project = connection.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()

    settings = connection.execute(
        "SELECT * FROM site_settings LIMIT 1"
    ).fetchone()

    previous_project = connection.execute(
        """
        SELECT id, title
        FROM projects
        WHERE id < ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (project_id,)
    ).fetchone()

    next_project = connection.execute(
        """
        SELECT id, title
        FROM projects
        WHERE id > ?
        ORDER BY id ASC
        LIMIT 1
        """,
        (project_id,)
    ).fetchone()

    connection.close()

    if project is None:
        return "Project not found", 404

    return render_template(
        "project_detail.html",
        project=project,
        settings=settings,
        previous_project=previous_project,
        next_project=next_project
    )

@app.route("/admin/projects/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):

    connection = get_db_connection()

    # Get the project we want to edit
    project = connection.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()

    # If project doesn't exist
    if project is None:
        connection.close()
        return "Project not found", 404

    # When the form is submitted
    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        technologies = request.form.get("technologies", "").strip()
        features = request.form.get("features", "").strip()
        github_url = request.form.get("github_url", "").strip()
        demo_url = request.form.get("demo_url", "").strip()
        status = request.form.get("status", "Completed").strip()
        category = request.form.get("category", "Other").strip()

        # Get uploaded image
        image = request.files.get("image")

        # Validate required fields
        if not title or not description:

            connection.close()

            return render_template(
                "admin/edit_project.html",
                project=project,
                error="Title and description are required."
            )

        # Keep the existing image by default
        image_url = project["image_url"]

        # Handle new image upload
        if image and image.filename:

            if not allowed_image(image.filename):

                connection.close()

                return render_template(
                    "admin/edit_project.html",
                    project=project,
                    error="Invalid image format. Use PNG, JPG, JPEG, or WebP."
                )

            # Delete the old image if one exists
            if project["image_url"]:

                old_image_path = os.path.join(
                    app.root_path,
                    "static",
                    project["image_url"].lstrip("/")
                )

                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Generate a unique filename
            original_filename = secure_filename(image.filename)

            filename = (
                f"{uuid.uuid4().hex}_"
                f"{original_filename}"
            )

            image_path = os.path.join(
                PROJECT_IMAGE_FOLDER,
                filename
            )

            image.save(image_path)

            image_url = f"/images/projects/{filename}"

        # Update the project
        connection.execute(
            """
            UPDATE projects
            SET title = ?,
                description = ?,
                features = ?,
                technologies = ?,
                github_url = ?,
                demo_url = ?,
                status = ?,
                category = ?,
                image_url = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                features,
                technologies,
                github_url,
                demo_url,
                status,
                category,
                image_url,
                project_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin_dashboard"))

    connection.close()

    return render_template(
        "admin/edit_project.html",
        project=project
    )

# -------------------------
# DELETE PROJECT
# -------------------------

@app.route("/admin/projects/delete/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):

    connection = get_db_connection()

    # Check if the project exists
    project = connection.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()

    if project is None:
        connection.close()
        return "Project not found", 404

    # Delete the project
    connection.execute(
        "DELETE FROM projects WHERE id = ?",
        (project_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin_dashboard"))

# SITE SETTINGS
@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def site_settings():
    connection = get_db_connection()

    settings = connection.execute(
        "SELECT * FROM site_settings WHERE id = 1"
    ).fetchone()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        headline = request.form.get("headline", "").strip()
        hero_description = request.form.get("hero_description", "").strip()
        about = request.form.get("about", "").strip()
        email = request.form.get("email", "").strip()
        linkedin_url = request.form.get("linkedin_url", "").strip()
        github_url = request.form.get("github_url", "").strip()
        resume_url = request.form.get("resume_url", "").strip()

        if settings:
            connection.execute(
                """
                UPDATE site_settings
                SET name = ?,
                    headline = ?,
                    hero_description = ?,
                    about = ?,
                    email = ?,
                    linkedin_url = ?,
                    github_url = ?,
                    resume_url = ?
                WHERE id = 1
                """,
                (
                    name,
                    headline,
                    hero_description,
                    about,
                    email,
                    linkedin_url,
                    github_url,
                    resume_url
                )
            )

        else:
            connection.execute(
                """
                INSERT INTO site_settings
                (
                    id,
                    name,
                    headline,
                    hero_description,
                    about,
                    email,
                    linkedin_url,
                    github_url,
                    resume_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    1,
                    name,
                    headline,
                    hero_description,
                    about,
                    email,
                    linkedin_url,
                    github_url,
                    resume_url
                )
            )

        connection.commit()

        settings = connection.execute(
            "SELECT * FROM site_settings WHERE id = 1"
        ).fetchone()

        connection.close()

        return render_template(
            "admin/settings.html",
            settings=settings,
            success="Settings saved successfully!"
        )

    connection.close()

    return render_template(
        "admin/settings.html",
        settings=settings
    )

# SKILLS
@app.route("/admin/skills", methods=["GET", "POST"])
@login_required
def manage_skills():

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()

        if not name:
            skills = connection.execute(
                "SELECT * FROM skills ORDER BY id DESC"
            ).fetchall()

            connection.close()

            return render_template(
                "admin/skills.html",
                skills=skills,
                error="Skill name is required."
            )

        connection.execute(
            """
            INSERT INTO skills (name, category)
            VALUES (?, ?)
            """,
            (name, category)
        )

        connection.commit()

        skills = connection.execute(
            "SELECT * FROM skills ORDER BY id DESC"
        ).fetchall()

        connection.close()

        return render_template(
            "admin/skills.html",
            skills=skills,
            success="Skill added successfully!"
        )

    skills = connection.execute(
        "SELECT * FROM skills ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/skills.html",
        skills=skills
    )

# EDIT SKILL
@app.route("/admin/skills/edit/<int:skill_id>", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):

    connection = get_db_connection()

    skill = connection.execute(
        "SELECT * FROM skills WHERE id = ?",
        (skill_id,)
    ).fetchone()

    if skill is None:
        connection.close()
        return "Skill not found", 404

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()

        if not name:
            connection.close()

            return render_template(
                "admin/edit_skill.html",
                skill=skill,
                error="Skill name is required."
            )

        connection.execute(
            """
            UPDATE skills
            SET name = ?,
                category = ?
            WHERE id = ?
            """,
            (
                name,
                category,
                skill_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("manage_skills"))

    connection.close()

    return render_template(
        "admin/edit_skill.html",
        skill=skill
    )

# DELETE SKILL
@app.route("/admin/skills/delete/<int:skill_id>", methods=["POST"])
@login_required
def delete_skill(skill_id):

    connection = get_db_connection()

    skill = connection.execute(
        "SELECT * FROM skills WHERE id = ?",
        (skill_id,)
    ).fetchone()

    if skill is None:
        connection.close()
        return "Skill not found", 404

    connection.execute(
        "DELETE FROM skills WHERE id = ?",
        (skill_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_skills"))

# EXPERIENCE
@app.route("/admin/experience", methods=["GET", "POST"])
@login_required
def manage_experience():

    connection = get_db_connection()

    if request.method == "POST":

        role = request.form.get("role", "").strip()
        company = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        description = request.form.get("description", "").strip()

        if not role or not company:
            experiences = connection.execute(
                "SELECT * FROM experience ORDER BY id DESC"
            ).fetchall()

            connection.close()

            return render_template(
                "admin/experience.html",
                experiences=experiences,
                error="Role and company are required."
            )

        connection.execute(
            """
            INSERT INTO experience
            (role, company, location, start_date, end_date, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                role,
                company,
                location,
                start_date,
                end_date,
                description
            )
        )

        connection.commit()

        experiences = connection.execute(
            "SELECT * FROM experience ORDER BY id DESC"
        ).fetchall()

        connection.close()

        return render_template(
            "admin/experience.html",
            experiences=experiences,
            success="Experience added successfully!"
        )

    experiences = connection.execute(
        "SELECT * FROM experience ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/experience.html",
        experiences=experiences
    )

# EDIT EXPERIENCE
@app.route("/admin/experience/edit/<int:experience_id>", methods=["GET", "POST"])
@login_required
def edit_experience(experience_id):

    connection = get_db_connection()

    experience = connection.execute(
        "SELECT * FROM experience WHERE id = ?",
        (experience_id,)
    ).fetchone()

    if experience is None:
        connection.close()
        return "Experience not found", 404

    if request.method == "POST":

        role = request.form.get("role", "").strip()
        company = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        description = request.form.get("description", "").strip()

        if not role or not company:
            connection.close()

            return render_template(
                "admin/edit_experience.html",
                experience=experience,
                error="Role and company are required."
            )

        connection.execute(
            """
            UPDATE experience
            SET role = ?,
                company = ?,
                location = ?,
                start_date = ?,
                end_date = ?,
                description = ?
            WHERE id = ?
            """,
            (
                role,
                company,
                location,
                start_date,
                end_date,
                description,
                experience_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("manage_experience"))

    connection.close()

    return render_template(
        "admin/edit_experience.html",
        experience=experience
    )

# DELETE EXPERIENCE
@app.route("/admin/experience/delete/<int:experience_id>", methods=["POST"])
@login_required
def delete_experience(experience_id):

    connection = get_db_connection()

    experience = connection.execute(
        "SELECT * FROM experience WHERE id = ?",
        (experience_id,)
    ).fetchone()

    if experience is None:
        connection.close()
        return "Experience not found", 404

    connection.execute(
        "DELETE FROM experience WHERE id = ?",
        (experience_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_experience"))

# =========================
# EDUCATION MANAGEMENT
# =========================

@app.route("/admin/education")
@login_required
def manage_education():
    connection = get_db_connection()

    education = connection.execute(
        "SELECT * FROM education ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/education.html",
        education=education
    )


@app.route("/admin/education/add", methods=["POST"])
@login_required
def add_education():
    degree = request.form["degree"]
    institution = request.form["institution"]
    location = request.form["location"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    description = request.form["description"]

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO education
        (degree, institution, location, start_date, end_date, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            degree,
            institution,
            location,
            start_date,
            end_date,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_education"))


@app.route("/admin/education/edit/<int:education_id>", methods=["GET", "POST"])
@login_required
def edit_education(education_id):

    connection = get_db_connection()

    education = connection.execute(
        "SELECT * FROM education WHERE id = ?",
        (education_id,)
    ).fetchone()

    if not education:
        connection.close()
        return "Education entry not found", 404

    if request.method == "POST":

        degree = request.form["degree"]
        institution = request.form["institution"]
        location = request.form["location"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        description = request.form["description"]

        connection.execute(
            """
            UPDATE education
            SET degree = ?,
                institution = ?,
                location = ?,
                start_date = ?,
                end_date = ?,
                description = ?
            WHERE id = ?
            """,
            (
                degree,
                institution,
                location,
                start_date,
                end_date,
                description,
                education_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("manage_education"))

    connection.close()

    return render_template(
        "admin/edit_education.html",
        education=education
    )

@app.route(
    "/admin/education/delete/<int:education_id>",
    methods=["POST"]
)
@login_required
def delete_education(education_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM education WHERE id = ?",
        (education_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_education"))

# =========================
# CERTIFICATIONS MANAGEMENT
# =========================

@app.route("/admin/certifications")
@login_required
def manage_certifications():
    connection = get_db_connection()

    certifications = connection.execute(
        "SELECT * FROM certifications ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/certifications.html",
        certifications=certifications
    )


@app.route("/admin/certifications/add", methods=["POST"])
@login_required
def add_certification():
    name = request.form["name"]
    issuer = request.form["issuer"]
    issue_date = request.form["issue_date"]
    credential_url = request.form["credential_url"]
    description = request.form["description"]

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO certifications
        (name, issuer, issue_date, credential_url, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            issuer,
            issue_date,
            credential_url,
            description
        )
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_certifications"))


@app.route("/admin/certifications/edit/<int:certification_id>", methods=["GET", "POST"])
@login_required
def edit_certification(certification_id):

    connection = get_db_connection()

    certification = connection.execute(
        "SELECT * FROM certifications WHERE id = ?",
        (certification_id,)
    ).fetchone()

    if not certification:
        connection.close()
        return "Certification not found", 404

    if request.method == "POST":

        name = request.form["name"]
        issuer = request.form["issuer"]
        issue_date = request.form["issue_date"]
        credential_url = request.form["credential_url"]
        description = request.form["description"]

        connection.execute(
            """
            UPDATE certifications
            SET name = ?,
                issuer = ?,
                issue_date = ?,
                credential_url = ?,
                description = ?
            WHERE id = ?
            """,
            (
                name,
                issuer,
                issue_date,
                credential_url,
                description,
                certification_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("manage_certifications"))

    connection.close()

    return render_template(
        "admin/edit_certification.html",
        certification=certification
    )


@app.route(
    "/admin/certifications/delete/<int:certification_id>",
    methods=["POST"]
)
@login_required
def delete_certification(certification_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM certifications WHERE id = ?",
        (certification_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_certifications"))





    
       

# =========================
# RESUME MANAGEMENT
# =========================

@app.route("/admin/resume", methods=["GET", "POST"])
@login_required
def manage_resume():

    connection = get_db_connection()

    settings = connection.execute(
        "SELECT * FROM site_settings WHERE id = 1"
    ).fetchone()

    if request.method == "POST":

        if "resume" not in request.files:
            connection.close()
            return "No file selected", 400

        file = request.files["resume"]

        if file.filename == "":
            connection.close()
            return "No file selected", 400

        if not allowed_file(file):
            connection.close()
            return "Only valid PDF files are allowed", 400

        filename = secure_filename(file.filename)

        # Remove the old resume if one exists
        old_resume = settings["resume_url"]

        if old_resume:
            old_path = os.path.join(
                app.root_path,
                "static",
                old_resume.lstrip("/")
            )

            if os.path.exists(old_path):
                os.remove(old_path)

        # Save the new resume
        file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        resume_url = f"/resume/{filename}"

        connection.execute(
            """
            UPDATE site_settings
            SET resume_url = ?
            WHERE id = 1
            """,
            (resume_url,)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("manage_resume"))

    connection.close()

    return render_template(
        "admin/resume.html",
        settings=settings
    )

# =========================
# CONTACT FORM
# =========================

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    message = request.form["message"].strip()

    if not name or not email or not message:
        return "All fields are required", 400

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO messages (name, email, message)
        VALUES (?, ?, ?)
        """,
        (name, email, message)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home") + "#contact")
# =========================
# CONTACT MESSAGES
# =========================

@app.route("/admin/messages")
@login_required
def manage_messages():
    connection = get_db_connection()

    messages = connection.execute(
        "SELECT * FROM messages ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin/messages.html",
        messages=messages
    )


@app.route(
    "/admin/messages/delete/<int:message_id>",
    methods=["POST"]
)
@login_required
def delete_message(message_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM messages WHERE id = ?",
        (message_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_messages"))

# -------------------------
# LOGOUT
# -------------------------

@app.route("/admin/logout")
@login_required
def admin_logout():

    logout_user()

    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"

    app.run(debug=debug_mode)