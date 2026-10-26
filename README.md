# Student Skill and Internship Matching System Using Sets and Relations

A complete, beginner-friendly web application designed to demonstrate the real-world application of **Discrete Mathematics (Sets, Set Operations, Relations, Cartesian Products, and Functions)** in solving the student-internship placement problem.

Developed with **Python (Flask)**, **SQLite**, **HTML5/Bootstrap 5**, **Chart.js**, and custom mathematical visualization engines.

---

## 🎯 1. Project Overview & Objectives

In standard recruitment platforms, matching algorithms often operate as opaque black boxes. This system models the candidate-internship matching problem using **formal Discrete Mathematics**, making every recommendation transparent, explainable, and verifiable.

### Core Objectives:
1. **Register Students & Maintain Academic Profiles:** Manage student IDs, disciplines, CGPA, qualifications, coursework, and personal skill sets ($S$).
2. **Internship Management:** Allow administrators to define internship opportunities with required skill sets ($R$), minimum CGPA, and eligible departments.
3. **Discrete Mathematical Matching:**
   - **Intersection ($S \cap R$):** Identify exact common skills.
   - **Set Difference ($R - S$):** Detect missing skill gaps.
   - **Relative Complement ($S - R$):** Highlight supplementary skills.
   - **Union ($S \cup R$):** Compute total skill universe.
   - **Matching Metric:** $\text{Skill Match } \% = \frac{|S \cap R|}{|R|} \times 100$.
4. **Separation of Academic Eligibility & Skill Similarity:** High skill overlap **never** overrides mandatory criteria (CGPA, department, degree constraints).
5. **Cartesian Product ($A \times B$) & Relations:** Model student-internship pairings as formal relations $R \subseteq A \times B$, construct binary relation matrices $M$, and test for function properties (domain, range, injectivity, surjectivity).
6. **Interactive Math Lab:** Dynamic SVG/CSS Venn diagrams and real-time set calculators for classroom teaching and viva demonstrations.

---

## 📐 2. Discrete Mathematics Mathematical Formulation

### A. Sets
- Let $A = \{s_1, s_2, \dots, s_m\}$ be the set of registered students.
- Let $B = \{i_1, i_2, \dots, i_n\}$ be the set of active internships.
- For each student $s \in A$, define their skill set:
  $$S = \{x : x \text{ is a skill possessed by student } s\}$$
- For each internship $i \in B$, define the required skill set:
  $$R = \{y : y \text{ is a skill required by internship } i\}$$

### B. Set Operations on Skills
1. **Common Skills (Intersection):**
   $$S \cap R = \{x : x \in S \land x \in R\}$$
2. **Missing Skills Gap (Set Difference):**
   $$R \setminus S = R - S = \{x : x \in R \land x \notin S\}$$
3. **Additional Skills (Relative Difference):**
   $$S \setminus R = S - R = \{x : x \in S \land x \notin R\}$$
4. **Skill Matching Percentage:**
   $$\text{Match Percentage} = \begin{cases} 
   \frac{|S \cap R|}{|R|} \times 100, & \text{if } |R| > 0 \\ 
   100\%, & \text{if } |R| = 0 \text{ (vacuously satisfied)} 
   \end{cases}$$
5. **Jaccard Similarity Coefficient:**
   $$J(S, R) = \frac{|S \cap R|}{|S \cup R|}$$

### C. Benchmark Classroom Example
Given:
- Student Skills: $S = \{\text{Python, SQL, HTML, Java}\}$ ($|S| = 4$)
- Required Skills: $R = \{\text{Python, SQL, Excel}\}$ ($|R| = 3$)

Calculations:
- **Common Skills ($S \cap R$):** $\{\text{Python, SQL}\}$ ($|S \cap R| = 2$)
- **Missing Skills ($R - S$):** $\{\text{Excel}\}$ ($|R - S| = 1$)
- **Additional Skills ($S - R$):** $\{\text{HTML, Java}\}$ ($|S - R| = 2$)
- **Skill Match Percentage:** $\frac{2}{3} \times 100 = \mathbf{66.67\%}$

### D. Cartesian Product & Relations
1. **Cartesian Product ($A \times B$):**
   $$A \times B = \{(s, i) : s \in A \land i \in B\}, \quad |A \times B| = |A| \times |B|$$
2. **Skill Relation ($R_{skill} \subseteq A \times B$):**
   $$(s, i) \in R_{skill} \iff \text{SkillMatch}(s, i) \ge \theta \quad (\text{default } \theta = 50\%)$$
3. **Academic Eligibility Relation ($R_{eligible} \subseteq A \times B$):**
   $$(s, i) \in R_{eligible} \iff (\text{CGPA}(s) \ge \text{MinCGPA}(i)) \land (\text{Dept}(s) \in \text{Depts}(i))$$
