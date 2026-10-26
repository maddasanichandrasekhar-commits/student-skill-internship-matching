"""
Student Skill and Internship Matching System Using Sets and Relations
======================================================================
Flask Web Application
Discrete Mathematics Demonstration Project
"""

import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, abort
)
from werkzeug.security import check_password_hash, generate_password_hash

import database as db
import matching_engine as me

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "discrete-math-matching-secret-key-2026-xyz")

# Ensure DB is initialized when app starts
with app.app_context():
    db.init_db()


# -------------------------------------------------------------
# Context Processors & Template Filters
# -------------------------------------------------------------

@app.context_processor
def inject_user_and_globals():
    """Inject current logged in user details into all templates."""
    user = None
    role = session.get("role")
    if role == "student" and "user_id" in session:
        user = db.get_student_by_id(session["user_id"])
    elif role == "admin" and "admin_username" in session:
        user = db.get_admin_by_username(session["admin_username"])
    return {
        "current_user": user,
        "current_role": role,
        "app_title": "Student Skill & Internship Matching System"
    }


@app.template_filter("split_skills")
def split_skills_filter(s):
    """Template filter to parse a comma-separated skill string into a list."""
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


# -------------------------------------------------------------
# Authentication Decorators
# -------------------------------------------------------------

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "student" or "user_id" not in session:
            flash("Please log in as a student to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin" or "admin_id" not in session:
            flash("Administrator login required.", "danger")
            return redirect(url_for("admin_login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------------------------------------
# Public & General Routes
# -------------------------------------------------------------

@app.route("/")
def index():
    """Module 1: Home Page with project overview, statistics, and discrete math showcase."""
    all_internships = db.get_all_internships(status="Active")
    all_students = db.get_all_students()
    all_apps = db.get_all_applications()
    
    # Calculate stats
    stats = {
        "total_students": len(all_students),
        "total_internships": len(all_internships),
        "total_applications": len(all_apps),
        "cartesian_pairs": len(all_students) * len(all_internships)
    }

    # If student is logged in, compute match scores for featured internships
    student = None
    featured = all_internships[:4]
    evaluations = {}
    if session.get("role") == "student" and "user_id" in session:
        student = db.get_student_by_id(session["user_id"])
        if student:
            for item in featured:
                evaluations[item["id"]] = me.evaluate_student_internship_match(student, item)

    return render_template(
        "index.html", 
        stats=stats, 
        internships=featured,
        student=student,
        evaluations=evaluations
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Unified / Student login route with quick demo options."""
    if request.method == "POST":
        email_or_id = request.form.get("email_or_id", "").strip()
        password = request.form.get("password", "")

        # Try looking up student by email first, then student_id code
        student = db.get_student_by_email(email_or_id)
        if not student:
            student = db.get_student_by_code(email_or_id)

        if student and check_password_hash(student["password_hash"], password):
            session.clear()
            session["role"] = "student"
            session["user_id"] = student["id"]
            session["user_name"] = student["name"]
            session["student_id_code"] = student["student_id"]
            flash(f"Welcome back, {student['name']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("student_dashboard"))
        
        flash("Invalid email/student ID or password. Please try again.", "danger")

    # Sample students for quick-login demo
    demo_students = db.get_all_students()[:4]
    return render_template("login.html", demo_students=demo_students)


@app.route("/demo-login/<role>/<identifier>")
def demo_login(role, identifier):
    """Instant login shortcut for reviewers, presentation evaluators, and testing."""
    session.clear()
    if role == "student":
        student = db.get_student_by_code(identifier)
        if not student:
            student = db.get_student_by_id(int(identifier)) if identifier.isdigit() else None
        if student:
            session["role"] = "student"
            session["user_id"] = student["id"]
            session["user_name"] = student["name"]
            session["student_id_code"] = student["student_id"]
            flash(f"Logged in as demo student: {student['name']} ({student['student_id']})", "info")
            return redirect(url_for("student_dashboard"))
    elif role == "admin":
        admin = db.get_admin_by_username("admin")
        if admin:
            session["role"] = "admin"
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            session["admin_name"] = admin["full_name"]
            flash("Logged in as Administrator (Head of Placement)", "info")
            return redirect(url_for("admin_dashboard"))

    flash("Demo user not found.", "warning")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Module 2: Student Registration with full academic profile and skill set input."""
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip().upper()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        department = request.form.get("department", "").strip()
        degree = request.form.get("degree", "").strip()
        year_of_study = request.form.get("year_of_study", 1)
        cgpa = request.form.get("cgpa", 0.0)
        skills = request.form.get("skills", "").strip()
        qualifications = request.form.get("qualifications", "").strip()
        interests = request.form.get("interests", "").strip()
        completed_courses = request.form.get("completed_courses", "").strip()

        # Validation
        if not student_id or not name or not email or not password or not department or not skills:
            flash("Please fill in all mandatory fields (marked with *).", "warning")
            return render_template("register.html", form=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", form=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template("register.html", form=request.form)

        # Check uniqueness
        if db.get_student_by_email(email):
            flash("A student with this email is already registered.", "danger")
            return render_template("register.html", form=request.form)

        if db.get_student_by_code(student_id):
            flash("A student with this Student ID already exists.", "danger")
            return render_template("register.html", form=request.form)

        try:
            cgpa_val = float(cgpa)
            if not (0.0 <= cgpa_val <= 10.0):
                flash("CGPA must be between 0.0 and 10.0.", "warning")
                return render_template("register.html", form=request.form)
        except ValueError:
            flash("Please enter a valid numeric CGPA.", "warning")
            return render_template("register.html", form=request.form)

        # Create student in SQLite
        new_id = db.create_student(
            student_id=student_id,
            name=name,
            email=email,
            password=password,
            department=department,
            degree=degree,
            year_of_study=int(year_of_study),
            cgpa=cgpa_val,
            skills=skills,
            qualifications=qualifications,
            interests=interests,
            completed_courses=completed_courses
        )

        session.clear()
        session["role"] = "student"
        session["user_id"] = new_id
        session["user_name"] = name
        session["student_id_code"] = student_id

        flash(f"Registration successful! Welcome to the Matching System, {name}.", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("register.html", form={})


@app.route("/logout")
def logout():
    """Clear session and log user out."""
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("index"))


@app.route("/internships")
def internships_catalog():
    """Browse all internships with search query, department, work mode, and CGPA filters."""
    q = request.args.get("q", "").strip().lower()
    dept_filter = request.args.get("department", "").strip()
    mode_filter = request.args.get("work_mode", "").strip()
    min_cgpa_filter = request.args.get("min_cgpa", "").strip()

    all_internships = db.get_all_internships(status="Active")
    filtered = []

    for item in all_internships:
        # Search text match
        if q:
            searchable = f"{item['title']} {item['company_name']} {item['description']} {item['required_skills']}".lower()
            if q not in searchable:
                continue

        # Department filter
        if dept_filter and dept_filter != "all":
            depts = [d.strip().lower() for d in item["eligible_departments"].split(",")]
            if dept_filter.lower() not in depts and "all" not in depts:
                continue

        # Work mode filter
        if mode_filter and mode_filter != "all":
            if item["work_mode"].lower() != mode_filter.lower():
                continue

        # Min CGPA filter
        if min_cgpa_filter:
            try:
                cgpa_val = float(min_cgpa_filter)
                if float(item["min_cgpa"]) > cgpa_val:
                    continue
            except ValueError:
                pass

        filtered.append(item)

    # Evaluate matches for logged in student
    evaluations = {}
    applied_map = {}
    student = None
    if session.get("role") == "student" and "user_id" in session:
        student = db.get_student_by_id(session["user_id"])
        if student:
            for item in filtered:
                evaluations[item["id"]] = me.evaluate_student_internship_match(student, item)
            # Find which internships the student already applied to
            apps = db.get_student_applications(student["id"])
            applied_map = {a["internship_id"]: a["status"] for a in apps}

    # Department list for filter dropdown
    departments = [
        "Computer Science", "Information Technology", "Electronics & Communication",
        "Biotechnology", "Bioinformatics", "Data Science", "Mathematics"
    ]

    return render_template(
        "internships.html",
        internships=filtered,
        evaluations=evaluations,
        applied_map=applied_map,
        student=student,
        q=q,
        selected_dept=dept_filter,
        selected_mode=mode_filter,
        min_cgpa=min_cgpa_filter,
        departments=departments
    )


@app.route("/internship/<int:internship_id>")
def internship_detail(internship_id):
    """Detailed view of an internship with Discrete Math set analysis against the logged in student."""
    internship = db.get_internship_by_id(internship_id)
    if not internship:
        flash("Internship not found.", "warning")
        return redirect(url_for("internships_catalog"))

    student = None
    evaluation = None
    already_applied = False
    app_status = None

    if session.get("role") == "student" and "user_id" in session:
        student = db.get_student_by_id(session["user_id"])
        if student:
            evaluation = me.evaluate_student_internship_match(student, internship)
            existing = db.query_db(
                "SELECT * FROM applications WHERE student_id = ? AND internship_id = ?",
                (student["id"], internship_id), one=True
            )
            if existing:
                already_applied = True
                app_status = existing["status"]

    return render_template(
        "internship_detail.html",
        internship=internship,
        student=student,
        evaluation=evaluation,
        already_applied=already_applied,
        app_status=app_status
    )


# -------------------------------------------------------------
# Module 5: Discrete Mathematics Laboratory & Visualizer
# -------------------------------------------------------------

@app.route("/math-lab")
def math_lab():
    """
    Dedicated Discrete Mathematics Interactive Playground:
    - Interactive Set Calculator (S, R, S ∩ R, R − S, S − R, S ∪ R, S △ R)
    - Venn Diagram generator
    - Cartesian Product A × B explorer
    - Binary Relation Matrix and Relations (R_skill, R_eligible, R_match)
    - Domain, Codomain, Range, and Function properties (injective, surjective, bijective)
    """
    students = db.get_all_students()
    internships = db.get_all_internships(status="Active")
    
    # Default threshold
    threshold = float(request.args.get("threshold", 50.0))
    
    # Compute relations on seeded/current data
    relations_data = me.compute_relations_and_mappings(students, internships, threshold=threshold)
    cartesian_data = me.compute_cartesian_product(students, internships)

    # Preset examples for interactive demonstration
    presets = [
        {
            "name": "Classroom Master Prompt Example",
            "S": "Python, SQL, HTML, Java",
            "R": "Python, SQL, Excel",
            "desc": "Expected: Common={Python, SQL}, Missing={Excel}, Additional={HTML, Java}, Match=66.67%"
        },
        {
            "name": "Software Developer Intern vs Rahul",
            "S": "Python, SQL, HTML, Java, Git, React",
            "R": "Python, SQL, HTML, Java, Git, Data Structures",
            "desc": "High overlap (83.33% match) with one missing foundational skill."
        },
        {
            "name": "Bioinformatics Intern vs Rohan",
            "S": "Python, R, Genomics, BLAST, Molecular Biology, Linux, SQL",
            "R": "Python, R, Genomics, BLAST, Molecular Biology, Linux",
            "desc": "100% skill match (Subset relation R ⊆ S)."
        },
        {
            "name": "Disjoint Skill Sets (Zero Overlap)",
            "S": "Biochemistry, Molecular Biology, PCR",
            "R": "React, Node.js, CSS, JavaScript",
            "desc": "Intersection is Empty Set ∅, Match = 0%."
        },
        {
            "name": "Empty Requirement Edge Case",
            "S": "Python, Java",
            "R": "",
            "desc": "Empty requirement set R = ∅; vacuously satisfied (100%)."
        }
    ]

    return render_template(
        "math_lab.html",
        students=students,
        internships=internships,
        relations_data=relations_data,
        cartesian_data=cartesian_data,
        threshold=threshold,
        presets=presets
    )


@app.route("/api/set-operations", methods=["POST"])
def api_set_operations():
    """API endpoint to calculate discrete math set operations on custom user inputs."""
    data = request.get_json() or {}
    student_skills_raw = data.get("student_skills", "")
    required_skills_raw = data.get("required_skills", "")

    s_set = me.parse_to_set(student_skills_raw)
    r_set = me.parse_to_set(required_skills_raw)
    result = me.set_operations(s_set, r_set)
    return jsonify(result)


# -------------------------------------------------------------
# Student Portal Routes
# -------------------------------------------------------------

@app.route("/student/dashboard")
@student_required
def student_dashboard():
    """
    Module 4 & Student Portal:
    Computes set operations and matching against every active internship.
    Categorizes into Eligible & Recommended, Eligible with Gap, and Ineligible.
    """
    student = db.get_student_by_id(session["user_id"])
    internships = db.get_all_internships(status="Active")
    applications = db.get_student_applications(student["id"])
    applied_ids = {a["internship_id"]: a for a in applications}

    # Evaluate matches
    evaluated_list = []
    skill_frequency_missing = {}

    for item in internships:
        eval_res = me.evaluate_student_internship_match(student, item)
        eval_res["applied"] = item["id"] in applied_ids
        eval_res["application"] = applied_ids.get(item["id"])
        eval_res["internship"] = item
        evaluated_list.append(eval_res)

        # Collect missing skills for learning recommendation
        if eval_res["is_eligible"]:
            for ms in eval_res["missing_skills"]:
                skill_frequency_missing[ms] = skill_frequency_missing.get(ms, 0) + 1

    # Sort: Eligible first, then descending by skill match %
    evaluated_list.sort(key=lambda x: (x["is_eligible"], x["skill_match_percentage"]), reverse=True)

    # Top recommended skills to learn
    recommended_skills_to_learn = sorted(
        skill_frequency_missing.items(), key=lambda item: item[1], reverse=True
    )[:5]

    # Quick metrics
    total_eligible = sum(1 for e in evaluated_list if e["is_eligible"])
    high_match = sum(1 for e in evaluated_list if e["is_eligible"] and e["skill_match_percentage"] >= 70)

    student_skills_set = me.parse_to_set(student["skills"])

    return render_template(
        "student_dashboard.html",
        student=student,
        student_skills=sorted(list(student_skills_set)),
        evaluated_list=evaluated_list,
        applications=applications,
        total_eligible=total_eligible,
        high_match=high_match,
        recommended_skills_to_learn=recommended_skills_to_learn
    )


@app.route("/student/profile", methods=["GET", "POST"])
@student_required
def student_profile():
    """Module 2: Update Student Profile, skills set, and academic parameters."""
    student = db.get_student_by_id(session["user_id"])

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        degree = request.form.get("degree", "").strip()
        year_of_study = request.form.get("year_of_study", 1)
        cgpa = request.form.get("cgpa", 0.0)
        skills = request.form.get("skills", "").strip()
        qualifications = request.form.get("qualifications", "").strip()
        interests = request.form.get("interests", "").strip()
        completed_courses = request.form.get("completed_courses", "").strip()

        if not name or not department or not skills:
            flash("Name, Department, and Skills are required fields.", "warning")
            return render_template("student_profile.html", student=student)

        try:
            cgpa_val = float(cgpa)
            if not (0.0 <= cgpa_val <= 10.0):
                flash("CGPA must be between 0.0 and 10.0.", "warning")
                return render_template("student_profile.html", student=student)
        except ValueError:
            flash("Invalid CGPA value.", "warning")
            return render_template("student_profile.html", student=student)

        db.update_student(
            student_id=student["id"],
            name=name,
            department=department,
            degree=degree,
            year_of_study=int(year_of_study),
            cgpa=cgpa_val,
            skills=skills,
            qualifications=qualifications,
            interests=interests,
            completed_courses=completed_courses
        )

        session["user_name"] = name
        flash("Profile updated successfully! Matches have been recalculated.", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("student_profile.html", student=student)


@app.route("/student/applications")
@student_required
def student_applications():
    """View status of all applications submitted by the logged in student."""
    student = db.get_student_by_id(session["user_id"])
    applications = db.get_student_applications(student["id"])
    return render_template("student_applications.html", student=student, applications=applications)


@app.route("/apply/<int:internship_id>", methods=["POST"])
@student_required
def apply_internship(internship_id):
    """Handle student application to an internship with real-time set math calculation."""
    student = db.get_student_by_id(session["user_id"])
    internship = db.get_internship_by_id(internship_id)

    if not internship:
        flash("Internship not found.", "danger")
        return redirect(url_for("internships_catalog"))

    eval_res = me.evaluate_student_internship_match(student, internship)
    common_str = ", ".join(eval_res["common_skills"])
    missing_str = ", ".join(eval_res["missing_skills"])

    success, msg = db.apply_for_internship(
        student_id=student["id"],
        internship_id=internship_id,
        match_percentage=eval_res["skill_match_percentage"],
        is_eligible=eval_res["is_eligible"],
        common_skills=common_str,
        missing_skills=missing_str
    )

    if success:
        flash(f"Application for '{internship['title']}' submitted successfully!", "success")
    else:
        flash(msg, "warning")

    return redirect(request.referrer or url_for("student_dashboard"))


# -------------------------------------------------------------
# Module 3 & Admin Portal Routes
# -------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin / Placement Coordinator Login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = db.get_admin_by_username(username)
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["role"] = "admin"
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            session["admin_name"] = admin["full_name"]
            flash(f"Welcome, {admin['full_name']}!", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin username or password.", "danger")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin Dashboard with Chart.js analytics and Discrete Math overview."""
    students = db.get_all_students()
    internships = db.get_all_internships()
    applications = db.get_all_applications()

    # Pre-calculate analytics for Chart.js
    # 1. Internships per department
    dept_counts = {}
    for i in internships:
        depts = [d.strip() for d in i["eligible_departments"].split(",") if d.strip()]
        for d in depts:
            dept_counts[d] = dept_counts.get(d, 0) + 1

    # 2. Application statuses
    status_counts = {"Applied": 0, "Under Review": 0, "Shortlisted": 0, "Accepted": 0, "Rejected": 0}
    for a in applications:
        s = a.get("status", "Applied")
        status_counts[s] = status_counts.get(s, 0) + 1

    # 3. Overall match relation cardinality at 50% threshold
    rel_data = me.compute_relations_and_mappings(students, internships, threshold=50.0)

    # 4. Department distribution of students
    student_depts = {}
    for s in students:
        sd = s["department"]
        student_depts[sd] = student_depts.get(sd, 0) + 1

    return render_template(
        "admin_dashboard.html",
        students_count=len(students),
        internships_count=len(internships),
        applications_count=len(applications),
        cartesian_size=len(students) * len(internships),
        active_matches_count=rel_data["r_match_cardinality"],
        dept_counts=dept_counts,
        status_counts=status_counts,
        student_depts=student_depts,
        recent_applications=applications[:6]
    )


@app.route("/admin/internships")
@admin_required
def admin_internships():
    """Module 3: Manage internships listing."""
    internships = db.get_all_internships()
    return render_template("admin_internships.html", internships=internships)


@app.route("/admin/internships/new", methods=["GET", "POST"])
@admin_required
def admin_new_internship():
    """Module 3: Add new internship opportunity."""
    if request.method == "POST":
        code = request.form.get("internship_code", "").strip().upper()
        title = request.form.get("title", "").strip()
        company = request.form.get("company_name", "").strip()
        desc = request.form.get("description", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        min_cgpa = request.form.get("min_cgpa", 6.0)
        eligible_depts = request.form.get("eligible_departments", "").strip()
        required_quals = request.form.get("required_qualifications", "").strip()
        duration = request.form.get("duration", "").strip()
        work_mode = request.form.get("work_mode", "Hybrid").strip()
        location = request.form.get("location", "").strip()
        stipend = request.form.get("stipend", "").strip()
        deadline = request.form.get("deadline", "").strip()
        apply_link = request.form.get("apply_link", "").strip()
        status = request.form.get("status", "Active").strip()

        if not code or not title or not company or not required_skills:
            flash("Code, Title, Company, and Required Skills are mandatory.", "warning")
            return render_template("admin_internship_form.html", form=request.form, is_edit=False)

        try:
            db.create_internship(
                internship_code=code,
                title=title,
                company_name=company,
                description=desc,
                required_skills=required_skills,
                min_cgpa=float(min_cgpa),
                eligible_departments=eligible_depts,
                required_qualifications=required_quals,
                duration=duration,
                work_mode=work_mode,
                location=location,
                stipend=stipend,
                deadline=deadline,
                apply_link=apply_link,
                status=status
            )
            flash(f"Internship '{title}' ({code}) added successfully!", "success")
            return redirect(url_for("admin_internships"))
        except Exception as e:
            flash(f"Error creating internship: {str(e)}", "danger")

    return render_template("admin_internship_form.html", form={}, is_edit=False)


@app.route("/admin/internships/edit/<int:internship_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_internship(internship_id):
    """Module 3: Edit existing internship."""
    internship = db.get_internship_by_id(internship_id)
    if not internship:
        flash("Internship not found.", "danger")
        return redirect(url_for("admin_internships"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company_name", "").strip()
        desc = request.form.get("description", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        min_cgpa = request.form.get("min_cgpa", 6.0)
        eligible_depts = request.form.get("eligible_departments", "").strip()
        required_quals = request.form.get("required_qualifications", "").strip()
        duration = request.form.get("duration", "").strip()
        work_mode = request.form.get("work_mode", "Hybrid").strip()
        location = request.form.get("location", "").strip()
        stipend = request.form.get("stipend", "").strip()
        deadline = request.form.get("deadline", "").strip()
        apply_link = request.form.get("apply_link", "").strip()
        status = request.form.get("status", "Active").strip()

        db.update_internship(
            internship_id=internship_id,
            title=title,
            company_name=company,
            description=desc,
            required_skills=required_skills,
            min_cgpa=float(min_cgpa),
            eligible_departments=eligible_depts,
            required_qualifications=required_quals,
            duration=duration,
            work_mode=work_mode,
            location=location,
            stipend=stipend,
            deadline=deadline,
            apply_link=apply_link,
            status=status
        )
        flash(f"Internship '{title}' updated successfully!", "success")
        return redirect(url_for("admin_internships"))

    return render_template("admin_internship_form.html", form=internship, is_edit=True)


@app.route("/admin/internships/delete/<int:internship_id>", methods=["POST"])
@admin_required
def admin_delete_internship(internship_id):
    """Delete an internship."""
    db.delete_internship(internship_id)
    flash("Internship deleted successfully.", "info")
    return redirect(url_for("admin_internships"))


@app.route("/admin/students")
@admin_required
def admin_students():
    """View roster of all registered students with skills & CGPA."""
    students = db.get_all_students()
    return render_template("admin_students.html", students=students)


@app.route("/admin/applications")
@admin_required
def admin_applications():
    """Manage candidate applications and update statuses."""
    applications = db.get_all_applications()
    return render_template("admin_applications.html", applications=applications)


@app.route("/admin/application/<int:app_id>/status", methods=["POST"])
@admin_required
def admin_update_app_status(app_id):
    """Update status of student application (e.g. Under Review, Shortlisted, Accepted, Rejected)."""
    new_status = request.form.get("status", "Applied")
    db.update_application_status(app_id, new_status)
    flash(f"Application #{app_id} status updated to '{new_status}'.", "success")
    return redirect(url_for("admin_applications"))


@app.route("/admin/relation-matrix")
@admin_required
def admin_relation_matrix():
    """Module 5: Admin Discrete Mathematics Matrix and Relational Analytics."""
    students = db.get_all_students()
    internships = db.get_all_internships(status="Active")
    threshold = float(request.args.get("threshold", 50.0))
    rel_data = me.compute_relations_and_mappings(students, internships, threshold=threshold)
    return render_template("admin_relation_matrix.html", rel_data=rel_data, threshold=threshold)


# -------------------------------------------------------------
# Main Application Entry Point
# -------------------------------------------------------------

if __name__ == "__main__":
    # Run locally on port 5000 in debug mode
    print("=" * 60)
    print("Starting Student Skill & Internship Matching System")
    print("Discrete Mathematics Demonstration Web App")
    print("URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
