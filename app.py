import os
from pathlib import Path
from dotenv import load_dotenv

# Find the exact path to the directory containing app.py
env_path = Path(__file__).resolve().parent / ".env"

# Force load the .env file from that exact path
load_dotenv(dotenv_path=env_path)

# Retrieve the API key
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError(
        f"GROQ_API_KEY environment variable not set. Looked for .env at: {env_path}"
    )
import os
from flask import Flask, render_template, request, jsonify, session
from groq import Groq
from profile_data import PROFILE_SYSTEM_PROMPT

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

# Read API key from environment variable (never hardcode it in source)
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY environment variable not set. "
        'Run in PowerShell: $env:GROQ_API_KEY = "your-key-here"'
    )

# Initialize Groq client
client = Groq(api_key=api_key)

# Select model
model = "openai/gpt-oss-120b"


def new_conversation():
    """Fresh conversation history, seeded with Hithaishi's profile context."""
    return [{"role": "system", "content": PROFILE_SYSTEM_PROMPT}]


@app.route("/")
def index():
    # Start a fresh conversation each time the page loads
    session["conversation_history"] = new_conversation()
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    # Retrieve conversation history from session (seed it if missing, e.g. session expired)
    conversation_history = session.get("conversation_history") or new_conversation()

    # Add user input to conversation history
    conversation_history.append({"role": "user", "content": user_input})

    try:
        # Get the Groq response
        response = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            max_tokens=350,
            temperature=0.7,
        )

        # Extract the output text
        ai_output = response.choices[0].message.content

        # Add the AI message into the conversation history
        conversation_history.append({"role": "assistant", "content": ai_output})

        # Save updated history back to session
        session["conversation_history"] = conversation_history

        return jsonify({"reply": ai_output})

    except Exception as e:
        return jsonify({"error": f"Sorry, I encountered an error: {str(e)}"}), 500


@app.route("/reset", methods=["POST"])
def reset():
    session["conversation_history"] = new_conversation()
    return jsonify({"status": "conversation reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
