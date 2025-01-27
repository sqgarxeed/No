import telebot
import datetime
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Replace with your Telegram bot token
bot = telebot.TeleBot('8018452264:AAEGFJekVzKvP-vnowxCry8zYBWfQCJfSFY')

# Admin user IDs
admin_id = ["6442837812"]

# File to store allowed users and their expiration times
USER_ACCESS_FILE = "user_access.txt"

# Dictionary to store user access information (user_id: expiration_date)
user_access = {}

# Track active attacks
active_attacks = []

# Dictionary to track the last attack time for each user
user_last_attack_time = {}

# Dictionary to store attack limits (user_id: max_attack_duration)
attack_limits = {}

# Ensure the access file exists
if not os.path.exists(USER_ACCESS_FILE):
    open(USER_ACCESS_FILE, "w").close()

# Load user access information from file
def load_user_access():
    try:
        with open(USER_ACCESS_FILE, "r") as file:
            access = {}
            for line in file:
                user_id, expiration = line.strip().split(",")
                access[user_id] = datetime.datetime.fromisoformat(expiration)
            return access
    except FileNotFoundError:
        return {}
    except ValueError as e:
        logging.error(f"Error loading user access file: {e}")
        return {}

# Save user access information to file
def save_user_access():
    temp_file = f"{USER_ACCESS_FILE}.tmp"
    try:
        with open(temp_file, "w") as file:
            for user_id, expiration in user_access.items():
                file.write(f"{user_id},{expiration.isoformat()}\n")
        os.replace(temp_file, USER_ACCESS_FILE)
    except Exception as e:
        logging.error(f"Error saving user access file: {e}")

# Load access information on startup
user_access = load_user_access()

# Command: /start
@bot.message_handler(commands=['start'])
def start_command(message):
    logging.info("Start command received")
    welcome_message = """
    🌟 Welcome to the **Lightning DDoS Bot**! 🌟

    ⚡️ With this bot, you can:
    - Check your subscription status.
    - Simulate powerful attacks responsibly.
    - Manage access and commands efficiently.

    🚀 Use `/help` to see the available commands and get started!

    🛡️ For assistance, contact [@wtf_vai](https://t.me/wtf_vai).

    **Note:** Unauthorized access is prohibited. Contact an admin if you need access.
    """
    bot.reply_to(message, welcome_message, parse_mode='Markdown')