4. **Recommended Match Relation ($R_{match} \subseteq A \times B$):**
   $$R_{match} = R_{skill} \cap R_{eligible}$$
5. **Binary Relation Matrix ($M_{|A| \times |B|}$):**
   $$M[s][i] = \begin{cases} 1, & \text{if } (s, i) \in R_{match} \\ 0, & \text{otherwise} \end{cases}$$
6. **Domain & Range:**
   $$\text{Dom}(R_{match}) = \{s \in A : \exists i \in B, (s, i) \in R_{match}\}$$
   $$\text{Ran}(R_{match}) = \{i \in B : \exists s \in A, (s, i) \in R_{match}\}$$

---

## 💻 3. Technology Stack

- **Backend:** Python 3.10+ with Flask (lightweight, modular architecture)
- **Database:** SQLite (built-in relational DBMS, zero external setup)
- **Frontend:** HTML5, CSS3 (Modern responsive theme with custom color tokens), Bootstrap 5.3.3, FontAwesome 6.5
- **Visualizations:** Chart.js 4.4 (interactive analytics charts) & Dynamic SVG/CSS Venn Diagram
- **Deployment:** Ready for Render, Heroku, or PythonAnywhere (`Procfile`, `requirements.txt`)

---

## 🚀 4. How to Run Locally

### Prerequisites
- Python 3.10 or later installed on your system.
- `pip` package manager.

### Step 1: Clone or Navigate to the Workspace
```bash
cd "Student Skill and Intrenship Matching System"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Access in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 5. Pre-Seeded Accounts & Demo Access

The database comes pre-seeded with realistic students across diverse disciplines and sample internships.

### Evaluator 1-Click Access
The home page and login pages feature **1-Click Quick Demo Login buttons** for examiners:
- **Student 1 (Computer Science):** `rahul.sharma@college.edu` / `student123` (ID: `STU101`, CGPA: 8.75)
- **Student 2 (Biotechnology):** `priya.nair@college.edu` / `student123` (ID: `STU103`, CGPA: 9.15)
- **Student 3 (Bioinformatics):** `rohan.verma@college.edu` / `student123` (ID: `STU104`, CGPA: 8.45)
- **Placement Administrator:** `admin` / `admin123`

---

## 📁 6. System Architecture & File Directory

```
Student Skill and Intrenship Matching System/
├── app.py                  # Main Flask controller with routing, authentication, and API endpoints
├── database.py             # SQLite database layer, schema migration, and pre-seeded sample data
├── matching_engine.py      # Discrete mathematics engine: sets, relations, Cartesian product, matrix
├── matching_system.db      # SQLite relational database storage
├── requirements.txt        # Python package dependencies
├── Procfile                # Cloud deployment configuration for gunicorn
├── static/
│   ├── css/
│   │   └── style.css       # Modern CSS design system (tokens, cards, Venn diagram, matrix)
│   └── js/
│       └── main.js         # Client-side dynamic Venn updater, set calculator AJAX, tooltips
├── templates/
│   ├── base.html           # Master layout with responsive navbar, flash alerts, and footer
│   ├── index.html          # Module 1: Landing page with metrics & classroom test showcase
│   ├── login.html          # Unified student & 1-click quick login
│   ├── register.html       # Module 2: Student registration with interactive skill pills
│   ├── internships.html    # Module 1/Catalog: Search, filter & live match score cards
│   ├── internship_detail.html # Deep-dive internship specs & set theory breakdown
│   ├── math_lab.html       # Module 5: Interactive Discrete Math Lab & Venn Diagram visualizer
│   ├── student_dashboard.html # Student portal with skill gap advisory & match progress
│   ├── student_profile.html   # Student profile editor
│   ├── student_applications.html # Candidate application tracker
│   ├── admin_login.html       # Placement cell admin login
│   ├── admin_dashboard.html   # Admin control panel with Chart.js analytics
│   ├── admin_internships.html # Module 3: Manage internships
│   ├── admin_internship_form.html # Module 3: Create & edit internship forms
│   ├── admin_students.html    # Registered students roster (Set A)
│   ├── admin_applications.html # Candidate application review pipeline
│   └── admin_relation_matrix.html # Module 5: Relation matrix & mapping analysis
└── README.md               # Project documentation
```

---

## 🌐 7. Cloud Deployment (Render / Heroku)

This application is ready for zero-config deployment on Render or Heroku:
1. **Render:**
   - Create a new **Web Service** pointing to your GitHub repository.
   - Set **Build Command:** `pip install -r requirements.txt`
   - Set **Start Command:** `gunicorn app:app`
2. **Procfile:**
   Contains:
   ```
   web: gunicorn app:app
   ```
