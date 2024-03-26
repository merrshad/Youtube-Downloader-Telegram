import telebot
from telebot import types
from pytube import YouTube
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import requests
import sqlite3


conn = sqlite3.connect('users.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY)''')
                  
cursor.execute('''ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0''')

conn.commit()
conn.close()

token = 'Your-Bot-Token'

channel_id = -1243423432 # ایدی عددی کانالی که قرا است رربات ممبر های عضو شده یا نشده را چک کند 
channel_join = -123456789  # ایدی عددی کانالی که ربات وقتی کاربری ربات را استارت کرد یک اعلان در کانال ارسال کند


bot = telebot.TeleBot(token)

# تابع بررسی وجود کاربر در دیتابیس
def is_user_exist(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# تابع افزودن کاربر به دیتابیس
def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    
    
@bot.message_handler(commands=['start'])
def handle_start(message):
    # بررسی عضویت کاربر در کانال
    user_id = message.from_user.id
    is_member = check_membership(user_id, channel_id)
    
    if is_member:
        if not is_user_exist(user_id):
            add_user(user_id)
        else:    
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
            button1 = KeyboardButton('دانلود از یوتیوب')
            button2 = KeyboardButton('پشتیبانی')
            keyboard.add(button1, button2)
            bot.send_message(message.chat.id, f""" سلام  {message.from_user.first_name}  به ربات یوتیوب دانلودر خوش آمدی♥️

    لینک ویدیوی یوتیوبتو برام بفرس و سریع تحویل بگیر ⚡️

    🦧 برای شروع یکی از گزینه های زیر رو انتخاب کن :""", reply_markup=keyboard)
            
            bot.send_message(channel_join, f"کاربر جدید با نام {message.from_user.first_name} عضو ربات شد.")

    else:
        bot.send_message(message.chat.id, """کاربر گرامی لطفا برای استفاده از ربات ، ابتدا در کانال زیر عضو شوید 👀 
🆔 @newpacks

و سپس دوباره دستور   /start را ارسال کنید. """)
        
        


    
    
# بررسی عضویت کاربر در کانال
def check_membership(user_id, channel_id):
    try:
        member = bot.get_chat_member(channel_id, user_id)
        if member.status == 'left':
            return False
        else:
            return True
        
    except telebot.apihelper.ApiException as e:
        if e.result_json['description'] == 'Bad Request : chat not found':
         return False
    
  
# تابع ارسال پیام به تمام کاربران
        #این تابع به دلیل استفاده خیلی به کامنت تبدیل شده است برای استفاده فقط کافی است تا از حالت کامنت در بیاید

"""def send_message_to_all_users(message_text):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0")  # فقط کاربرانی که بلاک نشده‌اند
    user_ids = cursor.fetchall()
    conn.close()
    
    for user_id in user_ids:
        try:
            # بررسی عضویت کاربر در کانال
            member = bot.get_chat_member(channel_id, user_id[0])
            if member.status != 'left':
                bot.send_message(user_id[0], message_text)
        except Exception as e:
            print(f"Error occurred while sending message to user {user_id[0]}: {e}")

# مثال استفاده از تابع
send_message_to_all_users("ربات آپدیت شد✅\n\n لطفا برای استفاده دوباره ربات را /start کنید.")
"""

@bot.message_handler(func=lambda message: message.text == "دانلود از یوتیوب")
def handle_download_button(message):
    is_member = check_membership(message.from_user.id, channel_id)
    if is_member:
        bot.reply_to(message, "لطفاً لینک ویدیوی YouTube را ارسال کنید.📬")
    else:
        bot.send_message(message.chat.id, 'شما باید عضو کانال ما باشید تا بتوانید از این قابلیت استفاده کنید.')
        
        

@bot.message_handler(func=lambda message: message.text == "پشتیبانی")
def handle_supp_button(message):   
    bot.send_message(message.chat.id,'فعلا برقراری ارتباط با پشتیبانی مقدور نیست \n بعدا امتحان کنید😁')
        
# 
@bot.message_handler(func=lambda message: True)
def handle_video_link(message):
    try:
 
        video_url = message.text
        youtube = YouTube(video_url)
        

        # ایجاد گزینه‌های انتخاب کیفیت ویدیو
        keyboard = types.InlineKeyboardMarkup(row_width=2)
    
        status_message = bot.send_message(message.chat.id,'در حال جستجوی کیفیت های موجود برای دانلود...⏳')
        for stream in youtube.streams.filter(file_extension='mp4', progressive=True) :
                button_text = f" 🎬  {stream.resolution} - {stream.filesize / (1024 * 1024):.1f} MB"
                button = types.InlineKeyboardButton(text=button_text, callback_data=stream.itag)
                keyboard.add(button)
                
        for stream in youtube.streams.filter(file_extension='mp4', resolution='480p'):
            button_text = f"🎬  {stream.resolution} - {stream.filesize / (1024 * 1024):.1f} MB"
            button = types.InlineKeyboardButton(text=button_text, callback_data=stream.itag)
            keyboard.add(button)
            
            
        button_audio_128 = types.InlineKeyboardButton(text=" 128kbps  🎧 ", callback_data="audio_128")
        button_audio_320 = types.InlineKeyboardButton(text=" 320kbps  🎧", callback_data="audio_320")
        keyboard.add(button_audio_128, button_audio_320)    
                
        bot.delete_message(message.chat.id, status_message.message_id)  
        
        global qual_mssg
        # ارسال گزینه‌های انتخاب کیفیت به کاربر
        qual_mssg = bot.send_message(message.chat.id, 'لطفا کیفیت ویدیو رو انتخاب کن :', reply_markup=keyboard)
        
        # ذخیره لینک ویدیو
        bot.video_url = video_url

    except Exception as e:
        bot.send_message(message.chat.id, 'خطا در خطا در بارگیری ویدیو ، یک لینک معتبر ارسال کن .')

# پاسخ به انتخاب کیفیت ویدیو
@bot.callback_query_handler(func=lambda call: True)
def handle_quality_selection(call):
    try:
        video_url = bot.video_url
        youtube = YouTube(video_url)

        if call.data == "audio_128":
            # دانلود ویدیو با کیفیت انتخاب شده
            video = youtube.streams.get_by_itag(140)
            bot.delete_message(call.message.chat.id, qual_mssg.message_id)
            status_message = bot.send_message(call.message.chat.id, 'در حال دانلود فایل صوتی...')
            progress_bar = bot.send_chat_action(call.message.chat.id, 'upload_audio')

            # دانلود فایل صوتی
            audio_file = video.download()
            bot.delete_message(call.message.chat.id, status_message.message_id)
            # پاکسازی فایل موقت
            if os.path.exists(audio_file):
                caption = f"عنوان : {youtube.title}\n ناشر : {youtube.author}\n مدت زمان : {youtube.length} ثانیه\n @newpacks"
                upload_statues = bot.send_message(call.message.chat.id, 'در حال آپلود فایل صوتی...')
                time.sleep(2)
                bot.send_audio(call.message.chat.id, open(audio_file, 'rb'), caption=caption)
                bot.delete_message(call.message.chat.id, upload_statues.message_id)
                bot.send_message(call.message.chat.id, 'فایل صوتی ارسال شد✅ ')
                os.remove(audio_file)  # حذف فایل موقت پس از ارسال
            else:
                bot.send_message(call.message.chat.id, 'خطا در دانلود فایل صوتی.')
        
        elif call.data == "audio_320":
            # دانلود ویدیو با کیفیت انتخاب شده
            video = youtube.streams.get_by_itag(251)
            bot.delete_message(call.message.chat.id, qual_mssg.message_id)
            status_message = bot.send_message(call.message.chat.id, 'در حال دانلود فایل صوتی...')
            progress_bar = bot.send_chat_action(call.message.chat.id, 'upload_audio')

            # دانلود فایل صوتی
            audio_file = video.download()
            bot.delete_message(call.message.chat.id, status_message.message_id)
            # پاکسازی فایل موقت
            if os.path.exists(audio_file):
                caption = f"عنوان : {youtube.title}\n ناشر : {youtube.author}\n مدت زمان : {youtube.length} ثانیه\n @newpacks"
                upload_statues = bot.send_message(call.message.chat.id, 'در حال آپلود فایل صوتی...')
                time.sleep(2)
                bot.send_audio(call.message.chat.id, open(audio_file, 'rb'), caption=caption)
                bot.delete_message(call.message.chat.id, upload_statues.message_id)
                bot.send_message(call.message.chat.id, 'فایل صوتی ارسال شد✅ ')
                os.remove(audio_file)  # حذف فایل موقت پس از ارسال
            else:
                bot.send_message(call.message.chat.id, 'خطا در دانلود فایل صوتی.')
        
        else:
            
            # چک کردن اندازه فایل برای ویدیوهای با حجم بیشتر از 50 مگابایت
            video = youtube.streams.get_by_itag(call.data)
            file_size = video.filesize
            
            if file_size > 50 * 1024 * 1024:  # بررسی اندازه فایل (بیشتر از 50 مگابایت)
                bot.send_message(call.message.chat.id, """ متاسفانه با توجه به محدودیت های تلگرام نمیتونیم ویدیو هایی با حجم بیشتر از 50 مگابایت رو برات ارسال کنیم 😕

در تلاشیم که این محدودیت را رفع کنیم و به زودی به شما خبر میدیم ❤️
""") 
                return  # پایان فرآیند در صورت بیشتر بودن حجم فایل
            # در غیر این صورت، دانلود ویدیو با کیفیت انتخاب شده
            video = youtube.streams.get_by_itag(call.data)
            bot.delete_message(call.message.chat.id, qual_mssg.message_id)
            status_message = bot.send_message(call.message.chat.id, 'در حال دانلود ویدیو...')
            progress_bar = bot.send_chat_action(call.message.chat.id, 'upload_video')

            # دانلود فایل ویدیو
            video_file = video.download()
            
            bot.delete_message(call.message.chat.id, status_message.message_id)

            # پاکسازی فایل موقت
            if os.path.exists(video_file):
                caption = f"عنوان : {youtube.title}\n ناشر : {youtube.author}\n مدت زمان : {youtube.length} ثانیه\n @newpacks"
                upload_statues = bot.send_message(call.message.chat.id, 'در حال آپلود ویدیو...')
                time.sleep(2)
                bot.send_video(call.message.chat.id, open(video_file, 'rb'), caption=caption,supports_streaming=True)
                bot.delete_message(call.message.chat.id, upload_statues.message_id)
                bot.send_message(call.message.chat.id, 'ویدیو ارسال شد✅ ')
                os.remove(video_file)  # حذف فایل موقت پس از ارسال
            else:
                bot.send_message(call.message.chat.id, 'خطا در دانلود ویدیو.')
 
    except Exception as e:
        bot.send_message(call.message.chat.id, 'خطا در دانلود.')
           

# شروع ربات
bot.polling()