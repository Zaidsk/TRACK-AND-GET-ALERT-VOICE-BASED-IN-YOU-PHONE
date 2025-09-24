cat > ~/status_nagger.py << 'PY'
#!/usr/bin/env python3
import subprocess, sys, os, csv, datetime, json, shutil, pathlib

HOME = str(pathlib.Path.home())
LOG_CSV = os.path.join(HOME, "progress_log.csv")

TASK_NAME = os.getenv("TASK_NAME", "Top priority task")
QUESTIONS = [
    "Pichle time block me kya progress hua?",
    "Koi blocker? (Haan/Na + short note)",
    "Next time block me exact kya karoge?"
]

def have(cmd):
    return shutil.which(cmd) is not None

def termux_tts(text):
    if have("termux-tts-speak"):
        subprocess.run(["termux-tts-speak", text])

def termux_dialog_text(title, hint="Type here..."):
    if not have("termux-dialog"):
        return ""
    proc = subprocess.run(
        ["termux-dialog", "-t", title, "-i", hint],
        capture_output=True, text=True
    )
    try:
        data = json.loads(proc.stdout.strip() or "{}")
        return data.get("text", "")
    except Exception:
        return ""

def termux_notify(title, text):
    if have("termux-notification"):
        subprocess.run(["termux-notification", "--title", title, "--content", text])

def ensure_csv():
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "task", "q1_progress", "q2_blockers", "q3_next"])

def main():
    ensure_csv()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Voice + notification
    termux_tts(f"Zaid, check-in time! {TASK_NAME} ka status do.")
    termux_notify("Status Check-in", f"{TASK_NAME}: Teen sawaal ka jawab do.")

    # Ask questions
    answers = []
    for q in QUESTIONS:
        ans = termux_dialog_text(TASK_NAME, q).strip()
        if not ans:
            termux_tts(q)
        answers.append(ans)

    # Save to CSV
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([now, TASK_NAME] + answers)

    # Wrap up
    termux_tts("Thanks! Status saved. Keep going.")
    termux_notify("Logged ✅", f"{now}\n{TASK_NAME}\nSaved to progress_log.csv")

if __name__ == "__main__":
    need = ["termux-tts-speak", "termux-dialog", "termux-notification"]
    missing = [c for c in need if not have(c)]
    if missing:
        print("Missing:", ", ".join(missing))
        sys.exit(1)
    main()
PY
chmod +x ~/status_nagger.py
