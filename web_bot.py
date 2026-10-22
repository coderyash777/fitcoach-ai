import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")

SYSTEM_PROMPT = """You are 'FitCoach AI', a supportive, motivating, and knowledgeable personal fitness coach and sports nutritionist.

Your mission:
- Guide the user towards their fitness, health, strength, and body composition goals safely and effectively.
- Provide custom workout plans (gym, home, bodyweight, dumbbells, cardio).
- Offer nutrition advice, calorie/macro breakdowns, healthy meal suggestions, and hydration tips.
- Teach proper exercise form, injury prevention, warmups, and recovery routines.
- Keep the user disciplined and motivated like a friendly, dedicated personal trainer.

Style guidelines:
- If you don't know the user's stats or goals yet, proactively ask 2-3 friendly questions.
- Use clear bullet points, bold text for exercises, sets, reps, and keep advice realistic and sustainable.
- Format responses nicely in markdown.
"""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FitCoach AI - Personal Fitness Coach</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --card: #1e293b;
      --card-hover: #334155;
      --accent: #10b981;
      --accent-glow: rgba(16, 185, 129, 0.25);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --user-bubble: #2563eb;
      --bot-bubble: #1e293b;
      --border: #334155;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    header {
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 14px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand .logo {
      font-size: 26px;
      background: #10b98122;
      border: 1px solid var(--accent);
      padding: 6px 10px;
      border-radius: 10px;
    }
    .brand h1 { font-size: 1.15rem; font-weight: 700; color: #fff; }
    .brand p { font-size: 0.75rem; color: var(--accent); }
    .header-actions {
      display: flex;
      gap: 10px;
    }
    .btn-secondary {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.8rem;
      transition: all 0.2s;
    }
    .btn-secondary:hover {
      background: var(--card-hover);
      color: var(--text);
    }
    #chat-container {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-width: 900px;
      width: 100%;
      margin: 0 auto;
    }
    .message {
      display: flex;
      gap: 12px;
      max-width: 85%;
      animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .message.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }
    .message.bot {
      align-self: flex-start;
    }
    .avatar {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      flex-shrink: 0;
    }
    .bot .avatar {
      background: #10b98122;
      border: 1px solid var(--accent);
    }
    .user .avatar {
      background: #2563eb33;
      border: 1px solid #3b82f6;
    }
    .bubble {
      padding: 12px 16px;
      border-radius: 14px;
      font-size: 0.95rem;
      line-height: 1.55;
    }
    .user .bubble {
      background: var(--user-bubble);
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .bot .bubble {
      background: var(--bot-bubble);
      color: var(--text);
      border: 1px solid var(--border);
      border-bottom-left-radius: 4px;
    }
    .bot .bubble p { margin-bottom: 8px; }
    .bot .bubble p:last-child { margin-bottom: 0; }
    .bot .bubble ul, .bot .bubble ol { margin: 8px 0 8px 20px; }
    .bot .bubble table {
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0;
      font-size: 0.85rem;
    }
    .bot .bubble th, .bot .bubble td {
      border: 1px solid var(--border);
      padding: 6px 10px;
      text-align: left;
    }
    .bot .bubble th { background: rgba(255,255,255,0.05); }
    .bot .bubble strong { color: #38bdf8; }
    .quick-prompts {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 0 20px 10px;
      max-width: 900px;
      width: 100%;
      margin: 0 auto;
    }
    .chip {
      background: var(--card);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 16px;
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .chip:hover {
      border-color: var(--accent);
      color: var(--accent);
      background: rgba(16, 185, 129, 0.08);
    }
    footer {
      background: var(--card);
      border-top: 1px solid var(--border);
      padding: 12px 20px;
    }
    .input-box {
      max-width: 900px;
      margin: 0 auto;
      display: flex;
      gap: 10px;
    }
    textarea {
      flex: 1;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 12px 14px;
      border-radius: 10px;
      resize: none;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      height: 48px;
      line-height: 1.4;
    }
    textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-glow);
    }
    .btn-send {
      background: var(--accent);
      color: #0f172a;
      border: none;
      font-weight: 700;
      padding: 0 20px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 0.95rem;
      transition: all 0.2s;
    }
    .btn-send:hover { opacity: 0.9; }
    .btn-send:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .typing-dots span {
      display: inline-block;
      width: 6px;
      height: 6px;
      margin: 0 2px;
      background: var(--accent);
      border-radius: 50%;
      animation: bounce 1.2s infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-6px); }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="logo">🏋️</div>
      <div>
        <h1>FitCoach AI</h1>
        <p>● Online & Ready to Train</p>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn-secondary" onclick="resetChat()">🔄 Reset Chat</button>
    </div>
  </header>

  <div id="chat-container">
    <div class="message bot">
      <div class="avatar">🏋️</div>
      <div class="bubble">
        <p><strong>Hey there! I'm FitCoach AI.</strong></p>
        <p>I'm your personal coach for workout splits, customized meal plans, calorie/macro counting, and daily motivation. What's your top fitness goal right now?</p>
      </div>
    </div>
  </div>

  <div class="quick-prompts">
    <div class="chip" onclick="quickSend('I want to lose 5kg in 2 months. Make me a plan.')">🎯 Lose 5kg in 2 months</div>
    <div class="chip" onclick="quickSend('Give me a 4-day muscle building gym workout routine.')">💪 4-Day Muscle Split</div>
    <div class="chip" onclick="quickSend('I have 30 mins at home with no equipment. Give me a killer workout!')">🏠 30-min Home HIIT</div>
    <div class="chip" onclick="quickSend('Calculate my daily calories and protein for weight loss.')">🥗 Calculate Calories & Protein</div>
  </div>

  <footer>
    <form class="input-box" onsubmit="event.preventDefault(); sendMessage();">
      <textarea id="user-input" placeholder="Ask about workouts, diet plans, macros, or form..." onkeydown="handleKeyDown(event)"></textarea>
      <button class="btn-send" id="send-btn" type="submit">Send</button>
    </form>
  </footer>

  <script>
    let chatHistory = [];

    function handleKeyDown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    }

    function quickSend(text) {
      document.getElementById('user-input').value = text;
      sendMessage();
    }

    function appendMessage(role, text) {
      const container = document.getElementById('chat-container');
      const msgDiv = document.createElement('div');
      msgDiv.className = `message ${role}`;
      
      const avatar = document.createElement('div');
      avatar.className = 'avatar';
      avatar.textContent = role === 'user' ? '👤' : '🏋️';
      
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      if (role === 'bot') {
        bubble.innerHTML = marked.parse(text);
      } else {
        bubble.textContent = text;
      }
      
      msgDiv.appendChild(avatar);
      msgDiv.appendChild(bubble);
      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
      return msgDiv;
    }

    async function sendMessage() {
      const input = document.getElementById('user-input');
      const text = input.value.trim();
      if (!text) return;

      appendMessage('user', text);
      input.value = '';

      const sendBtn = document.getElementById('send-btn');
      sendBtn.disabled = true;

      // Temporary typing indicator
      const container = document.getElementById('chat-container');
      const typingDiv = document.createElement('div');
      typingDiv.className = 'message bot typing-indicator';
      typingDiv.innerHTML = '<div class="avatar">🏋️</div><div class="bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
      container.appendChild(typingDiv);
      container.scrollTop = container.scrollHeight;

      chatHistory.push({ role: 'user', content: text });

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: chatHistory })
        });
        
        const data = await response.json();
        typingDiv.remove();

        if (data.reply) {
          appendMessage('bot', data.reply);
          chatHistory.push({ role: 'assistant', content: data.reply });
        } else {
          appendMessage('bot', '⚠️ Error: ' + (data.error || 'Could not get response.'));
        }
      } catch (err) {
        typingDiv.remove();
        appendMessage('bot', '⚠️ Connection error: ' + err.message);
      } finally {
        sendBtn.disabled = false;
        input.focus();
      }
    }

    function resetChat() {
      chatHistory = [];
      const container = document.getElementById('chat-container');
      container.innerHTML = `
        <div class="message bot">
          <div class="avatar">🏋️</div>
          <div class="bubble">
            <p><strong>Chat reset! Ready for your next session.</strong></p>
            <p>What are your goals today? Workout plan, diet tips, or motivation?</p>
          </div>
        </div>
      `;
    }
  </script>
