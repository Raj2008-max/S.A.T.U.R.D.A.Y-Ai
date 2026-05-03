from flask import Flask, request, jsonify, render_template_string
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
print("KEY FOUND:", os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(prompt, history=None):
    messages = [
        {
            "role": "system",
            "content": (
                "You are S.A.T.U.R.D.A.Y — a brilliant, witty, and highly capable AI assistant. "
                "Your name stands for Synthetized Artificial Thought Unit for Reasoning, Decisions, and Yielding answers. "
                "You are sleek, confident, and helpful. Keep responses clear and conversational. "
                "You were created as a personal AI assistant project."
            )
        }
    ]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1024
    )
    return response.choices[0].message.content


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>S.A.T.U.R.D.A.Y</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #eef1f7;
  --surface: #ffffff;
  --surface2: #f4f6fb;
  --border: rgba(0,0,0,0.07);
  --text: #0f1117;
  --text-muted: #7b8299;
  --text-faint: #b0b6cc;
  --accent: #4657f5;
  --accent-light: #eaedff;
  --accent-glow: rgba(70,87,245,0.18);
  --shadow: 0 8px 40px rgba(70,87,245,0.10);
  --radius: 20px;
  --radius-sm: 14px;
  --sidebar-w: 240px;
  --sidebar-w-tablet: 190px;
  --header-h: 60px;
}

html, body {
  height: 100%;
  /* FIX 1: Use dvh for stable mobile viewport (handles browser chrome show/hide) */
  height: 100dvh;
  overflow: hidden;
}

body {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
  height: 100dvh;
}

body::before {
  content: '';
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse 70% 55% at 15% 8%, rgba(70,87,245,0.09) 0%, transparent 60%),
    radial-gradient(ellipse 55% 45% at 88% 82%, rgba(130,80,255,0.08) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}

/* ===================== SPLASH ===================== */
#splash {
  position: fixed; inset: 0; z-index: 100;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: linear-gradient(145deg, #f0f3ff 0%, #e8ecf8 100%);
  transition: opacity 0.55s ease, transform 0.55s ease;
}
#splash.hidden { opacity: 0; pointer-events: none; transform: scale(1.03); }

.splash-bot {
  width: 120px; height: 120px; border-radius: 50%;
  background: #fff;
  box-shadow: 0 16px 50px rgba(70,87,245,0.20), 0 0 0 2px rgba(70,87,245,0.10);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 28px;
  animation: float 3s ease-in-out infinite;
  position: relative; overflow: hidden;
}
.splash-bot::before {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 38%; background: linear-gradient(90deg, #4657f5, #8b5cf6, #06b6d4);
  border-radius: 0 0 50% 50%;
}
.bot-face { position: relative; z-index: 2; display: flex; gap: 13px; margin-top: -8px; }
.bot-eye {
  width: 15px; height: 15px; background: #0f1117; border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0,0,0,0.12); animation: blink 4s infinite;
}
@keyframes blink { 0%,90%,100% { transform: scaleY(1); } 95% { transform: scaleY(0.07); } }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-9px); } }

.splash-name {
  font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 4px; color: var(--accent); margin-bottom: 6px;
}
.splash-tagline { font-size: 14px; color: var(--text-muted); margin-bottom: 44px; font-weight: 300; }
.splash-btn {
  background: var(--accent); color: #fff; border: none; border-radius: 50px;
  padding: 14px 42px; font-size: 15px; font-weight: 600;
  font-family: 'DM Sans', sans-serif; cursor: pointer;
  box-shadow: 0 8px 22px var(--accent-glow);
  transition: transform 0.2s, box-shadow 0.2s; margin-bottom: 18px;
}
.splash-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px var(--accent-glow); }
.splash-login { font-size: 13px; color: var(--text-muted); }
.splash-login a { color: var(--accent); text-decoration: none; font-weight: 500; }

/* ===================== APP SHELL ===================== */
#app {
  position: relative; z-index: 1;
  display: flex; width: 100vw;
  height: 100vh;
  height: 100dvh; /* FIX 1: dynamic viewport height */
  opacity: 0; transform: translateY(14px);
  transition: opacity 0.5s ease 0.15s, transform 0.5s ease 0.15s;
  overflow: hidden;
}
#app.visible { opacity: 1; transform: translateY(0); }

/* ===================== SIDEBAR ===================== */
#sidebar {
  width: var(--sidebar-w);
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  flex-shrink: 0; overflow: hidden;
  transition: width 0.3s ease, transform 0.3s ease;
  z-index: 10;
}

