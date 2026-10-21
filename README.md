# 🏋️ FitCoach AI - Personal Fitness & Nutrition Chatbot

A personalized AI fitness coach powered by OpenRouter.

## ✨ Features
- **Personalized Coaching:** Tailored workout splits (gym/home/bodyweight), custom calorie & macro targets, healthy meal plans, and warm-up routines.
- **Conversation Memory:** Remembers your height, weight, goals, and previous messages throughout your chat session.
- **Two Ways to Chat:**
  1. **Terminal CLI (`bot.py`):** Fast, interactive command-line chat with save & clear commands.
  2. **Modern Web UI (`web_bot.py`):** Beautiful dark-mode web application running locally at `http://localhost:5000` with Markdown rendering and quick-prompt chips.

## 🚀 Quick Start

### 1. Requirements
Ensure you have Python 3.10+ installed and the required packages:
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Your `.env` file is already created in this directory:
```env
OPENROUTER_API_KEY=your_key_here
```

### 3. Run the Bot

**Option A: Interactive Terminal Coach**
```bash
python bot.py
```
- Type `exit` to quit.
- Type `clear` to reset memory.
- Type `save` to export your conversation to a text file.

**Option B: Web Browser Interface**
```bash
python web_bot.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.
