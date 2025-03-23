from telebot import types
import telebot
import sqlite3

bot = telebot.TeleBot('Your_API_TOKEN')


user_data = {}



def create_table_if_not_exists():
    try:
        conn = sqlite3.connect('check.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                user_id INTEGER UNIQUE
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")


create_table_if_not_exists()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if check_user_id_in_db(user_id):
        bot.send_message(user_id, "You are already registered! You can continue working with the bot.")
    else:
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="Registration", callback_data="button1")
        button2 = types.InlineKeyboardButton(text="Login", callback_data="button2")
        keyboard.add(button1)
        keyboard.add(button2)
        bot.send_message(user_id, "Select a login method", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "button1":
        msg = bot.send_message(call.from_user.id, "Okay, create yourself a nickname.")
        bot.register_next_step_handler(msg, process_username)
        
    elif call.data == "button2":
        msg = bot.send_message(call.from_user.id, "Ok, enter your nickname")
        bot.register_next_step_handler(msg, process_login_username)

def process_username(message):
    try:
        username = message.text.strip()
        if check_user_in_db(username):
            bot.send_message(message.chat.id, 'This nickname is already taken!')
            return start(message)
            
        user_data[message.chat.id] = {'username': username}
        msg = bot.send_message(message.chat.id, 'Now create a password')
        bot.register_next_step_handler(msg, process_password)
        
    except Exception as e:
        print(e)
        bot.reply_to(message, 'An error has occurred!')

def process_password(message):
    try:
        password = message.text  
        username = user_data[message.chat.id]['username']
        user_id = message.chat.id
        reg(username, password, user_id)
        bot.send_message(message.chat.id, 'You have registered successfully!')
        del user_data[message.chat.id]
        
    except Exception as e:
        print(e)
        bot.reply_to(message, 'An error has occurred!')

def process_login_username(message):
    try:
        username = message.text.strip()
        if not check_user_in_db(username):
            bot.send_message(message.chat.id, 'User not found!')
            return start(message)
            
        user_data[message.chat.id] = {'username': username}
        msg = bot.send_message(message.chat.id, 'Enter your password')
        bot.register_next_step_handler(msg, process_login_password)
        
    except Exception as e:
        print(e)
        bot.reply_to(message, 'An error has occurred!')

def process_login_password(message):
    try:
        password = message.text.strip()
        username = user_data[message.chat.id]['username']
        
        if check_password(username, password):
            user_id = message.chat.id
            update_user_id_in_db(username, user_id)
            bot.send_message(message.chat.id, 'Successful login!')
        else:
            bot.send_message(message.chat.id, 'Incorrect password!')
            
        del user_data[message.chat.id]
        
    except Exception as e:
        print(e)
        bot.reply_to(message, 'An error has occurred!')


############################################################################################################
############################################################################################################
############################################################################################################
                                               #Working with DB#

def reg(username, password, user_id):
    try:
        conn = sqlite3.connect('check.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password, user_id) VALUES(?,?,?)", (username, password, user_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)


############################################################################################################ 
def check_user_in_db(username):
    try:
        conn = sqlite3.connect('check.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        return bool(result)
    except Exception as e:
        print(e)
        return False

def check_password(username, password):
    try:
        conn = sqlite3.connect('check.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password))
        result = cursor.fetchone()
        conn.close()
        return bool(result)
    except Exception as e:
        print(e)
        return False

def check_user_id_in_db(user_id):
    try:
        conn = sqlite3.connect('check.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return bool(result)
    except Exception as e:
        print(e)
        return False

############################################################################################################

def update_user_id_in_db(username, user_id):
    try:
        conn = sqlite3.connect('check.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET user_id = ? WHERE username = ?', (user_id, username))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)

############################################################################################################
############################################################################################################
############################################################################################################

if __name__ == '__main__':
    bot.polling()
