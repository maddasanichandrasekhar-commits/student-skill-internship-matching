"""
Database Module for Student Skill and Internship Matching System
================================================================
SQLite storage with helpers for students, internships, applications, and admin.
Includes automatic schema creation and realistic initial seed data.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matching_system.db")


def get_db_connection():
    """Create and return a database connection with row factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and pre-populate sample data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        department TEXT NOT NULL,
        degree TEXT NOT NULL,
        year_of_study INTEGER NOT NULL,
        cgpa REAL NOT NULL,
        skills TEXT NOT NULL,
        qualifications TEXT,
        interests TEXT,
        completed_courses TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Internships Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        min_cgpa REAL NOT NULL DEFAULT 6.0,
        eligible_departments TEXT NOT NULL,
        required_qualifications TEXT NOT NULL,
        duration TEXT NOT NULL,
        work_mode TEXT NOT NULL,
        location TEXT NOT NULL,
        stipend TEXT NOT NULL,
        deadline TEXT NOT NULL,
        apply_link TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Applications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        internship_id INTEGER NOT NULL,
        match_percentage REAL NOT NULL,
        is_eligible INTEGER NOT NULL DEFAULT 1,
        common_skills TEXT,
        missing_skills TEXT,
        status TEXT DEFAULT 'Applied',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(internship_id) REFERENCES internships(id) ON DELETE CASCADE,
        UNIQUE(student_id, internship_id)
    );
    """)

    # 4. Admins Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'Administrator'
    );
    """)

    conn.commit()

    # Seed Admin User if not present
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            ("admin", generate_password_hash("admin123"), "System Administrator", "Head of Placement")
        )

    # Seed Sample Students if not present
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            (
                "STU101", "Rahul Sharma", "rahul.sharma@college.edu", generate_password_hash("student123"),
                "Computer Science", "B.Tech", 3, 8.75,
                "Python, SQL, HTML, Java, Git, React",
                "B.Tech in Computer Science & Engineering",
                "Software Engineering, Cloud Architecture, Full Stack Web Dev",
                "Discrete Mathematics, Data Structures & Algorithms, DBMS, Operating Systems"
            ),
            (
                "STU102", "Ananya Patel", "ananya.patel@college.edu", generate_password_hash("student123"),
                "Information Technology", "B.Tech", 4, 8.20,
                "Python, SQL, Excel, Power BI, Statistics, Tableau",
                "B.Tech in Information Technology",
                "Data Analytics, Business Intelligence, Data Pipelines",
                "Discrete Mathematics, Statistical Computing, Database Systems, Big Data Analytics"
            ),
            (
                "STU103", "Priya Nair", "priya.nair@college.edu", generate_password_hash("student123"),
                "Biotechnology", "B.Tech", 3, 9.15,
                "Biochemistry, Lab Techniques, Molecular Biology, PCR, Genetics, R",
                "B.Tech in Biotechnology",
                "Genetic Engineering, Molecular Diagnostics, Pharmaceutical Research",
                "Bioprocess Engineering, Cell Biology, Molecular Genetics, Bioethics"
            ),
            (
                "STU104", "Rohan Verma", "rohan.verma@college.edu", generate_password_hash("student123"),
                "Bioinformatics", "B.Tech", 4, 8.45,
                "Python, R, Genomics, BLAST, Molecular Biology, Linux, SQL",
                "B.Tech in Bioinformatics",
                "Computational Biology, Structural Genomics, Next-Gen Sequencing",
                "Bioinformatics Algorithms, Discrete Structures, Perl & Python for Bio, Proteomics"
            ),
            (
                "STU105", "Sneha Reddy", "sneha.reddy@college.edu", generate_password_hash("student123"),
                "Computer Science", "B.Tech", 2, 7.80,
                "HTML, CSS, JavaScript, React, Node.js, Git, Figma",
                "B.Tech in Computer Science",
                "Frontend Web Design, UI/UX, Progressive Web Apps",
                "Discrete Mathematics, Web Technologies, Object Oriented Programming"
            ),
            (
                "STU106", "Vikram Malhotra", "vikram.malhotra@college.edu", generate_password_hash("student123"),
                "Electronics & Communication", "B.Tech", 3, 6.90,
                "Python, C++, Embedded Systems, IoT, Linux",
                "B.Tech in ECE",
                "Internet of Things, Robotics, Edge AI",
                "Microprocessors, Signal Processing, Computer Networks"
            )
        ]
        cursor.executemany("""
            INSERT INTO students (
                student_id, name, email, password_hash, department, degree, year_of_study, 
                cgpa, skills, qualifications, interests, completed_courses
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_students)

    # Seed Sample Internships as per requirements
    cursor.execute("SELECT COUNT(*) FROM internships")
    if cursor.fetchone()[0] == 0:
        sample_internships = [
            (
                "INT-SWE-01",
                "Software Developer Intern",
                "Microsoft India",
                "Join our core engineering team to build high-scale cloud microservices, develop clean REST APIs, and optimize database queries.",
                "Python, SQL, HTML, Java, Git, Data Structures",
                7.5,
                "Computer Science, Information Technology, Electronics & Communication",
                "B.Tech, B.E, MCA",
                "6 Months",
                "Hybrid",
                "Hyderabad / Bangalore",
                "₹45,000 / month",
                "2026-11-30",
                "https://careers.microsoft.com",
                "Active"
            ),
            (
                "INT-DATA-02",
                "Data Analyst Intern",
                "Deloitte Consulting",
                "Analyze large-scale enterprise datasets, design executive dashboards, extract actionable business intelligence, and automate SQL reporting pipelines.",
                "Python, SQL, Excel, Power BI, Statistics",
                7.0,
                "Computer Science, Information Technology, Data Science, Mathematics",
                "B.Tech, B.Sc, BCA, MCA",
                "3 Months",
                "Remote",
                "Bangalore / Remote",
                "₹35,000 / month",
                "2026-12-15",
                "https://careers.deloitte.com",
                "Active"
            ),
            (
                "INT-WEB-03",
                "Web Developer Intern",
                "Spotify Labs",
                "Collaborate with UI designers and full-stack developers to craft responsive, accessible web interfaces using React and modern CSS paradigms.",
                "HTML, CSS, JavaScript, React, Node.js",
                6.5,
                "Computer Science, Information Technology, BCA, MCA",
                "B.Tech, B.Sc, BCA",
                "4 Months",
                "Remote",
                "Mumbai / Remote",
                "₹30,000 / month",
                "2026-11-20",
                "https://spotifyjobs.com",
                "Active"
            ),
            (
                "INT-BIO-04",
                "Biotechnology Research Intern",
                "Biocon Biologics",
                "Conduct bench experiments in cell culture, protein purification, PCR assays, and DNA sequencing for next-generation biosimilar drugs.",
                "Biochemistry, Lab Techniques, Molecular Biology, PCR, Genetics",
                8.0,
                "Biotechnology, Biomedical Engineering, Life Sciences",
                "B.Tech, B.Sc, M.Sc, M.Tech",
                "6 Months",
                "On-site",
                "Bangalore Bio-Cluster",
                "₹25,000 / month",
                "2026-12-01",
                "https://biocon.com/careers",
                "Active"
            ),
            (
                "INT-BINF-05",
                "Bioinformatics & Genomics Intern",
                "Illumina Life Sciences",
                "Process high-throughput NGS genetic datasets, run sequence alignments using BLAST and specialized biopython pipelines in a Linux HPC cluster.",
                "Python, R, Genomics, BLAST, Molecular Biology, Linux",
                7.5,
                "Bioinformatics, Biotechnology, Computer Science",
                "B.Tech, M.Tech, M.Sc",
                "6 Months",
                "Hybrid",
                "Chennai / Hybrid",
                "₹32,000 / month",
                "2026-12-10",
                "https://illumina.com/careers",
                "Active"
            ),
            (
                "INT-AIML-06",
                "AI/ML Research Intern",
                "TensorMind Labs",
                "Implement neural network models, optimize hyperparameter searches, and apply discrete math algorithms to machine learning workflows.",
                "Python, PyTorch, Linear Algebra, Machine Learning, SQL, Git",
                8.0,
                "Computer Science, Information Technology, Data Science",
                "B.Tech, M.Tech",
                "6 Months",
                "Hybrid",
                "Gurugram / Hybrid",
                "₹50,000 / month",
                "2026-11-25",
                "https://tensormind.ai/careers",
                "Active"
            )
        ]
        cursor.executemany("""
            INSERT INTO internships (
                internship_code, title, company_name, description, required_skills, min_cgpa, 
                eligible_departments, required_qualifications, duration, work_mode, 
                location, stipend, deadline, apply_link, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_internships)

    # Seed initial applications so the system looks active and lived-in
    cursor.execute("SELECT COUNT(*) FROM applications")
    if cursor.fetchone()[0] == 0:
        sample_apps = [
            (1, 1, 83.33, 1, "Python, SQL, HTML, Java, Git", "Data Structures", "Shortlisted"),
            (2, 2, 100.0, 1, "Python, SQL, Excel, Power BI, Statistics", "", "Under Review"),
            (3, 4, 100.0, 1, "Biochemistry, Lab Techniques, Molecular Biology, PCR, Genetics", "", "Shortlisted"),
            (4, 5, 100.0, 1, "Python, R, Genomics, BLAST, Molecular Biology, Linux", "", "Applied"),
            (5, 3, 100.0, 1, "HTML, CSS, JavaScript, React, Node.js", "", "Accepted"),
        ]
        cursor.executemany("""
            INSERT INTO applications (
                student_id, internship_id, match_percentage, is_eligible, 
                common_skills, missing_skills, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_apps)

    conn.commit()
    conn.close()


def query_db(query: str, args=(), one: bool = False):
    """Execute a query and fetch results as dictionaries."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    if not rv:
        return None if one else []
    return (dict(rv[0])) if one else [dict(x) for x in rv]


def execute_db(query: str, args=()):
    """Execute an INSERT, UPDATE, or DELETE query and commit."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    last_id = cur.lastrowid
    conn.commit()
    conn.close()
    return last_id


# ------------------ STUDENT HELPERS ------------------ #

def get_all_students():
    """Retrieve all students ordered by name."""
    return query_db("SELECT * FROM students ORDER BY name ASC")


def get_student_by_id(student_id: int):
    """Retrieve student by primary key ID."""
    return query_db("SELECT * FROM students WHERE id = ?", (student_id,), one=True)


def get_student_by_email(email: str):
    """Retrieve student by email."""
    return query_db("SELECT * FROM students WHERE LOWER(email) = LOWER(?)", (email.strip(),), one=True)


def get_student_by_code(code: str):
    """Retrieve student by college student ID code (e.g. STU101)."""
    return query_db("SELECT * FROM students WHERE UPPER(student_id) = UPPER(?)", (code.strip(),), one=True)


def create_student(student_id: str, name: str, email: str, password: str, department: str,
                   degree: str, year_of_study: int, cgpa: float, skills: str,
                   qualifications: str = "", interests: str = "", completed_courses: str = ""):
    """Insert a new student with hashed password."""
    password_hash = generate_password_hash(password)
    return execute_db("""
        INSERT INTO students (
            student_id, name, email, password_hash, department, degree, 
            year_of_study, cgpa, skills, qualifications, interests, completed_courses
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id.strip().upper(), name.strip(), email.strip().lower(), password_hash,
        department.strip(), degree.strip(), int(year_of_study), float(cgpa),
        skills.strip(), qualifications.strip(), interests.strip(), completed_courses.strip()
    ))


def update_student(student_id: int, name: str, department: str, degree: str,
                   year_of_study: int, cgpa: float, skills: str,
                   qualifications: str = "", interests: str = "", completed_courses: str = ""):
    """Update student profile details."""
    return execute_db("""
        UPDATE students SET 
            name = ?, department = ?, degree = ?, year_of_study = ?,
            cgpa = ?, skills = ?, qualifications = ?, interests = ?, completed_courses = ?
        WHERE id = ?
    """, (
        name.strip(), department.strip(), degree.strip(), int(year_of_study),
        float(cgpa), skills.strip(), qualifications.strip(), interests.strip(),
        completed_courses.strip(), student_id
    ))


# ------------------ INTERNSHIP HELPERS ------------------ #

def get_all_internships(status: str = None):
    """Retrieve internships, optionally filtered by status."""
    if status:
        return query_db("SELECT * FROM internships WHERE status = ? ORDER BY id DESC", (status,))
    return query_db("SELECT * FROM internships ORDER BY id DESC")


def get_internship_by_id(internship_id: int):
    """Retrieve internship by primary key ID."""
    return query_db("SELECT * FROM internships WHERE id = ?", (internship_id,), one=True)


def create_internship(internship_code: str, title: str, company_name: str, description: str,
                      required_skills: str, min_cgpa: float, eligible_departments: str,
                      required_qualifications: str, duration: str, work_mode: str,
                      location: str, stipend: str, deadline: str, apply_link: str = "", status: str = "Active"):
    """Insert a new internship."""
    return execute_db("""
        INSERT INTO internships (
            internship_code, title, company_name, description, required_skills,
            min_cgpa, eligible_departments, required_qualifications, duration,
            work_mode, location, stipend, deadline, apply_link, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        internship_code.strip().upper(), title.strip(), company_name.strip(),
        description.strip(), required_skills.strip(), float(min_cgpa),
        eligible_departments.strip(), required_qualifications.strip(),
        duration.strip(), work_mode.strip(), location.strip(), stipend.strip(),
        deadline.strip(), apply_link.strip(), status
    ))


def update_internship(internship_id: int, title: str, company_name: str, description: str,
                      required_skills: str, min_cgpa: float, eligible_departments: str,
                      required_qualifications: str, duration: str, work_mode: str,
                      location: str, stipend: str, deadline: str, apply_link: str, status: str):
    """Update internship details."""
    return execute_db("""
        UPDATE internships SET
            title = ?, company_name = ?, description = ?, required_skills = ?,
            min_cgpa = ?, eligible_departments = ?, required_qualifications = ?,
            duration = ?, work_mode = ?, location = ?, stipend = ?,
            deadline = ?, apply_link = ?, status = ?
        WHERE id = ?
    """, (
        title.strip(), company_name.strip(), description.strip(), required_skills.strip(),
        float(min_cgpa), eligible_departments.strip(), required_qualifications.strip(),
        duration.strip(), work_mode.strip(), location.strip(), stipend.strip(),
        deadline.strip(), apply_link.strip(), status, internship_id
    ))


def delete_internship(internship_id: int):
    """Delete an internship and associated applications."""
    return execute_db("DELETE FROM internships WHERE id = ?", (internship_id,))


# ------------------ APPLICATION HELPERS ------------------ #

def get_student_applications(student_id: int):
    """Retrieve all applications submitted by a student with internship details."""
    return query_db("""
        SELECT a.*, i.internship_code, i.title as internship_title, i.company_name, 
               i.location, i.stipend, i.work_mode, i.deadline, i.required_skills
        FROM applications a
        JOIN internships i ON a.internship_id = i.id
        WHERE a.student_id = ?
        ORDER BY a.applied_at DESC
    """, (student_id,))


def get_all_applications():
    """Retrieve all applications with student and internship details."""
    return query_db("""
        SELECT a.*, 
               s.name as student_name, s.student_id as student_code, s.department as student_dept, s.cgpa as student_cgpa,
               i.internship_code, i.title as internship_title, i.company_name
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN internships i ON a.internship_id = i.id
        ORDER BY a.applied_at DESC
    """)


def apply_for_internship(student_id: int, internship_id: int, match_percentage: float,
                         is_eligible: bool, common_skills: str, missing_skills: str):
    """Submit an application if not already applied."""
    existing = query_db(
        "SELECT id FROM applications WHERE student_id = ? AND internship_id = ?",
        (student_id, internship_id), one=True
    )
    if existing:
        return False, "You have already applied for this internship."
    
    execute_db("""
        INSERT INTO applications (
            student_id, internship_id, match_percentage, is_eligible,
            common_skills, missing_skills, status
        ) VALUES (?, ?, ?, ?, ?, ?, 'Applied')
    """, (student_id, internship_id, match_percentage, 1 if is_eligible else 0, common_skills, missing_skills))
    return True, "Application submitted successfully!"


def update_application_status(app_id: int, status: str):
    """Update status of an application (e.g. Applied, Under Review, Shortlisted, Accepted, Rejected)."""
    return execute_db("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))


# ------------------ ADMIN HELPERS ------------------ #

def get_admin_by_username(username: str):
    """Retrieve admin by username."""
    return query_db("SELECT * FROM admin_users WHERE username = ?", (username.strip(),), one=True)