.sb-header {
  padding: 20px 16px 14px;
  border-bottom: 1px solid var(--border);
  display: flex; flex-direction: column; align-items: center; gap: 7px;
}
.sb-bot {
  width: 52px; height: 52px; border-radius: 50%;
  background: #fff;
  box-shadow: 0 4px 16px rgba(70,87,245,0.15), 0 0 0 1.5px rgba(70,87,245,0.10);
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
}
.sb-bot::before {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 36%; background: linear-gradient(90deg, #4657f5, #8b5cf6);
  border-radius: 0 0 50% 50%;
}
.sb-bot-eyes { position: relative; z-index: 2; display: flex; gap: 6px; margin-top: -3px; }
.sb-bot-eye { width: 7px; height: 7px; background: #0f1117; border-radius: 50%; }
.sb-name {
  font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 700;
  letter-spacing: 2.5px; color: var(--accent);
}
.sb-status { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--text-muted); }
.sb-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; animation: pulse-dot 2s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.5;transform:scale(0.75);} }

.sb-body { flex: 1; overflow-y: auto; padding: 12px 10px; }
.sb-body::-webkit-scrollbar { width: 3px; }
.sb-body::-webkit-scrollbar-thumb { background: rgba(70,87,245,0.12); border-radius: 3px; }

