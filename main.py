import os
import threading
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

def run_bot():
    subprocess.run(["python", "bot.py"])

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
