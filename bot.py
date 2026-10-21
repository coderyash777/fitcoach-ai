import os
import sys
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise SystemExit("Error: OPENROUTER_API_KEY not found in .env file. Please check your .env file.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using openrouter/free model router
MODEL = "openrouter/free"

SYSTEM_PROMPT = """You are 'FitCoach AI', a supportive, motivating, and knowledgeable personal fitness coach and sports nutritionist.

Your mission:
- Guide the user towards their fitness, health, strength, and body composition goals safely and effectively.
- Provide custom workout plans (gym or home, bodyweight, dumbbells, cardio).
- Offer nutrition advice, calorie/macro breakdowns, healthy meal suggestions, and hydration tips.
- Teach proper exercise form, injury prevention, warmups, and recovery routines.
- Keep the user disciplined and motivated like a friendly, dedicated personal trainer.

Style guidelines:
- If you don't know the user's stats or goals yet, proactively ask 2-3 friendly questions (e.g., current fitness level, goal, workout location/equipment).
- Use clear bullet points, bold text for exercises, sets, and reps, and keep advice realistic and sustainable.
- Keep tone positive, energetic, and encouraging!
"""

def chat_with_coach():
    print("=" * 60)
    print("  🏋️  Welcome to FitCoach AI - Your Personal Fitness Coach! 🏋️")
    print("=" * 60)
    print("Commands:")
    print("  - Type 'exit' or 'quit' to end the session.")
    print("  - Type 'clear' to reset chat memory.")
    print("  - Type 'save' to export chat history to a text file.")
    print("-" * 60)
    print("FitCoach: Hey there! I'm your personal fitness coach. What are your main fitness goals right now? (e.g., lose fat, build muscle, increase stamina, home workouts)")
    print("-" * 60)

    # Initialize conversation history with system instructions
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nFitCoach: Keep grinding! See you next workout! 💪")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("\nFitCoach: Great work today! Stay hydrated and consistent! 💪")
            break

        if user_input.lower() == "clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("\n[Memory cleared. Starting fresh!]")
            continue

        if user_input.lower() == "save":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fitness_chat_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for msg in messages:
                    if msg["role"] != "system":
                        f.write(f"{msg['role'].capitalize()}: {msg['content']}\n\n")
            print(f"\n[Chat history saved to {filename}]")
            continue

        # Add user's message to conversation history
        messages.append({"role": "user", "content": user_input})

        print("\nFitCoach is thinking...", end="\r", flush=True)

        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Personal Fitness Chatbot",
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                },
                timeout=60,
            )

            # Clear the 'thinking...' line
            print(" " * 30, end="\r")

            if not response.ok:
                print(f"Error {response.status_code}: {response.text[:300]}")
                # Remove the last user message if the request failed so history stays clean
                messages.pop()
                continue

            data = response.json()
            reply = data["choices"][0]["message"]["content"]

            # Append assistant's reply to conversation history
            messages.append({"role": "assistant", "content": reply})

            print(f"FitCoach:\n{reply}\n")

        except requests.RequestException as error:
            print(f"\nNetwork error: {error}")
            messages.pop()

if __name__ == "__main__":
    chat_with_coach()