.sb-section-label {
  font-size: 10px; font-weight: 600; letter-spacing: 1.5px;
  color: var(--text-faint); padding: 6px 8px 4px; text-transform: uppercase;
}
.sb-item {
  display: flex; align-items: center; gap: 9px;
  padding: 9px 10px; border-radius: 10px;
  font-size: 13px; color: var(--text-muted);
  cursor: pointer; transition: background 0.18s, color 0.18s;
  margin-bottom: 1px;
}
.sb-item:hover { background: var(--surface2); color: var(--text); }
.sb-item.active { background: var(--accent-light); color: var(--accent); font-weight: 500; }
.sb-item-icon { font-size: 14px; width: 18px; text-align: center; flex-shrink: 0; }
.sb-item-text { flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.sb-item-time { font-size: 10px; color: var(--text-faint); flex-shrink: 0; }
.sb-divider { height: 1px; background: var(--border); margin: 8px 0; }

.sb-footer { padding: 10px; border-top: 1px solid var(--border); }
.sb-footer-btn {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 9px 10px; border-radius: 10px;
  background: none; border: none; font-family: 'DM Sans', sans-serif;
  font-size: 13px; color: var(--text-muted); cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.sb-footer-btn:hover { background: var(--surface2); color: var(--text); }

/* ===================== MAIN ===================== */
#main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
  min-height: 0;
  height: 100%;
  /* FIX 3: ensure main always fills available space */
  min-width: 0;
  transition: margin-left 0.3s ease;
}

.header {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 20;
  height: var(--header-h);
}
.header-menu-btn {
  display: none;
  width: 34px; height: 34px; align-items: center; justify-content: center;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 50%; cursor: pointer; font-size: 16px;
  transition: background 0.2s; flex-shrink: 0;
}
.header-menu-btn:hover { background: var(--accent-light); }
.header-bot {
  width: 36px; height: 36px; border-radius: 50%; background: #fff;
  box-shadow: 0 3px 12px rgba(70,87,245,0.14), 0 0 0 1.5px rgba(70,87,245,0.10);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; position: relative; overflow: hidden;
}
.header-bot::before {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 36%; background: linear-gradient(90deg, #4657f5, #8b5cf6);
  border-radius: 0 0 50% 50%;
}
.header-bot-eyes { position: relative; z-index: 2; display: flex; gap: 5px; margin-top: -2px; }
.header-bot-eye { width: 6px; height: 6px; background: #fff; border-radius: 50%; }
.header-info { flex: 1; }
.header-title {
  font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 2px; color: var(--text);
}
.header-status {
  display: flex; align-items: center; gap: 4px;
  font-size: 10px; color: var(--text-muted); margin-top: 1px;
}
.status-dot { width: 5px; height: 5px; background: #22c55e; border-radius: 50%; animation: pulse-dot 2s infinite; }
.header-actions { display: flex; gap: 6px; }
.icon-btn {
  width: 32px; height: 32px; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 13px;
  transition: background 0.2s, transform 0.15s;
}
.icon-btn:hover { background: var(--accent-light); transform: scale(1.08); }
.icon-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }

/* ===================== CHAT BODY ===================== */
#chat-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin: 12px;
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  min-height: 0;
}

#chatbox {
  flex: 1;
  overflow-y: auto;
  padding: 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
  min-height: 0;
  /* FIX: ensure overscroll doesn't bounce on iOS */
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}
#chatbox::-webkit-scrollbar { width: 4px; }
#chatbox::-webkit-scrollbar-thumb { background: rgba(70,87,245,0.12); border-radius: 4px; }

.welcome {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; flex: 1; text-align: center;
  gap: 8px; padding: 30px 20px;
}
.welcome-emoji { font-size: 38px; margin-bottom: 4px; }
.welcome-title { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: var(--text); }
.welcome-sub { font-size: 13px; color: var(--text-muted); line-height: 1.55; max-width: 280px; margin-top: 4px; }
.welcome-chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 12px; }
.chip {
  background: var(--accent-light); color: var(--accent);
  border-radius: 50px; padding: 8px 15px; font-size: 12px; font-weight: 500;
  cursor: pointer; border: 1px solid rgba(70,87,245,0.15); transition: all 0.18s;
}
.chip:hover { background: var(--accent); color: #fff; transform: translateY(-1px); }

.msg-row { display: flex; align-items: flex-end; gap: 8px; animation: slideUp 0.28s ease; }
.msg-row.user { flex-direction: row-reverse; }
@keyframes slideUp { from{opacity:0;transform:translateY(10px);} to{opacity:1;transform:translateY(0);} }

.avatar {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; overflow: hidden; position: relative;
}
.avatar.bot-avatar { background: #f0f3ff; border: 1px solid rgba(70,87,245,0.14); }
.avatar.bot-avatar::before {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 35%; background: linear-gradient(90deg, #4657f5, #8b5cf6);
  border-radius: 0 0 50% 50%;
}
.avatar-eyes { position: relative; z-index: 2; display: flex; gap: 4px; margin-top: -2px; }
.avatar-eye { width: 5px; height: 5px; background: #0f1117; border-radius: 50%; }
.avatar.user-avatar { background: var(--accent); color: #fff; font-weight: 600; }

.bubble {
  max-width: 72%; padding: 11px 14px;
  border-radius: var(--radius-sm); font-size: 14px; line-height: 1.56;
  word-break: break-word; /* FIX: prevent long words from overflowing */
}
.bubble.bot {
  background: #fff; border: 1px solid var(--border);
  border-bottom-left-radius: 4px; color: var(--text);
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.bubble.user {
  background: var(--accent); color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 14px var(--accent-glow);
}

.bubble-actions { display: flex; gap: 5px; margin-top: 6px; flex-wrap: wrap; }
.bubble-action-btn {
  background: var(--surface2); border: 1px solid var(--border); border-radius: 50px;
  padding: 4px 10px; font-size: 11px; color: var(--text-muted); cursor: pointer;
  transition: all 0.18s;
}
.bubble-action-btn:hover { background: var(--accent-light); color: var(--accent); border-color: rgba(70,87,245,0.2); }

.typing-row { display: flex; align-items: flex-end; gap: 8px; }
.typing-bubble {
  background: #fff; border: 1px solid var(--border);
  border-radius: var(--radius-sm); border-bottom-left-radius: 4px;
  padding: 13px 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  display: flex; gap: 5px; align-items: center;
}
.typing-dot {
  width: 7px; height: 7px; background: var(--accent); border-radius: 50%;
  opacity: 0.4; animation: bounce 1.2s infinite;
}
.typing-dot:nth-child(2){animation-delay:.2s;} .typing-dot:nth-child(3){animation-delay:.4s;}
@keyframes bounce{0%,60%,100%{transform:translateY(0);opacity:.4;} 30%{transform:translateY(-6px);opacity:1;}}

/* ===================== INPUT AREA ===================== */
.input-area {
  padding: 10px 14px 14px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  border-radius: 0 0 var(--radius) var(--radius);
  flex-shrink: 0;
  /* FIX 2: safe area inset for notched phones */
  padding-bottom: max(14px, env(safe-area-inset-bottom));
  /* Keep input above keyboard on mobile */
  position: relative;
  z-index: 5;
}
.wake-badge {
  display: none; align-items: center; gap: 5px;
  background: var(--accent-light); color: var(--accent);
  border: 1px solid rgba(70,87,245,0.18); border-radius: 50px;
  padding: 4px 12px; font-size: 11px; font-weight: 500; margin-bottom: 8px;
}
.wake-badge.visible { display: flex; }
.speaking-badge {
  display: none; align-items: center; gap: 6px;
  font-size: 11px; color: var(--text-muted); margin-bottom: 6px;
}
.speaking-badge.visible { display: flex; }
.wave { display: flex; gap: 2px; align-items: center; }
.wave span { display: block; width: 2px; background: var(--accent); border-radius: 2px; animation: wv .8s infinite ease-in-out; }
.wave span:nth-child(1){height:7px;} .wave span:nth-child(2){height:13px;animation-delay:.1s;}
.wave span:nth-child(3){height:9px;animation-delay:.2s;} .wave span:nth-child(4){height:15px;animation-delay:.15s;}
.wave span:nth-child(5){height:7px;animation-delay:.3s;}
@keyframes wv{0%,100%{transform:scaleY(0.5);} 50%{transform:scaleY(1);}}

.input-row {
  display: flex; align-items: center; gap: 7px;
  background: var(--surface2); border: 1.5px solid var(--border);
  border-radius: 50px; padding: 6px 6px 6px 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-row:focus-within { border-color: rgba(70,87,245,0.35); box-shadow: 0 0 0 3px var(--accent-glow); }
#msg {
  flex: 1; border: none; outline: none; background: transparent;
  font-family: 'DM Sans', sans-serif; color: var(--text);
  font-size: 16px; /* FIX: prevents mobile zoom on focus (must be >= 16px) */
  line-height: 1.4;
  /* FIX: prevent iOS from doing weird things */
  -webkit-appearance: none;
  appearance: none;
}
#msg::placeholder { color: var(--text-muted); }

/* FIX: ensure disabled state is visible */
#msg:disabled { opacity: 0.6; cursor: not-allowed; }

.input-btns { display: flex; align-items: center; gap: 4px; }
.mic-btn, .send-btn {
  width: 36px; height: 36px; border-radius: 50%; border: none;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 14px; transition: all 0.2s; flex-shrink: 0;
  /* FIX: make buttons reliably tappable on mobile */
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
.mic-btn { background: var(--surface); border: 1.5px solid var(--border); color: var(--text-muted); }
.mic-btn:hover { background: var(--accent-light); color: var(--accent); }
.mic-btn.listening { background: #fee2e2; color: #ef4444; border-color: #fca5a5; animation: pulse-mic 1s infinite; }
@keyframes pulse-mic{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.3);} 50%{box-shadow:0 0 0 6px rgba(239,68,68,0);}}
.send-btn { background: var(--accent); color: #fff; box-shadow: 0 4px 12px var(--accent-glow); }
.send-btn:hover { transform: scale(1.08); }
.send-btn:disabled { opacity: 0.4; cursor: default; transform: none; }

/* Loading state for send button */
.send-btn.loading {
  opacity: 0.7;
  cursor: wait;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* ===================== TOAST ===================== */
#toast {
  position: fixed; bottom: 22px; left: 50%;
  transform: translateX(-50%) translateY(60px);
  background: #0f1117; color: #fff;
  padding: 8px 20px; border-radius: 50px;
  font-size: 13px; font-weight: 500; z-index: 200;
  transition: transform 0.28s ease; pointer-events: none;
}
#toast.show { transform: translateX(-50%) translateY(0); }

/* ===================== OVERLAY ===================== */
#sidebar-overlay {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,0.28); z-index: 9;
}
#sidebar-overlay.visible { display: block; }

/* ===================== RESPONSIVE ===================== */

/* Desktop > 900px */
@media (min-width: 900px) {
  #sidebar { width: var(--sidebar-w); transform: none !important; }
  .header-menu-btn { display: none !important; }
  .header-bot, .header-info { display: none; }
  .header { justify-content: flex-end; padding: 12px 16px; border-bottom: none; background: transparent; }
  #chat-body { margin: 14px 14px 14px 0; }
}

/* Tablet 600–899px */
@media (min-width: 600px) and (max-width: 899px) {
  #sidebar {
    width: var(--sidebar-w-tablet);
    /* FIX: use absolute positioning so collapse gives full width to main */
    position: absolute;
    height: 100%;
    z-index: 10;
    top: 0; left: 0;
    transition: transform 0.3s ease;
    box-shadow: none;
  }
  #sidebar.collapsed {
    transform: translateX(calc(-1 * var(--sidebar-w-tablet)));
    box-shadow: 4px 0 24px rgba(0,0,0,0.1);
  }
  /* FIX 3: main always fills full width, sidebar overlays it */
  #main {
    width: 100%;
    margin-left: 0 !important;
  }
  .header-menu-btn { display: flex !important; }
  .header-bot, .header-info { display: flex; }
  #chat-body { margin: 10px 10px 10px 10px; border-radius: 16px; }
  .sb-item-time { display: none; }
}

/* Phone < 600px */
@media (max-width: 599px) {
  #sidebar {
    position: absolute; height: 100%; width: 260px;
    transform: translateX(-110%); transition: transform 0.3s ease;
    box-shadow: 4px 0 30px rgba(0,0,0,0.12);
    z-index: 10;
  }
  #sidebar.open { transform: translateX(0); }
  /* FIX: prevent main content from being interactive under open sidebar */
  #sidebar.open ~ #sidebar-overlay { pointer-events: all; }

  .header-menu-btn { display: flex !important; }
  .header-bot, .header-info { display: flex; }

  #main {
    width: 100%;
    /* FIX: main always fills full width on mobile */
    flex: 1;
    min-width: 0;
  }

  #chat-body {
    margin: 8px;
    border-radius: 16px;
    flex: 1;
    min-height: 0;
  }

  .bubble { max-width: 85%; font-size: 13px; }
  .header { padding: 12px 14px; }
  .sb-item-time { display: none; }

  .input-area {
    padding: 8px 10px;
    /* FIX 2: safe area for iPhone notch / home indicator */
    padding-bottom: max(12px, env(safe-area-inset-bottom));
  }

  #msg {
    font-size: 16px; /* FIX: prevents iOS Safari zoom on input focus */
  }

  /* Larger tap targets on mobile */
  .mic-btn, .send-btn {
    width: 40px; height: 40px;
  }
}
</style>
</head>
<body>

