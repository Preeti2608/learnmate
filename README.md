# LearnMate – AI-Powered Personalized Course Pathway Agent

> **Your intelligent AI learning coach** — powered by IBM watsonx.ai and IBM Granite models.
> LearnMate understands your goals, evaluates your skills, and generates personalized learning roadmaps.

---

## ✨ Features

| Module | Description |
|---|---|
| 🏠 Home Page | Attractive landing with hero section and features overview |
| 👤 Student Profile | Capture education, skills, career goal, and learning preferences |
| 🤖 AI Chat Coach | Real-time conversational coach powered by IBM Granite 3.3 |
| 🗺️ Learning Roadmap | Beginner → Intermediate → Advanced phases with milestones |
| 📊 Skill Gap Analysis | Identify missing skills and priority learning areas |
| 📚 Course Recommendations | Curated learning topics in optimal order |
| 📅 Weekly Study Planner | Personalized daily schedule based on available hours |
| 💻 Project Recommendations | Hands-on project ideas across all skill levels |
| 💼 Career Guidance | Career paths, interview prep, certifications, action plan |
| 📈 Progress Dashboard | Unified view of your learning profile and all modules |

---

## 🏗️ Project Structure

```
learnmate/
├── app.py                    # Flask application – all routes & API endpoints
├── agent.py                  # IBM watsonx.ai agent + AGENT_INSTRUCTIONS
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── .env                      # Your credentials (DO NOT commit)
│
├── templates/
│   ├── base.html             # Base layout with navbar, footer, dark mode
│   ├── home.html             # Landing page
│   ├── profile.html          # Student profile form
│   ├── chat.html             # AI Chat Assistant
│   ├── roadmap.html          # Learning Roadmap
│   ├── skill_gap.html        # Skill Gap Analysis
│   ├── courses.html          # Course Recommendations
│   ├── weekly_plan.html      # Weekly Study Planner
│   ├── projects.html         # Project Recommendations
│   ├── career.html           # Career Guidance
│   ├── dashboard.html        # Progress Dashboard
│   ├── _ai_result_area.html  # Shared AI result component
│   ├── _nav_shortcuts.html   # Shared navigation shortcuts
│   ├── 404.html              # 404 error page
│   └── 500.html              # 500 error page
│
└── static/
    ├── css/
    │   └── style.css         # Complete design system (light + dark mode)
    └── js/
        ├── main.js           # Dark mode, animations, global utils
        ├── chat.js           # Chat assistant interactions
        └── generator.js      # AI content generation (shared)
```

---

## 🚀 Local Deployment – Step by Step

### Prerequisites

- Python 3.10 or higher
- An [IBM Cloud account](https://cloud.ibm.com/registration)
- An IBM watsonx.ai project

### 1. Clone / Download the project

```bash
# If using git:
git clone <your-repo-url>
cd learnmate

# Or just navigate to the project folder:
cd learnmate
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate (Windows):
venv\Scripts\activate

# Activate (macOS/Linux):
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and fill in your real credentials:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=your_random_secret_key
FLASK_ENV=development
```

#### How to get IBM credentials:

1. **IBM API Key**
   - Visit [IBM Cloud → Manage → Access (IAM) → API keys](https://cloud.ibm.com/iam/apikeys)
   - Click **Create an IBM Cloud API key**
   - Copy the key immediately (shown only once)

2. **watsonx.ai Project ID**
   - Go to [watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
   - Open your project → Click **Manage** tab
   - Copy the **Project ID** from the General section

3. **Service URL**
   - Use the URL for your IBM Cloud region:
     - US South: `https://us-south.ml.cloud.ibm.com`
     - EU Frankfurt: `https://eu-de.ml.cloud.ibm.com`
     - UK South: `https://eu-gb.ml.cloud.ibm.com`
     - Tokyo: `https://jp-tok.ml.cloud.ibm.com`

### 5. Run the application

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## 🌐 Production Deployment

### Using Gunicorn (recommended)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t learnmate .
docker run -p 5000:5000 --env-file .env learnmate
```

### Deploy to IBM Code Engine / Cloud Foundry

```bash
# IBM Cloud CLI
ibmcloud login
ibmcloud cf push learnmate -b python_buildpack
```

---

## 🎨 Customizing the AI Agent

Open [`agent.py`](agent.py) and edit the `AGENT_INSTRUCTIONS` block at the top:

```python
# ── Personality & tone ──────────────────────────────────────────────────────
AGENT_PERSONALITY = "..."         # Change persona, language, energy level

# ── Career coaching style ───────────────────────────────────────────────────
CAREER_COACHING_STYLE = "..."     # Change approach (mentorship, tough-love, etc.)

# ── Learning preferences ────────────────────────────────────────────────────
LEARNING_PREFERENCE_STYLE = "..."  # Adjust how resources are recommended

# ── Recommendation behavior ─────────────────────────────────────────────────
RECOMMENDATION_BEHAVIOR = "..."   # How topics are selected and ordered

# ── Motivation messages ─────────────────────────────────────────────────────
MOTIVATION_STYLE = "..."          # Style of motivational messages

# ── Difficulty calibration ──────────────────────────────────────────────────
DIFFICULTY_CALIBRATION = "..."    # How content adapts to skill level
```

---

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore`
- Rotate your IBM API key regularly
- Use `FLASK_ENV=production` in deployment
- Set a long, random `FLASK_SECRET_KEY` in production

---

## 🤖 IBM Granite Model

LearnMate uses **IBM Granite 3.3 8B Instruct** (`ibm/granite-3-1-8b-base`):

- Optimized for instruction-following and conversational tasks
- Low latency, high quality responses
- Change the model in `agent.py`:

```python
MODEL_ID = "ibm/granite-3-1-8b-base"  # Change to any supported model
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | 3.0.3 | Web framework |
| `python-dotenv` | 1.0.1 | Environment variable management |
| `ibm-watsonx-ai` | 1.1.2 | IBM watsonx.ai SDK |
| `requests` | 2.32.3 | HTTP client |
| `gunicorn` | 22.0.0 | Production WSGI server |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `EnvironmentError: IBM_API_KEY must be set` | Copy `.env.example` → `.env` and fill credentials |
| `AI service unavailable (503)` | Check API key validity and watsonx project ID |
| `Module not found` | Run `pip install -r requirements.txt` in your virtualenv |
| Dark mode not saving | Check browser localStorage is enabled |
| Chat not responding | Open browser DevTools → Network tab for error details |

---

## 📄 License

MIT License – free to use, modify, and distribute.

---

*Built with ❤️ using Python Flask + IBM watsonx.ai (IBM Granite 3.3)*