# Command: /bgmi
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    logging.info("BGMI command received")
    global active_attacks
    user_id = str(message.from_user.id)

    # Check if the user is authorized
    if user_id not in user_access or user_access[user_id] < datetime.datetime.now():
        bot.reply_to(message, "❌ You are not authorized to use this bot or your access has expired. Please contact an admin.")
        return

    # Remove completed attacks
    active_attacks = [attack for attack in active_attacks if attack['end_time'] > datetime.datetime.now()]

    # Check for cooldown
    if user_id in user_last_attack_time:
        last_attack_time = user_last_attack_time[user_id]
        time_since_last_attack = (datetime.datetime.now() - last_attack_time).total_seconds()
        if time_since_last_attack < 120:  # 120 seconds cooldown
            remaining_time = 120 - int(time_since_last_attack)
            bot.reply_to(message, f"⚠️ You must wait {remaining_time} more seconds before launching another attack.")
            return

    # Parse command
    command = message.text.split()
    if len(command) != 4 or not command[3].isdigit():
        bot.reply_to(message, "Invalid format! Use: `/bgmi <target> <port> <duration>`", parse_mode='Markdown')
        return

    target, port, duration = command[1], command[2], int(command[3])

    # Validate port
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        bot.reply_to(message, "Invalid port! Please provide a port number between 1 and 65535.")
        return

    # Check attack duration limit
    if user_id in attack_limits and duration > attack_limits[user_id]:
        bot.reply_to(message, f"⚠️ You can only launch attacks up to {attack_limits[user_id]} seconds.")
        return

    # Escape dynamic values
    target = target.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")
    port = port.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")

    # Add attack to active attacks
    attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    active_attacks.append({
        'user_id': user_id,
        'target': target,
        'port': port,
        'end_time': attack_end_time
    })

    user_last_attack_time[user_id] = datetime.datetime.now()

    attack_message = f"""
    ⚡️🔥 𝐀𝐓𝐓𝐀𝐂𝐊 𝐃𝐄𝐏𝐋𝐎𝐘𝐄𝐃 🔥⚡️

    👑 **Commander**: `{user_id}`
    🎯 **Target Locked**: `{target}`
    📡 **Port Engaged**: `{port}`
    ⏳ **Duration**: `{duration} seconds`
    ⚔️ **Weapon**: `BGMI Protocol`

    🔥 **The wrath is unleashed. May the network shatter!** 🔥
    """
    try:
        bot.send_message(message.chat.id, attack_message, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(f"Telegram API error: {e}")
        bot.reply_to(message, "🚨 Failed to deploy the attack. Please check your parameters.")

# Command: /when
@bot.message_handler(commands=['when'])
def when_command(message):
    logging.info("When command received")
    global active_attacks
    active_attacks = [attack for attack in active_attacks if attack['end_time'] > datetime.datetime.now()]

    if not active_attacks:
        bot.reply_to(message, "No attacks are currently in progress.")
        return

    active_attack_message = "Current active attacks:\n"
    for attack in active_attacks:
        target = attack['target']
        port = attack['port']
        time_remaining = max((attack['end_time'] - datetime.datetime.now()).total_seconds(), 0)
        active_attack_message += f"🌐 Target: `{target}`, 📡 Port: `{port}`, ⏳ Remaining Time: {int(time_remaining)} seconds\n"

    bot.reply_to(message, active_attack_message)

# Command: /help
@bot.message_handler(commands=['help'])
def help_command(message):
    logging.info("Help command received")
    help_text = """
    🚀 **Available Commands:**
    - **/start** - 🎉 Get started with a warm welcome message!
    - **/help** - 📖 Discover all the amazing things this bot can do for you!
    - **/bgmi <target> <port> <duration>** - ⚡ Launch an attack.
    - **/when** - ⏳ Check the remaining time for current attacks.
    - **/grant <user_id> <days>** - Grant user access (Admin only).
    - **/revoke <user_id>** - Revoke user access (Admin only).
    - **/attack_limit <user_id> <max_duration>** - Set max attack duration (Admin only).

    📋 **Usage Notes:**
    - 🔄 Replace `<user_id>`, `<target>`, `<port>`, and `<duration>` with the appropriate values.
    - 📞 Need help? Contact an admin for permissions or support – they're here to assist!
    """.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")
    try:
        bot.reply_to(message, help_text, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
        logging.error(f"Telegram API error: {e}")
        bot.reply_to(message, "🚨 An error occurred while processing your request. Please try again later.")

# Command: /grant <user_id> <days>
@bot.message_handler(commands=['grant'])
def grant_command(message):
    logging.info("Grant command received")
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    # Parse the command
    command = message.text.split()
    if len(command) != 3 or not command[2].isdigit():
        bot.reply_to(message, "Invalid format! Use: `/grant <user_id> <days>`")
        return

    user_id, days = command[1], int(command[2])

    # Set expiration date
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=days)
    user_access[user_id] = expiration_date

    save_user_access()

    bot.reply_to(message, f"✅ User {user_id} granted access until {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}.")

# Command: /revoke <user_id>
@bot.message_handler(commands=['revoke'])
def revoke_command(message):
    logging.info("Revoke command received")
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    # Parse the command
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Invalid format! Use: `/revoke <user_id>`")
        return

    user_id = command[1]

    # Revoke access
    if user_id in user_access:
        del user_access[user_id]
        save_user_access()
        bot.reply_to(message, f"✅ User {user_id} access has been revoked.")
    else:
        bot.reply_to(message, f"❌ User {user_id} does not have access.")

# Command: /attack_limit <user_id> <max_duration>
@bot.message_handler(commands=['attack_limit'])
def attack_limit_command(message):
    logging.info("Attack limit command received")
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    # Parse the command
    command = message.text.split()
    if len(command) != 3 or not command[2].isdigit():
        bot.reply_to(message, "Invalid format! Use: `/attack_limit <user_id> <max_duration>`")
        return

    user_id, max_duration = command[1], int(command[2])

    # Set attack limit
    attack_limits[user_id] = max_duration

    bot.reply_to(message, f"✅ User {user_id} can now launch attacks up to {max_duration} seconds.")

# Polling with retry logic
while True:
    try:
        bot.polling(none_stop=True, interval=0, allowed_updates=["message"])
    except Exception as e:
        logging.error(f"Polling error: {e}")
        time.sleep(5)