<!-- SPLASH -->
<div id="splash">
  <div class="splash-bot">
    <div class="bot-face"><div class="bot-eye"></div><div class="bot-eye"></div></div>
  </div>
  <div class="splash-name">S.A.T.U.R.D.A.Y</div>
  <div class="splash-tagline">Your personal AI assistant</div>
  <button class="splash-btn" onclick="startApp()">Get Started</button>
  <div class="splash-login">Already used it? <a href="#" onclick="startApp()">Jump back in</a></div>
</div>

<div id="sidebar-overlay" onclick="closeSidebar()"></div>

<!-- APP -->
<div id="app">

  <!-- SIDEBAR -->
  <div id="sidebar">
    <div class="sb-header">
      <div class="sb-bot">
        <div class="sb-bot-eyes"><div class="sb-bot-eye"></div><div class="sb-bot-eye"></div></div>
      </div>
      <div class="sb-name">S.A.T.U.R.D.A.Y</div>
      <div class="sb-status"><div class="sb-dot"></div>Online · LLaMA 3.1</div>
    </div>

    <div class="sb-body">
      <div class="sb-section-label">Chats</div>
      <div class="sb-item active" onclick="newChat()">
        <span class="sb-item-icon">💬</span>
        <span class="sb-item-text">Current chat</span>
        <span class="sb-item-time">Now</span>
      </div>
      <div class="sb-item" id="hist-1" style="display:none;" onclick="loadHistory()">
        <span class="sb-item-icon">🕐</span>
        <span class="sb-item-text" id="hist-1-label">Previous chat</span>
        <span class="sb-item-time">Earlier</span>
      </div>

      <div class="sb-divider"></div>
      <div class="sb-section-label">Quick prompts</div>
      <div class="sb-item" onclick="quickSend('Give me a fun fact')">
        <span class="sb-item-icon">💡</span><span class="sb-item-text">Fun fact</span>
      </div>
      <div class="sb-item" onclick="quickSend('Help me write something creative')">
        <span class="sb-item-icon">✍️</span><span class="sb-item-text">Write something</span>
      </div>
      <div class="sb-item" onclick="quickSend('Explain a concept in simple terms')">
        <span class="sb-item-icon">🧠</span><span class="sb-item-text">Explain a concept</span>
      </div>
      <div class="sb-item" onclick="quickSend('Help me solve a math problem')">
        <span class="sb-item-icon">🧮</span><span class="sb-item-text">Math problem</span>
      </div>
      <div class="sb-item" onclick="quickSend('Help me debug my code')">
        <span class="sb-item-icon">🐛</span><span class="sb-item-text">Debug code</span>
      </div>

      <div class="sb-divider"></div>
      <div class="sb-section-label">Voice</div>
      <div class="sb-item" onclick="toggleMic()">
        <span class="sb-item-icon">🎤</span><span class="sb-item-text">Start listening</span>
      </div>
      <div class="sb-item" onclick="toggleVoiceOutput()">
        <span class="sb-item-icon" id="sb-voice-icon">🔊</span>
        <span class="sb-item-text" id="sb-voice-label">Voice output on</span>
      </div>
    </div>

    <div class="sb-footer">
      <button class="sb-footer-btn" onclick="clearChat()">
        <span style="font-size:15px;">🗑️</span> Clear chat
      </button>
    </div>
  </div>

  <!-- MAIN -->
  <div id="main">
    <div class="header">
      <div class="header-menu-btn" onclick="toggleSidebar()">☰</div>
      <div class="header-bot">
        <div class="header-bot-eyes"><div class="header-bot-eye"></div><div class="header-bot-eye"></div></div>
      </div>
      <div class="header-info">
        <div class="header-title">S.A.T.U.R.D.A.Y</div>
        <div class="header-status"><div class="status-dot"></div>Online · LLaMA 3.1</div>
      </div>
      <div class="header-actions">
        <div class="icon-btn" id="voiceToggle" onclick="toggleVoiceOutput()" title="Toggle voice">🔊</div>
        <div class="icon-btn" onclick="clearChat()" title="Clear chat">🗑️</div>
      </div>
    </div>

    <div id="chat-body">
      <div id="chatbox">
        <div class="welcome" id="welcome">
          <div class="welcome-emoji">👋</div>
          <div class="welcome-title">Hey! I'm Saturday.</div>
          <div class="welcome-sub">Ask me anything — powered by LLaMA 3.1. Try a prompt or type your own.</div>
          <div class="welcome-chips">
            <div class="chip" onclick="quickSend('What is a cool fact about space?')">🌌 Space fact</div>
            <div class="chip" onclick="quickSend('Give me a fun fact')">💡 Fun fact</div>
            <div class="chip" onclick="quickSend('Help me write a short story')">✍️ Write a story</div>
            <div class="chip" onclick="quickSend('Explain AI in simple terms')">🤖 Explain AI</div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="wake-badge" id="wakeBadge">
          <div class="wake-dot"></div> Wake word active — listening...
        </div>
        <div class="speaking-badge" id="speakingBadge">
          <div class="wave"><span></span><span></span><span></span><span></span><span></span></div>
          Speaking...
        </div>
        <div class="input-row">
          <input
            id="msg"
            type="text"
            placeholder="Message S.A.T.U.R.D.A.Y..."
            autocomplete="off"
            autocorrect="off"
            autocapitalize="sentences"
            spellcheck="true"
          />
          <div class="input-btns">
            <button class="mic-btn" id="micBtn" title="Voice input">🎤</button>
            <button class="send-btn" id="sendBtn" title="Send message">➤</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="toast"></div>

