"""
Discrete Mathematics Matching Engine
====================================
Demonstrates the practical application of:
- Sets and Set Operations (Union, Intersection, Set Difference, Symmetric Difference, Jaccard Similarity)
- Relations (Subsets of Cartesian Product A × B)
- Cartesian Product (A × B)
- Domain, Codomain, and Range of Relations
- Functions and Relational Matrix representations
"""

from typing import Dict, List, Set, Any, Tuple
import math


def normalize_skill(skill: str) -> str:
    """Normalize skill string (trimmed, formatted consistently)."""
    s = skill.strip()
    # Normalize common abbreviations or cases nicely
    acronyms = {"html": "HTML", "css": "CSS", "sql": "SQL", "pcr": "PCR", "blast": "BLAST", "r": "R", "ai": "AI", "ml": "ML"}
    lowered = s.lower()
    if lowered in acronyms:
        return acronyms[lowered]
    return s.title() if len(s) > 1 else s.upper()


def parse_to_set(data: Any) -> Set[str]:
    """
    Convert a comma-separated string, list, or set into a clean normalized Python Set.
    Safe handling for empty or null inputs.
    """
    if not data:
        return set()
    if isinstance(data, set):
        return {normalize_skill(x) for x in data if str(x).strip()}
    if isinstance(data, list):
        return {normalize_skill(x) for x in data if str(x).strip()}
    if isinstance(data, str):
        # Handle comma or semicolon separated
        items = [x.strip() for x in data.replace(";", ",").split(",")]
        return {normalize_skill(x) for x in items if x}
    return set()


