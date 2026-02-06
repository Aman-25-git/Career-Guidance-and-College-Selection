import streamlit as st
import sqlite3

# -------------------------------
# DATABASE SETUP
# -------------------------------
conn = sqlite3.connect("career_guidance.db", check_same_thread=False)
cursor = conn.cursor()

# Careers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS careers (
    career TEXT,
    interest TEXT,
    skill TEXT,
    min_score INTEGER,
    colleges TEXT,
    admission TEXT,
    jobs TEXT
)
""")

# Insert career data once
cursor.execute("SELECT COUNT(*) FROM careers")
if cursor.fetchone()[0] == 0:
    careers_data = [
        ("Software Engineer", "Technology", "Programming", 70,
         "IITs, NITs, IIITs, Top Private Universities",
         "PCM background, JEE / State Entrance Exams",
         "Software Developer, AI Engineer, Cloud Engineer"),

        ("Doctor", "Healthcare", "Analysis", 85,
         "AIIMS, Government Medical Colleges",
         "PCB background, NEET Exam",
         "Hospitals, Research, Private Practice"),

        ("MBA / Entrepreneur", "Business", "Management", 65,
         "IIMs, XLRI, Top Business Schools",
         "Any degree, CAT / XAT / MAT",
         "Manager, Startup Founder, Consultant"),

        ("Designer / Animator", "Arts", "Design", 60,
         "NIFT, NID, Fine Arts Colleges",
         "Portfolio + Entrance Test",
         "UI/UX Designer, Animator, Creative Director")
    ]
    cursor.executemany("INSERT INTO careers VALUES (?,?,?,?,?,?,?)", careers_data)
    conn.commit()

# -------------------------------
# USER HISTORY TABLE (NEW)
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    interest TEXT,
    skill TEXT,
    score INTEGER,
    recommended_career TEXT,
    match_score INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# -------------------------------
# AI MATCH ENGINE
# -------------------------------
def ai_recommend_with_score(interest, skill, score):
    cursor.execute("SELECT * FROM careers")
    careers = cursor.fetchall()

    best_match = None
    best_score = 0

    for c in careers:
        match = 0

        if interest == c[1]:
            match += 40
        if skill == c[2]:
            match += 40
        if score >= c[3]:
            match += 20
        else:
            match += int((score / c[3]) * 20)

        if match > best_score:
            best_score = match
            best_match = c

    return best_match, best_score

def generate_explanation(interest, skill, score, career, match_score):
    return f"""
Based on your interest in **{interest}** and your strength in **{skill}**, 
the career path of **{career}** aligns strongly with your profile.

Your academic score of **{score}%** contributes to a 
**{match_score}% compatibility score**, indicating strong career suitability.
"""

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(
    page_title="AI Career Guidance Tool",
    page_icon="🎓",
    layout="centered"
)

st.markdown(
    "<h1 style='text-align:center;color:#34d399'>🎓 AI Career Guidance & College Selection Tool</h1>",
    unsafe_allow_html=True
)

st.write("### Enter Student Details")

name = st.text_input("👤 Student Name")

interest = st.selectbox(
    "🎯 Area of Interest",
    ["Technology", "Healthcare", "Business", "Arts"]
)

skill = st.selectbox(
    "🛠 Primary Skill",
    ["Programming", "Analysis", "Management", "Design"]
)

score = st.number_input(
    "📊 Academic Score (%)",
    min_value=0,
    max_value=100,
    step=1
)

# -------------------------------
# SUBMIT
# -------------------------------
if st.button("🚀 Get AI Recommendation"):
    if name.strip() == "":
        st.warning("Please enter student name.")
    else:
        data, match_score = ai_recommend_with_score(interest, skill, score)

        if not data:
            st.error("No suitable career found.")
        else:
            explanation = generate_explanation(
                interest, skill, score, data[0], match_score
            )

            # -------------------------------
            # SAVE USER DATA (IMPORTANT)
            # -------------------------------
            cursor.execute("""
            INSERT INTO user_history
            (name, interest, skill, score, recommended_career, match_score)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                interest,
                skill,
                score,
                data[0],
                match_score
            ))
            conn.commit()

            # -------------------------------
            # RESULT CARD
            # -------------------------------
            st.markdown("---")
            st.markdown(
                f"""
                <div style="
                    background-color:#111827;
                    padding:22px;
                    border-radius:16px;
                    color:white;
                ">
                    <h2 style="color:#34d399">🎯 Personalized Career Recommendation</h2>
                    <p><b>👤 Student:</b> {name}</p>
                    <p><b>💼 Recommended Career:</b> {data[0]}</p>
                    <p><b>📈 Match Score:</b> {match_score}%</p>
                    <p><b>🏫 Colleges:</b> {data[4]}</p>
                    <p><b>📋 Admission:</b> {data[5]}</p>
                    <p><b>🚀 Job Prospects:</b> {data[6]}</p>
                    <hr>
                    <p><b>🧠 AI Explanation:</b><br>{explanation}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")
st.caption("Next-Gen AI Hackathon | SCCE WINNERS 🏆")
