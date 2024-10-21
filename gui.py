import re
import time
import customtkinter as ctk
import subprocess
import os
import json
import psutil
from dotenv import load_dotenv
from tkinter import messagebox
from datetime import datetime

load_dotenv()


def load_json(filename) -> dict:
    """Load data from a JSON file."""
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return {}


def save_json(filename, data) -> None:
    """Save data to a JSON file."""
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving {filename}: {e}")


def terminate_bot_processes() -> None:
    """checks/Terminates any existing bot processes."""
    current_directory = os.getcwd()

    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            if (
                proc.info["name"] in ["python", "python3"]
                and "main.py" in proc.info["cmdline"]
            ):
                if proc.info["exe"] and current_directory in proc.info["exe"]:
                    print(
                        f"Terminating process: {proc.info['pid']}, {proc.info['cmdline']}"
                    )
                    proc.terminate()
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def start_bot() -> None:
    """Starts the bot"""
    if not check_settings():
        return

    try:
        terminate_bot_processes()
        log_file = open("bot_log.log", "a")

        global bot_start_time
        bot_start_time = datetime.now()

        process = subprocess.Popen(
            ["python3", "main.py"],
            cwd=os.getcwd(),
            env=os.environ.copy(),
            stdout=log_file,
            stderr=log_file,
        )

        messagebox.showinfo("Success", "Bot started.")
        time.sleep(3)
        root.after(500, update_bot_username)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to start the bot: {str(e)}")


def save_settings() -> None:
    """Save the current settings."""
    try:
        api_key = api_key_entry.get()
        username = username_entry.get()
        shock_code = shock_code_entry.get()
        token = token_entry.get()

        with open(".env", "w") as f:
            f.write(f"SHOCKER_APIKEY={api_key}\n")
            f.write(f"SHOCKER_USERNAME={username}\n")
            f.write(f"SHOCKER_CODE={shock_code}\n")
            f.write(f"TOKEN={token}\n")

        whitelist_data = {
            "whitelist": [
                int(user_id.strip()) for user_id in whitelist_entry.get().split(",")
            ]
        }
        wordlist_data = {
            "words": [word.strip() for word in wordlist_entry.get().split(",")]
        }

        save_json("whitelist.json", whitelist_data)
        save_json("wordlist.json", wordlist_data)

        messagebox.showinfo("Success", "Settings saved successfully!")

    except Exception as e:
        custom_error(f"Failed to save settings: {str(e)}")


def custom_error(message: str) -> None:
    """displays the custom error"""
    error_popup = ctk.CTkToplevel()
    error_popup.title("Error")
    error_popup.geometry("300x200")
    error_popup.resizable(False, False)
    error_popup.configure(bg_color="#FF4C4C")

    label = ctk.CTkLabel(
        error_popup,
        text=message,
        text_color="white",
        font=("Arial", 14, "bold"),
        width=400,
    )
    label.pack(pady=30)

    close_button = ctk.CTkButton(
        error_popup,
        text="Close",
        command=error_popup.destroy,
        fg_color="#FF1C1C",
        hover_color="#FF4040",
        width=120,
        height=40,
        corner_radius=10,
        font=("Arial", 12, "bold"),
    )
    close_button.pack(pady=10)

    error_popup.mainloop()


def check_settings() -> bool:
    """checks if all required settings are filled out."""
    if not all(
        [
            api_key_entry.get(),
            username_entry.get(),
            shock_code_entry.get(),
            token_entry.get(),
        ]
    ):
        custom_error("Please fill out all the settings.")
        return False
    return True


def autofill_settings() -> None:
    """Autofill the settings."""
    api_key = os.getenv("SHOCKER_APIKEY")
    username = os.getenv("SHOCKER_USERNAME")
    shock_code = os.getenv("SHOCKER_CODE")
    token = os.getenv("TOKEN")

    whitelist_data = load_json("whitelist.json")
    wordlist_data = load_json("wordlist.json")

    api_key_entry.insert(0, api_key or "")
    username_entry.insert(0, username or "")
    shock_code_entry.insert(0, shock_code or "")
    token_entry.insert(0, token or "")

    if "whitelist" in whitelist_data:
        whitelist_entry.insert(
            0, ", ".join(str(user_id) for user_id in whitelist_data["whitelist"])
        )
    if "words" in wordlist_data:
        wordlist_entry.insert(0, ", ".join(wordlist_data["words"]))


def update_bot_username() -> None:
    """Update the bot's username on login"""
    with open("bot_log.log", "r") as log_file:
        log_lines = log_file.readlines()
    # hacky but eh
    bot_username = None
    for line in reversed(log_lines):
        match = re.search(r"Logged on as (\S+#\d+)", line)
        if match:
            bot_username = match.group(1)
            break

    if bot_username:
        bot_username_label.configure(text=f"Logged in as: {bot_username}")
        return

    root.after(1200, update_bot_username)


def update_uptime() -> None:
    """Update the bot's uptime."""
    if "bot_start_time" in globals():
        elapsed_time = datetime.now() - bot_start_time
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{elapsed_time.days}d {hours}h {minutes}m {seconds}s"
        uptime_label.configure(text=f"Uptime: {uptime}")

    root.after(1000, update_uptime)  # Updates every second


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


root = ctk.CTk()
root.title("PiShock SB Settings")
root.geometry("400x380")
root.resizable(True, False)


bot_username_label = ctk.CTkLabel(root, text="Bot Username: waiting...", anchor="w")
bot_username_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

uptime_label = ctk.CTkLabel(root, text="Uptime: 0d 0h 0m 0s", anchor="w")
uptime_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

api_key_label = ctk.CTkLabel(root, text="API Key:")
api_key_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
api_key_entry = ctk.CTkEntry(root)
api_key_entry.grid(row=2, column=1, padx=10, pady=5)

username_label = ctk.CTkLabel(root, text="Username:")
username_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
username_entry = ctk.CTkEntry(root)
username_entry.grid(row=3, column=1, padx=10, pady=5)

shock_code_label = ctk.CTkLabel(root, text="Shock Code:")
shock_code_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
shock_code_entry = ctk.CTkEntry(root)
shock_code_entry.grid(row=4, column=1, padx=10, pady=5)

token_label = ctk.CTkLabel(root, text="Discord Token:")
token_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
token_entry = ctk.CTkEntry(root)
token_entry.grid(row=5, column=1, padx=10, pady=5)

whitelist_label = ctk.CTkLabel(root, text="Whitelist (comma-separated IDs):")
whitelist_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
whitelist_entry = ctk.CTkEntry(root)
whitelist_entry.grid(row=6, column=1, padx=10, pady=5)

wordlist_label = ctk.CTkLabel(root, text="Wordlist (comma-separated words):")
wordlist_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
wordlist_entry = ctk.CTkEntry(root)
wordlist_entry.grid(row=7, column=1, padx=10, pady=5)

start_button = ctk.CTkButton(root, text="Start Bot", command=start_bot)
start_button.grid(row=8, column=0, padx=10, pady=5)

save_button = ctk.CTkButton(root, text="Save Settings", command=save_settings)
save_button.grid(row=8, column=1, padx=10, pady=5)

autofill_button = ctk.CTkButton(
    root, text="Autofill Settings", command=autofill_settings
)
autofill_button.grid(row=9, column=0, padx=10, pady=5, columnspan=2)

root.after(1000, update_uptime)
autofill_settings()  # Autofill settings on start
root.mainloop()