def set_operations(student_skills: Set[str], required_skills: Set[str]) -> Dict[str, Any]:
    """
    Perform core Discrete Mathematics Set Operations:
    Let S = Student Skills Set
    Let R = Internship Required Skills Set

    Operations:
    1. Intersection (Common Skills): S ∩ R = {x : x ∈ S and x ∈ R}
    2. Set Difference (Missing Skills): R − S = {x : x ∈ R and x ∉ S}
    3. Relative Difference (Additional Skills): S − R = {x : x ∈ S and x ∉ R}
    4. Union (Combined Skills): S ∪ R = {x : x ∈ S or x ∈ R}
    5. Symmetric Difference: S △ R = (S − R) ∪ (R − S)
    6. Skill Matching Percentage: (|S ∩ R| / |R|) × 100
    7. Jaccard Similarity Coefficient: |S ∩ R| / |S ∪ R|
    """
    S = set(student_skills)
    R = set(required_skills)

    # 1. Intersection: Common skills
    common_skills = S.intersection(R)

    # 2. Difference R - S: Missing skills required by employer that student lacks
    missing_skills = R.difference(S)

    # 3. Difference S - R: Additional skills student possesses beyond requirement
    additional_skills = S.difference(R)

    # 4. Union: All distinct skills in either student profile or internship
    combined_skills = S.union(R)

    # 5. Symmetric Difference: Skills in S or R, but not both
    symmetric_diff = S.symmetric_difference(R)

    # 6. Skill Matching Percentage calculation
    # Formula: |S ∩ R| / |R| * 100
    if len(R) == 0:
        # Edge case: If an internship requires zero skills, 100% skill match or 0%?
        # Mathematically, an empty requirement is vacuously satisfied (100.0%)
        match_percentage = 100.0
        match_explanation = "Internship requires no specific skills; vacuously satisfied (100%)."
    else:
        match_percentage = round((len(common_skills) / len(R)) * 100, 2)
        match_explanation = f"|S ∩ R| / |R| × 100 = {len(common_skills)}/{len(R)} × 100 = {match_percentage}%"

    # 7. Jaccard Similarity Coefficient (|S ∩ R| / |S ∪ R|)
    if len(combined_skills) == 0:
        jaccard_similarity = 1.0
    else:
        jaccard_similarity = round(len(common_skills) / len(combined_skills), 4)

    return {
        "student_skills": sorted(list(S)),
        "required_skills": sorted(list(R)),
        "common_skills": sorted(list(common_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "additional_skills": sorted(list(additional_skills)),
        "combined_skills": sorted(list(combined_skills)),
        "symmetric_difference": sorted(list(symmetric_diff)),
        "cardinalities": {
            "S": len(S),
            "R": len(R),
            "intersection": len(common_skills),
            "missing": len(missing_skills),
            "additional": len(additional_skills),
            "union": len(combined_skills),
            "symmetric_diff": len(symmetric_diff)
        },
        "match_percentage": match_percentage,
        "jaccard_similarity": jaccard_similarity,
        "match_explanation": match_explanation
    }


def evaluate_student_internship_match(student: Dict[str, Any], internship: Dict[str, Any]) -> Dict[str, Any]:
    """
    Match a student profile against an internship.
    CRITICAL RULE:
    Clearly distinguishes skill similarity from overall academic eligibility!
    A student is marked 'Eligible' ONLY if all mandatory academic criteria are met:
    - CGPA >= Min CGPA
    - Department in Eligible Departments
    - Degree/Qualification matches Required Qualifications (if specified)

    A 100% skill match DOES NOT override mandatory academic eligibility.
    """
    # 1. Parse skill sets
    s_skills = parse_to_set(student.get("skills", ""))
    r_skills = parse_to_set(internship.get("required_skills", ""))
    math_results = set_operations(s_skills, r_skills)

    # 2. Check Academic CGPA Requirement
    student_cgpa = float(student.get("cgpa", 0.0) or 0.0)
    min_cgpa = float(internship.get("min_cgpa", 0.0) or 0.0)
    cgpa_eligible = student_cgpa >= min_cgpa

    # 3. Check Department Eligibility via Set Membership
    # Let D = set of eligible departments for internship
    # Is student.department ∈ D?
    raw_dept_list = internship.get("eligible_departments", "")
    eligible_depts = {d.strip().lower() for d in raw_dept_list.split(",") if d.strip()}
    student_dept = str(student.get("department", "")).strip().lower()
    
    # If no department constraint specified or 'all' is listed, it's open to all
    if not eligible_depts or "all" in eligible_depts or "any" in eligible_depts:
        dept_eligible = True
    else:
        dept_eligible = student_dept in eligible_depts

    # 4. Check Degree / Qualification Eligibility
    raw_qual_list = internship.get("required_qualifications", "")
    eligible_quals = {q.strip().lower() for q in raw_qual_list.split(",") if q.strip()}
    student_qual = str(student.get("degree", student.get("qualification", ""))).strip().lower()
    
    if not eligible_quals or "all" in eligible_quals or "any" in eligible_quals:
        qual_eligible = True
    else:
        qual_eligible = (student_qual in eligible_quals) or any(q in student_qual for q in eligible_quals)

    # 5. Overall Eligibility: Conjunction (AND) of all mandatory conditions
    is_eligible = cgpa_eligible and dept_eligible and qual_eligible

    # 6. Detailed reason messages for transparency
    eligibility_details = []
    if cgpa_eligible:
        eligibility_details.append(f"✓ CGPA {student_cgpa:.2f} satisfies minimum requirement ({min_cgpa:.2f})")
    else:
        eligibility_details.append(f"✗ CGPA {student_cgpa:.2f} is below minimum requirement ({min_cgpa:.2f})")

    if dept_eligible:
        eligibility_details.append(f"✓ Department '{student.get('department', 'N/A')}' is accepted")
    else:
        eligibility_details.append(f"✗ Department '{student.get('department', 'N/A')}' is not in eligible set {{{', '.join(sorted(eligible_depts))}}}")

    if qual_eligible:
        eligibility_details.append("✓ Degree / Qualification criteria satisfied")
    else:
        eligibility_details.append(f"✗ Qualification '{student.get('degree', '')}' does not match required qualifications")

    # 7. Status Classification
    # Can be:
    # - 'EL_HIGH': Eligible with high skill match (>= 70%)
    # - 'EL_MED': Eligible with moderate skill match (40% - 69%)
    # - 'EL_LOW': Eligible with low skill match (< 40%)
    # - 'INELIGIBLE': Mandatory criteria not met (regardless of skill match)
    match_pct = math_results["match_percentage"]
    if is_eligible:
        if match_pct >= 70:
            badge_class = "success"
            status_text = "Strongly Recommended"
        elif match_pct >= 40:
            badge_class = "info"
            status_text = "Eligible - Moderate Match"
        else:
            badge_class = "warning"
            status_text = "Eligible - Skill Gap"
    else:
        badge_class = "danger"
        status_text = "Academically Ineligible"

    return {
        "student_id": student.get("id"),
        "student_name": student.get("name"),
        "student_code": student.get("student_id"),
        "internship_id": internship.get("id"),
        "internship_title": internship.get("title"),
        "company_name": internship.get("company_name"),
        "is_eligible": is_eligible,
        "cgpa_eligible": cgpa_eligible,
        "dept_eligible": dept_eligible,
        "qual_eligible": qual_eligible,
        "eligibility_details": eligibility_details,
        "status_text": status_text,
        "badge_class": badge_class,
        "set_math": math_results,
        "skill_match_percentage": match_pct,
        "common_skills": math_results["common_skills"],
        "missing_skills": math_results["missing_skills"],
        "additional_skills": math_results["additional_skills"],
    }


def compute_cartesian_product(students: List[Dict[str, Any]], internships: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes Cartesian Product A × B:
    Let A = Set of Students
    Let B = Set of Internships
    A × B = {(s, i) : s ∈ A and i ∈ B}
    Cardinality: |A × B| = |A| × |B|
    """
    pairs = []
    for s in students:
        for i in internships:
            pairs.append((s, i))

    return {
        "cardinality_A": len(students),
        "cardinality_B": len(internships),
        "total_pairs": len(pairs),
        "pairs": pairs,
        "formula": f"|A × B| = |A| × |B| = {len(students)} × {len(internships)} = {len(pairs)}"
    }


def compute_relations_and_mappings(
    students: List[Dict[str, Any]], 
    internships: List[Dict[str, Any]], 
    threshold: float = 50.0
) -> Dict[str, Any]:
    """
    Module 5: Discrete Math Relations, Matrix Representation, Domain & Range.
    
    Let:
    A = Set of Students
    B = Set of Internships
    Cartesian Product = A × B

    Relation R_skill ⊆ A × B:
    (s, i) ∈ R_skill ⟺ SkillMatchPercentage(s, i) ≥ threshold

    Relation R_eligible ⊆ A × B:
    (s, i) ∈ R_eligible ⟺ Student s satisfies all academic eligibility conditions for i

    Relation R_match ⊆ A × B (Recommended):
    R_match = R_skill ∩ R_eligible
    (s, i) ∈ R_match ⟺ (s, i) ∈ R_skill AND (s, i) ∈ R_eligible

    Also analyzes:
    - Domain: Dom(R) = {s ∈ A : ∃ i ∈ B, (s, i) ∈ R}
    - Codomain: B
    - Range: Ran(R) = {i ∈ B : ∃ s ∈ A, (s, i) ∈ R}
    - Matrix Representation: Binary matrix M of size |A| × |B| where M[s][i] = 1 if (s, i) ∈ R else 0
    - Function check: Does each student map to AT MOST ONE or EXACTLY ONE internship?
    """
    student_map = {s["id"]: s for s in students}
    internship_map = {i["id"]: i for i in internships}

    matrix = []
    r_skill_pairs = []
    r_eligible_pairs = []
    r_match_pairs = []
    detailed_pairs = []

    # Track domain and range for R_match
    dom_match = set()
    ran_match = set()

    for s in students:
        row = []
        for i in internships:
            eval_res = evaluate_student_internship_match(s, i)
            s_code = s.get("student_id", f"S{s['id']}")
            i_code = i.get("internship_code", f"I{i['id']}")
            pair_name = f"({s_code}, {i_code})"

            is_skill_ok = eval_res["skill_match_percentage"] >= threshold
            is_elig = eval_res["is_eligible"]
            is_match = is_skill_ok and is_elig

            if is_skill_ok:
                r_skill_pairs.append(pair_name)
            if is_elig:
                r_eligible_pairs.append(pair_name)
            if is_match:
                r_match_pairs.append(pair_name)
                dom_match.add(s_code)
                ran_match.add(i_code)

            matrix_val = 1 if is_match else 0
            row.append({
                "value": matrix_val,
                "is_match": is_match,
                "is_eligible": is_elig,
                "skill_match": eval_res["skill_match_percentage"],
                "student_name": s["name"],
                "internship_title": i["title"],
                "student_code": s_code,
                "internship_code": i_code,
                "common_skills": eval_res["common_skills"],
                "missing_skills": eval_res["missing_skills"]
            })

            detailed_pairs.append({
                "student": s,
                "internship": i,
                "evaluation": eval_res,
                "is_match": is_match
            })
        matrix.append(row)

    # Function verification on R_match
    # A relation R ⊆ A × B is a function if every element in A has at most one image in B (partial function)
    # or exactly one image (total function).
    student_outgoing_degrees = {}
    for s in students:
        s_code = s.get("student_id", f"S{s['id']}")
        count = sum(1 for p in r_match_pairs if p.startswith(f"({s_code},"))
        student_outgoing_degrees[s_code] = count

    is_function = all(count <= 1 for count in student_outgoing_degrees.values())
    is_total_function = all(count == 1 for count in student_outgoing_degrees.values())

    internship_incoming_degrees = {}
    for i in internships:
        i_code = i.get("internship_code", f"I{i['id']}")
        count = sum(1 for p in r_match_pairs if p.endswith(f", {i_code})"))
        internship_incoming_degrees[i_code] = count

    is_injective = is_function and all(count <= 1 for count in internship_incoming_degrees.values())
    is_surjective = (len(ran_match) == len(internships)) and is_function

    return {
        "threshold": threshold,
        "students": students,
        "internships": internships,
        "cardinality_A": len(students),
        "cardinality_B": len(internships),
        "cartesian_product_size": len(students) * len(internships),
        "r_skill_pairs": r_skill_pairs,
        "r_eligible_pairs": r_eligible_pairs,
        "r_match_pairs": r_match_pairs,
        "r_match_cardinality": len(r_match_pairs),
        "matrix": matrix,
        "domain": sorted(list(dom_match)),
        "codomain": [i.get("internship_code", f"I{i['id']}") for i in internships],
        "range": sorted(list(ran_match)),
        "is_function": is_function,
        "is_total_function": is_total_function,
        "is_injective": is_injective,
        "is_surjective": is_surjective,
        "detailed_pairs": detailed_pairs,
        "student_degrees": student_outgoing_degrees,
        "internship_degrees": internship_incoming_degrees
    }