</body>
</html>
"""

class FitnessBotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                user_messages = data.get("messages", [])

                api_key = (os.getenv("OPENROUTER_API_KEY") or API_KEY or "").strip()
                if not api_key or api_key in ("None", "your_key_here"):
                    error_msg = (
                        "OPENROUTER_API_KEY is missing. If deployed on Render, "
                        "go to Render Dashboard -> fitcoach-ai -> Environment -> Add 'OPENROUTER_API_KEY'."
                    )
                    res_payload = json.dumps({"error": error_msg})
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(res_payload.encode("utf-8"))
                    return

                # Prepend the system prompt
                full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_messages

                candidates = [
                    os.getenv("OPENROUTER_MODEL", "").strip(),
                    MODEL,
                    "minimax/minimax-m3.1-flash:free",
                    "openrouter/free",
                ]
                models_to_try = []
                for m in candidates:
                    if m and m not in models_to_try:
                        models_to_try.append(m)

                reply = None
                last_error = None
                status_code = 502

                for current_model in models_to_try:
                    try:
                        response = requests.post(
                            API_URL,
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json",
                                "HTTP-Referer": "https://fitcoach-ai.onrender.com",
                                "X-Title": "Personal Fitness Coach Web App",
                            },
                            json={
                                "model": current_model,
                                "messages": full_messages,
                            },
                            timeout=60,
                        )
                        if response.ok:
                            res_data = response.json()
                            content = res_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if content and not content.strip().startswith("User Safety:"):
                                reply = content
                                break
                        else:
                            status_code = response.status_code
                            last_error = f"API error {response.status_code}: {response.text[:200]}"
                    except Exception as req_err:
                        last_error = str(req_err)

                if reply:
                    res_payload = json.dumps({"reply": reply})
                    self.send_response(200)
                else:
                    res_payload = json.dumps({"error": last_error or "Unable to get response from AI provider."})
                    self.send_response(status_code)

            except Exception as e:
                res_payload = json.dumps({"error": str(e)})
                self.send_response(500)

            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(res_payload.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Clean logging
        sys.stdout.write(f"[Server] {format % args}\n")

def run(port=5000):
    import webbrowser
    server = HTTPServer(("0.0.0.0", port), FitnessBotHandler)
    url = f"http://localhost:{port}"
    print("=" * 60)
    print(f"🏋️  FitCoach AI Web App running at: {url}")
    print(f"    Alternative link: http://127.0.0.1:{port}")
    print("Opening browser automatically...")
    print("Press Ctrl+C in this terminal to stop the server.")
    print("=" * 60)
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    # Support Render / Cloud environment PORT variable
    port = int(os.environ.get("PORT", 5000))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run(port)
