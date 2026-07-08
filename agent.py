# =============================================================================
#  LearnMate – AI Agent Core
#  Handles IBM watsonx.ai (Granite) integration and all prompt engineering.
#
#  AGENT_INSTRUCTIONS – customize personality, tone, and behavior here.
# =============================================================================

import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters

# ─────────────────────────────────────────────────────────────────────────────
#  Model configuration
#  Uses /ml/v1/text/chat (non-deprecated API) via model.chat(messages=[...])
# ─────────────────────────────────────────────────────────────────────────────

AGENT_NAME = "LearnMate"

MODEL_ID = "meta-llama/llama-3-3-70b-instruct"

CHAT_PARAMS = TextChatParameters(
    max_tokens=3000,
    temperature=0.3,        # focused, consistent output
    top_p=0.9,
    repetition_penalty=1.15,
)

# ─────────────────────────────────────────────────────────────────────────────
#  System prompt
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are LearnMate, an expert AI learning coach and career advisor for students in technology fields.

Your rules:
1. Always respond with well-structured, actionable content using Markdown headings and bullet points.
2. Be specific — name exact topics, tools, frameworks, and platforms. Never give vague advice.
3. Match depth to the student's skill level: simple analogies for beginners, best practices for intermediate, architecture and leadership for advanced.
4. Connect every recommendation to a concrete career or job outcome.
5. Never fabricate URLs. Reference platforms by name only (e.g., freeCodeCamp, Coursera, LeetCode, YouTube).
6. End every response with one short, genuine motivational sentence relevant to the student's goal.
7. Do not repeat the student profile back verbatim. Use it silently to personalise your answer."""


# ─────────────────────────────────────────────────────────────────────────────
#  WatsonxAgent – singleton wrapper
# ─────────────────────────────────────────────────────────────────────────────

class WatsonxAgent:
    """Wrapper around IBM watsonx.ai ModelInference using the chat API."""

    def __init__(self):
        api_key = os.getenv("IBM_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        url = os.getenv("WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")

        if not api_key or not project_id:
            raise EnvironmentError(
                "IBM_API_KEY and WATSONX_PROJECT_ID must be set in .env"
            )

        credentials = Credentials(url=url, api_key=api_key)
        self.model = ModelInference(
            model_id=MODEL_ID,
            credentials=credentials,
            project_id=project_id,
        )

    def _profile_context(self, profile: dict) -> str:
        """Build a compact inline profile string from non-empty fields."""
        fields = {
            "Name": profile.get("name"),
            "Education": profile.get("education"),
            "Branch": profile.get("branch"),
            "Skill Level": profile.get("skill_level"),
            "Career Goal": profile.get("career_goal"),
            "Technologies": profile.get("technologies"),
            "Study Hours": f"{profile.get('study_hours')} hrs/day" if profile.get("study_hours") else None,
            "Learning Style": profile.get("learning_style"),
        }
        parts = [f"{k}: {v}" for k, v in fields.items() if v and v != "N/A"]
        return ("Student context — " + " | ".join(parts) + "\n\n") if parts else ""

    def chat(self, user_message: str, profile: dict | None = None) -> str:
        """Send a message via the /ml/v1/text/chat API and return the reply."""
        profile_line = self._profile_context(profile) if profile else ""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": profile_line + user_message},
        ]
        response = self.model.chat(messages=messages, params=CHAT_PARAMS)
        try:
            text = response["choices"][0]["message"]["content"]
            return text.strip() if text else "I'm sorry, I couldn't generate a response. Please try again."
        except (KeyError, IndexError):
            return "I'm sorry, I couldn't generate a response. Please try again."

    # ── Specialized generation methods ──────────────────────────────────────

    def generate_roadmap(self, profile: dict) -> str:
        """Generate a full personalized learning roadmap."""
        goal  = profile.get("career_goal", "a tech career")
        level = profile.get("skill_level", "Beginner")
        tech  = profile.get("technologies", "general programming")
        hours = profile.get("study_hours", "1-2")
        style = profile.get("learning_style", "Mixed")

        prompt_text = f"""Create a complete, personalised learning roadmap for someone who wants to become a {goal}.

Current level: {level}
Technologies of interest: {tech}
Available study time: {hours} hours/day
Learning style: {style}

Structure the roadmap exactly as follows:

## Phase 1 – Foundation (Weeks 1–N)
- List 6 specific topics with a one-line explanation of each
- Mini-project: [name one concrete beginner project]
- Milestone: [what the student can do/build after this phase]

## Phase 2 – Core Skills (Weeks N–N)
- List 7 specific topics with a one-line explanation of each
- Mini-project: [name one intermediate project]
- Milestone: [what the student can do/build after this phase]

## Phase 3 – Advanced & Job Ready (Weeks N–N)
- List 6 specific topics with a one-line explanation of each
- Capstone project: [name one portfolio-worthy project]
- Milestone: [what the student is ready for at this point]

## Timeline Summary
State the total estimated weeks to reach job-ready status given {hours} hrs/day.

Be specific with technology names, tools, and frameworks relevant to {goal}."""
        return self.chat(prompt_text, profile)

    def generate_skill_gap(self, profile: dict) -> str:
        """Perform a skill gap analysis."""
        goal  = profile.get("career_goal", "a tech career")
        level = profile.get("skill_level", "Beginner")
        tech  = profile.get("technologies", "general programming")

        prompt_text = f"""Perform a detailed skill gap analysis for someone targeting: {goal}
Current skill level: {level} | Technologies they know: {tech}

Respond with exactly these four sections:

## Current Strengths
List 5 specific skills/knowledge areas this person likely already has. Be realistic for their level.

## Critical Skill Gaps
List 8 specific skills they are missing to succeed as a {goal}. For each gap, state in one sentence why it is essential.

## Top 5 Priority Skills to Learn Next
Rank by highest impact. For each: state the skill, why it matters most now, and the best way to learn it.

## Senior-Level Skills (Long-Term)
List 5 skills needed to grow from junior to senior in this field. Briefly explain each.

Be specific — name exact technologies, tools, concepts, and frameworks."""
        return self.chat(prompt_text, profile)

    def generate_course_recommendations(self, profile: dict) -> str:
        """Generate ordered course/topic recommendations."""
        goal  = profile.get("career_goal", "a tech career")
        level = profile.get("skill_level", "Beginner")
        tech  = profile.get("technologies", "general programming")
        style = profile.get("learning_style", "Mixed")

        prompt_text = f"""Recommend a structured learning curriculum for someone who wants to become a {goal}.
Current level: {level} | Interested in: {tech} | Learns best via: {style}

Organise into exactly these four sections:

## 1. Prerequisites (Must Learn First)
List 4 foundational topics. For each: topic name, why it is needed, best resource type for a {style} learner, estimated hours.

## 2. Core Curriculum
List 8 essential topics for a {goal}. For each: topic name, why it matters for this career, best resource type, estimated hours.

## 3. Specialisation Topics
List 4 advanced topics that differentiate a candidate. For each: topic name, career advantage it provides, best resource type, estimated hours.

## 4. Bonus Skills
List 3 nice-to-have skills that accelerate hiring or growth.

Name specific platforms (Coursera, freeCodeCamp, The Odin Project, LeetCode, YouTube, official docs) for each entry."""
        return self.chat(prompt_text, profile)

    def generate_weekly_plan(self, profile: dict) -> str:
        """Generate a personalized weekly study plan."""
        goal  = profile.get("career_goal", "a tech career")
        level = profile.get("skill_level", "Beginner")
        hours = profile.get("study_hours", "2")
        tech  = profile.get("technologies", "general programming")

        prompt_text = f"""Create a realistic 7-day study plan for a {level}-level student working toward {goal}.
Available study time: {hours} hours/day | Focus technologies: {tech}

Format as a day-by-day schedule:

## Weekly Study Plan

**Monday** – [Topic] ({hours}h)
- Task 1 (Xmin): specific activity
- Task 2 (Xmin): specific activity

Repeat this exact format for Tuesday through Sunday.

Rules:
- Assign specific topics and tasks — not generic "study X".
- Include one dedicated revision/review session during the week.
- Include one hands-on coding/project session.
- Make Sunday a light review + planning day (max 1 hour).
- Time allocations must add up to {hours} hours per day.

End with a "Weekly Goal" line stating what the student will have learned or built by Sunday."""
        return self.chat(prompt_text, profile)

    def generate_projects(self, profile: dict) -> str:
        """Suggest hands-on projects across skill levels."""
        goal  = profile.get("career_goal", "a tech career")
        level = profile.get("skill_level", "Beginner")
        tech  = profile.get("technologies", "general programming")

        prompt_text = f"""Suggest 7 hands-on project ideas for a {level}-level student targeting {goal}.
Technologies to use: {tech}

Organise into three tiers:

## Beginner Projects (3 projects)
For each project:
- **Project Name**: descriptive title
- **Description**: 2 sentences explaining what it does and what problem it solves
- **Skills Developed**: list 3–4 specific skills
- **Time to Complete**: realistic estimate
- **Tech Stack**: exact technologies to use

## Intermediate Projects (3 projects)
Same format as above. Projects must combine multiple skills and be portfolio-worthy.

## Advanced Project (1 project)
Same format. This project must demonstrate job-readiness and could be shown in an interview.

Make every project realistic and directly relevant to the {goal} career path."""
        return self.chat(prompt_text, profile)

    def generate_career_guidance(self, profile: dict) -> str:
        """Provide career path guidance and interview prep."""
        goal  = profile.get("career_goal", "a tech career")
        level = profile.get("skill_level", "Beginner")
        tech  = profile.get("technologies", "general programming")
        edu   = profile.get("education", "N/A")

        prompt_text = f"""Provide actionable career guidance for someone targeting: {goal}
Current level: {level} | Education: {edu} | Technologies: {tech}

Cover all five sections below:

## Target Job Roles
Describe 3 specific job titles this person can realistically target. For each: title, typical responsibilities (4 bullet points), average salary range, and minimum skills required.

## Interview Preparation
List 10 technical topics most commonly tested in interviews for {goal} roles. Then list 5 key behavioural questions with a tip for answering each.

## Certifications to Pursue
Recommend 4 certifications. For each: name, issuing body, cost (free/paid), time to complete, and career impact.

## Networking & Visibility
List 6 specific actions to build professional presence: communities to join, platforms to use, content to create.

## 12-Month Action Plan
Write a month-by-month plan (Month 1 through Month 12) from current state to submitting the first job application. Each month: one main learning goal and one career-building action."""
        return self.chat(prompt_text, profile)


# ─────────────────────────────────────────────────────────────────────────────
#  Module-level singleton (lazy-initialized)
# ─────────────────────────────────────────────────────────────────────────────
_agent_instance: WatsonxAgent | None = None


def get_agent() -> WatsonxAgent:
    """Return the shared WatsonxAgent instance (created on first call)."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = WatsonxAgent()
    return _agent_instance