<script>
// ===================== STATE =====================
let history = [];
let savedHistory = [];
let savedFirstMsg = '';
let lastPrompt = '';
let voiceOutputOn = false;
let isListening = false;
let isSending = false; // FIX: guard against double-sends
let recognition = null;
let wakeRecognition = null;
const synth = window.speechSynthesis;

// ===================== INIT =====================
// FIX: attach events in JS instead of inline onclick for input & buttons (more reliable on mobile)
document.addEventListener('DOMContentLoaded', function () {
  const msgInput = document.getElementById('msg');
  const sendBtn = document.getElementById('sendBtn');
  const micBtn  = document.getElementById('micBtn');

  // Send on Enter key (but allow Shift+Enter for newlines if ever textarea is used)
  msgInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMsg();
    }
  });

  // Send button click
  sendBtn.addEventListener('click', function () {
    sendMsg();
  });

  // Mic button click
  micBtn.addEventListener('click', function () {
    toggleMic();
  });
});

// ===================== APP STARTUP =====================
function startApp() {
  document.getElementById('splash').classList.add('hidden');
  setTimeout(() => {
    document.getElementById('app').classList.add('visible');
    startWakeWordListener();
  }, 250);
}

// ===================== SIDEBAR =====================
function toggleSidebar() {
  const sb  = document.getElementById('sidebar');
  const ov  = document.getElementById('sidebar-overlay');
  const w   = window.innerWidth;

  if (w < 600) {
    // Mobile: slide in/out as overlay
    const open = sb.classList.toggle('open');
    ov.classList.toggle('visible', open);
  } else {
    // Tablet: collapse off-screen, main fills width
    sb.classList.toggle('collapsed');
    // Show overlay when sidebar is open on tablet too
    const isCollapsed = sb.classList.contains('collapsed');
    ov.classList.toggle('visible', !isCollapsed);
  }
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open', 'collapsed');
  document.getElementById('sidebar-overlay').classList.remove('visible');
}

