from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json

# توكن البوت
BOT_TOKEN = "7888513971:AAES9IDSLFsLYdoiaFdvftJBi8SOG8DjmLg"

# قاعدة بيانات المستخدمين
users = {}

# حفظ بيانات المستخدمين
def save_users():
    with open("users.json", "w") as file:
        json.dump(users, file)

# تحميل بيانات المستخدمين
def load_users():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# بدء المحادثة
def start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id in users and users[user_id]["active"]:
        update.message.reply_text("أهلاً بك! يمكنك الآن استخدام البوت للنشر.")
    else:
        update.message.reply_text(
            "مرحباً! يمكنك الاشتراك لاستخدام هذا البوت. "
            "استخدم الأمر /buy لمعرفة كيفية الدفع."
        )

# عرض معلومات الدفع
def buy(update: Update, context: CallbackContext):
    update.message.reply_text(
        "للاشتراك، قم بالدفع عبر PayPal على الرابط التالي:\n"
        "https://paypal.me/YourPayPalLink\n"
        "ثم أرسل إيصال الدفع إلى المشرف لتفعيل حسابك."
    )

# تفعيل الاشتراك يدويًا
def activate(update: Update, context: CallbackContext):
    if update.message.from_user.id == 123456789:  # ضع هنا معرف (ID) حسابك كمشرف
        try:
            user_id = context.args[0]
            users[user_id] = {"active": True}
            save_users()
            update.message.reply_text(f"تم تفعيل الاشتراك للمستخدم {user_id}.")
        except IndexError:
            update.message.reply_text("استخدام: /activate <user_id>")
    else:
        update.message.reply_text("هذا الأمر مخصص للمشرف فقط.")

# نشر الرسائل
def broadcast(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id in users and users[user_id]["active"]:
        message = update.message.text
        for chat_id in users[user_id]["groups"]:
            try:
                context.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                update.message.reply_text(f"فشل الإرسال إلى المجموعة: {e}")
    else:
        update.message.reply_text("لا تملك صلاحية النشر. يرجى الاشتراك أولاً.")

# إضافة مجموعة للمستخدم
def add_group(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id in users and users[user_id]["active"]:
        chat_id = update.message.chat_id
        if "groups" not in users[user_id]:
            users[user_id]["groups"] = []
        if chat_id not in users[user_id]["groups"]:
            users[user_id]["groups"].append(chat_id)
            save_users()
            update.message.reply_text("تمت إضافة المجموعة بنجاح.")
        else:
            update.message.reply_text("هذه المجموعة مضافة بالفعل.")
    else:
        update.message.reply_text("لا تملك صلاحية إضافة مجموعات. يرجى الاشتراك أولاً.")

# إعداد البوت
def main():
    global users
    users = load_users()

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("buy", buy))
    dispatcher.add_handler(CommandHandler("activate", activate))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, broadcast))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, add_group))

    updater.start_polling()
    updater.idle()

if name == "__main__":
    main()
