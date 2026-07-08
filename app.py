# =============================================================================
#  LearnMate – Flask Application
#  Entry point: all routes, session management, and API endpoints.
# =============================================================================

import os
import json
from flask import (
    Flask,
    render_template,
    request,
    session,
    jsonify,
    redirect,
    url_for,
    flash,
)
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from agent import get_agent  # noqa: E402  (must come after load_dotenv)

# ─────────────────────────────────────────────────────────────────────────────
#  App initialization
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "learnmate-dev-secret-2024")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ─────────────────────────────────────────────────────────────────────────────
#  Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def get_profile() -> dict:
    """Retrieve the student profile stored in the Flask session."""
    return session.get("profile", {})


def profile_complete() -> bool:
    """Check that mandatory profile fields are filled in."""
    p = get_profile()
    required = ["name", "career_goal", "skill_level", "technologies"]
    return all(p.get(f) for f in required)


# ─────────────────────────────────────────────────────────────────────────────
#  Routes – Public pages
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Landing page."""
    return render_template("home.html", profile=get_profile())


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Student profile form – collect learning context."""
    if request.method == "POST":
        # Build profile dict from form data
        session["profile"] = {
            "name": request.form.get("name", "").strip(),
            "education": request.form.get("education", ""),
            "college": request.form.get("college", "").strip(),
            "branch": request.form.get("branch", "").strip(),
            "skill_level": request.form.get("skill_level", "Beginner"),
            "career_goal": request.form.get("career_goal", "").strip(),
            "technologies": request.form.get("technologies", "").strip(),
            "study_hours": request.form.get("study_hours", "2"),
            "learning_style": request.form.get("learning_style", "Mixed"),
        }
        # Reset chat history when profile changes
        session.pop("chat_history", None)
        flash("Profile saved successfully! Let's build your learning path. 🚀", "success")
        return redirect(url_for("dashboard"))

    return render_template("profile.html", profile=get_profile())


# ─────────────────────────────────────────────────────────────────────────────
#  Routes – AI-powered feature pages (require profile)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/chat")
def chat():
    """AI Chat Assistant page."""
    if not profile_complete():
        flash("Please complete your profile first so LearnMate can personalize your experience.", "warning")
        return redirect(url_for("profile"))
    history = session.get("chat_history", [])
    return render_template("chat.html", profile=get_profile(), history=history)


@app.route("/roadmap")
def roadmap():
    """Personalized Learning Roadmap page."""
    if not profile_complete():
        flash("Please complete your profile to generate your roadmap.", "warning")
        return redirect(url_for("profile"))
    return render_template("roadmap.html", profile=get_profile())


@app.route("/skill-gap")
def skill_gap():
    """Skill Gap Analysis page."""
    if not profile_complete():
        flash("Complete your profile to see your skill gap analysis.", "warning")
        return redirect(url_for("profile"))
    return render_template("skill_gap.html", profile=get_profile())


@app.route("/courses")
def courses():
    """Course Recommendations page."""
    if not profile_complete():
        flash("Complete your profile to get course recommendations.", "warning")
        return redirect(url_for("profile"))
    return render_template("courses.html", profile=get_profile())


@app.route("/weekly-plan")
def weekly_plan():
    """Weekly Study Planner page."""
    if not profile_complete():
        flash("Complete your profile to generate your study plan.", "warning")
        return redirect(url_for("profile"))
    return render_template("weekly_plan.html", profile=get_profile())


@app.route("/projects")
def projects():
    """Project Recommendations page."""
    if not profile_complete():
        flash("Complete your profile to get project suggestions.", "warning")
        return redirect(url_for("profile"))
    return render_template("projects.html", profile=get_profile())


@app.route("/career")
def career():
    """Career Guidance page."""
    if not profile_complete():
        flash("Complete your profile to get career guidance.", "warning")
        return redirect(url_for("profile"))
    return render_template("career.html", profile=get_profile())


@app.route("/dashboard")
def dashboard():
    """Progress Dashboard page."""
    if not profile_complete():
        flash("Complete your profile to view your dashboard.", "warning")
        return redirect(url_for("profile"))
    return render_template("dashboard.html", profile=get_profile())


# ─────────────────────────────────────────────────────────────────────────────
#  API Endpoints – AJAX calls from the frontend
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Handle a single chat message, persist history in session."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    profile = get_profile()
    try:
        agent = get_agent()
        reply = agent.chat(user_message, profile)
    except Exception as exc:
        app.logger.error("Chat error: %s", exc)
        return jsonify({"error": "AI service unavailable. Check your API credentials."}), 503

    # Persist conversation in session (keep last 20 turns)
    history = session.get("chat_history", [])
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    session["chat_history"] = history[-40:]  # 20 turns × 2

    return jsonify({"reply": reply})


@app.route("/api/generate/<section>", methods=["POST"])
def api_generate(section: str):
    """
    Generic AI generation endpoint.
    section: roadmap | skill_gap | courses | weekly_plan | projects | career
    """
    profile = get_profile()
    if not profile:
        return jsonify({"error": "Profile not found."}), 400

    try:
        agent = get_agent()
        generators = {
            "roadmap": agent.generate_roadmap,
            "skill_gap": agent.generate_skill_gap,
            "courses": agent.generate_course_recommendations,
            "weekly_plan": agent.generate_weekly_plan,
            "projects": agent.generate_projects,
            "career": agent.generate_career_guidance,
        }
        generator_fn = generators.get(section)
        if not generator_fn:
            return jsonify({"error": f"Unknown section: {section}"}), 400

        content = generator_fn(profile)
        # Cache the result in the session to avoid re-generating on page refresh
        session.setdefault("generated", {})[section] = content
        session.modified = True
        return jsonify({"content": content})

    except Exception as exc:
        app.logger.error("Generation error for '%s': %s", section, exc)
        return jsonify({"error": "AI service unavailable. Check your API credentials."}), 503


@app.route("/api/profile/clear", methods=["POST"])
def api_clear_profile():
    """Clear session data (reset for a new student)."""
    session.clear()
    return jsonify({"status": "cleared"})


# ─────────────────────────────────────────────────────────────────────────────
#  Error handlers
# ─────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