// ===================== TOAST =====================
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}

// ===================== WELCOME =====================
function hideWelcome() {
  const w = document.getElementById('welcome');
  if (w) w.remove();
}

// ===================== AVATAR =====================
function makeBotAvatar() {
  return `<div class="avatar bot-avatar"><div class="avatar-eyes"><div class="avatar-eye"></div><div class="avatar-eye"></div></div></div>`;
}

// ===================== MESSAGES =====================
function appendMessage(text, type) {
  hideWelcome();
  const box = document.getElementById('chatbox');
  const row = document.createElement('div');
  row.className = 'msg-row ' + type;
  const safe = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
  const attr = text.replace(/"/g, '&quot;');

  if (type === 'bot') {
    row.innerHTML = `${makeBotAvatar()}
      <div>
        <div class="bubble bot">${safe}</div>
        <div class="bubble-actions">
          <button class="bubble-action-btn copy-btn" data-text="${attr}">📋 Copy</button>
          <button class="bubble-action-btn retry-btn">🔄 Retry</button>
          <button class="bubble-action-btn read-btn">🔊 Read</button>
        </div>
      </div>`;

    // Attach action button events after DOM insert
    row.querySelector('.copy-btn').addEventListener('click', function () {
      copyMsg(this);
    });
    row.querySelector('.retry-btn').addEventListener('click', function () {
      regenerate();
    });
    row.querySelector('.read-btn').addEventListener('click', function () {
      const bubbleText = this.closest('.bubble-actions').previousElementSibling.innerText;
      speakText(bubbleText);
    });
  } else {
    row.innerHTML = `<div class="bubble user">${safe}</div><div class="avatar user-avatar">U</div>`;
  }

  box.appendChild(row);
  // FIX: use requestAnimationFrame to scroll after render
  requestAnimationFrame(() => {
    box.scrollTop = box.scrollHeight;
  });
}

// ===================== TYPING INDICATOR =====================
function showTyping() {
  const box = document.getElementById('chatbox');
  const el = document.createElement('div');
  el.className = 'typing-row'; el.id = 'typing';
  el.innerHTML = `${makeBotAvatar()}<div class="typing-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
  box.appendChild(el);
  requestAnimationFrame(() => { box.scrollTop = box.scrollHeight; });
}
function hideTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

// ===================== SEND MESSAGE — CORE FIX =====================
async function sendMsg() {
  // FIX: guard against double sends and empty messages
  if (isSending) return;

  const input   = document.getElementById('msg');
  const sendBtn = document.getElementById('sendBtn');
  const text    = input.value.trim();
  if (!text) return;

  // Track state
  isSending = true;
  if (history.length === 0 && !savedFirstMsg) savedFirstMsg = text;
  lastPrompt = text;

  // Update UI
  appendMessage(text, 'user');
  input.value = '';
  input.disabled = true;
  sendBtn.disabled = true;
  sendBtn.classList.add('loading');
  sendBtn.textContent = '⟳';

  showTyping();

  // Close sidebar on mobile when sending
  if (window.innerWidth < 600) closeSidebar();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: history })
    });

    // FIX: handle non-ok HTTP responses
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.reply || `Server error ${res.status}`);
    }

    const data = await res.json();
    hideTyping();

    // Update history (keep rolling window of 20 messages)
    history.push({ role: 'user', content: text });
    history.push({ role: 'assistant', content: data.reply });
    if (history.length > 20) history = history.slice(-20);

    appendMessage(data.reply, 'bot');
    if (voiceOutputOn) speakText(data.reply);

  } catch (e) {
    hideTyping();
    const errMsg = e.message && e.message !== 'Failed to fetch'
      ? `Error: ${e.message}`
      : 'Connection error. Check your API key and network, then try again.';
    appendMessage(errMsg, 'bot');
    console.error('sendMsg error:', e);
  } finally {
    // FIX: always re-enable input after request, success or failure
    isSending = false;
    input.disabled = false;
    sendBtn.disabled = false;
    sendBtn.classList.remove('loading');
    sendBtn.textContent = '➤';
    // Return focus to input for better UX
    input.focus();
  }
}

// ===================== QUICK SEND =====================
function quickSend(text) {
  if (isSending) return;
  const input = document.getElementById('msg');
  input.value = text;
  sendMsg();
}

// ===================== REGENERATE =====================
async function regenerate() {
  if (!lastPrompt || isSending) return;
  // Remove last bot+user message pair from history
  history = history.slice(0, -2);
  const input = document.getElementById('msg');
  input.value = lastPrompt;
  await sendMsg();
}

// ===================== CHAT MANAGEMENT =====================
function newChat() {
  if (history.length > 0) {
    savedHistory = [...history];
    const label = (savedFirstMsg || 'Previous chat').slice(0, 26);
    document.getElementById('hist-1-label').textContent = label + (label.length >= 26 ? '…' : '');
    document.getElementById('hist-1').style.display = 'flex';
  }
  history = []; lastPrompt = ''; savedFirstMsg = '';
  const box = document.getElementById('chatbox');
  box.innerHTML = '';
  const w = document.createElement('div');
  w.className = 'welcome'; w.id = 'welcome';
  w.innerHTML = `<div class="welcome-emoji">👋</div>
    <div class="welcome-title">New chat started!</div>
    <div class="welcome-sub">Ask me anything — I'm ready.</div>
    <div class="welcome-chips">
      <div class="chip">💡 Fun fact</div>
      <div class="chip">✍️ Write a story</div>
      <div class="chip">🤖 Explain AI</div>
    </div>`;

  // Attach chip events properly
  const chips = w.querySelectorAll('.chip');
  const chipTexts = ['Give me a fun fact', 'Help me write a short story', 'Explain AI in simple terms'];
  chips.forEach((chip, i) => {
    chip.addEventListener('click', () => quickSend(chipTexts[i]));
  });

  box.appendChild(w);
  closeSidebar();
}

function clearChat() { newChat(); showToast('Chat cleared'); }

function loadHistory() {
  if (savedHistory.length === 0) return;
  history = [...savedHistory];
  const box = document.getElementById('chatbox');
  box.innerHTML = '';
  history.forEach(m => appendMessage(m.content, m.role === 'user' ? 'user' : 'bot'));
  showToast('Previous chat loaded');
  closeSidebar();
}

// ===================== COPY =====================
function copyMsg(btn) {
  const text = btn.getAttribute('data-text');
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => showToast('Copied!'));
  } else {
    // Fallback for older browsers
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('Copied!');
  }
}

// ===================== VOICE OUTPUT =====================
function toggleVoiceOutput() {
  voiceOutputOn = !voiceOutputOn;
  const btn = document.getElementById('voiceToggle');
  btn.textContent = voiceOutputOn ? '🔊' : '🔇';
  btn.classList.toggle('active', !voiceOutputOn);
  document.getElementById('sb-voice-icon').textContent = voiceOutputOn ? '🔊' : '🔇';
  document.getElementById('sb-voice-label').textContent = voiceOutputOn ? 'Voice output on' : 'Voice output off';
  showToast(voiceOutputOn ? 'Voice output on' : 'Voice output off');
  if (!voiceOutputOn) synth.cancel();
}

function speakText(text) {
  if (synth.speaking) {
    synth.cancel();
    document.getElementById('speakingBadge').classList.remove('visible');
    return;
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1.05; utter.pitch = 1;
  const badge = document.getElementById('speakingBadge');
  utter.onstart = () => badge.classList.add('visible');
  utter.onend   = () => badge.classList.remove('visible');
  utter.onerror = () => badge.classList.remove('visible');
  synth.speak(utter);
}

// ===================== MIC / VOICE INPUT =====================
function toggleMic() { isListening ? stopMic() : startMic(); }

function startMic() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { showToast('Speech recognition not supported'); return; }
  recognition = new SR();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = false;
  recognition.onstart  = () => { isListening = true; document.getElementById('micBtn').classList.add('listening'); };
  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    document.getElementById('msg').value = transcript;
    stopMic();
    sendMsg();
  };
  recognition.onerror = () => stopMic();
  recognition.onend   = () => { if (isListening) stopMic(); };
  try { recognition.start(); } catch(e) { showToast('Mic error: ' + e.message); }
}

function stopMic() {
  isListening = false;
  document.getElementById('micBtn').classList.remove('listening');
  try { if (recognition) recognition.stop(); } catch(e) {}
}

// ===================== WAKE WORD =====================
function startWakeWordListener() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return;
  function listen() {
    wakeRecognition = new SR();
    wakeRecognition.lang = 'en-US';
    wakeRecognition.continuous = false;
    wakeRecognition.interimResults = false;
    wakeRecognition.onresult = (e) => {
      const said = e.results[0][0].transcript.toLowerCase();
      if (said.includes('hey saturday') || said.includes('saturday')) activateWake();
    };
    wakeRecognition.onend   = () => { if (!isListening) setTimeout(listen, 600); };
    wakeRecognition.onerror = () => setTimeout(listen, 2000);
    try { wakeRecognition.start(); } catch(e) {}
  }
  listen();
}

function activateWake() {
  const b = document.getElementById('wakeBadge');
  b.classList.add('visible');
  setTimeout(() => b.classList.remove('visible'), 3000);
  startMic();
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")
    history = data.get("history", [])
    try:
        reply = get_ai_response(msg, history)
        return jsonify({"reply": reply})
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"reply": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
