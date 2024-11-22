from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in users and users[user_id].get("active"):
        await update.message.reply_text("أهلاً بك! يمكنك الآن استخدام البوت للنشر.")
    else:
        await update.message.reply_text(
            "مرحباً! يمكنك الاشتراك لاستخدام هذا البوت. "
            "استخدم الأمر /buy لمعرفة كيفية الدفع."
        )

# عرض معلومات الدفع
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "للاشتراك، قم بالدفع عبر PayPal على الرابط التالي:\n"
        "https://paypal.me/YourPayPalLink\n"
        "ثم أرسل إيصال الدفع إلى المشرف لتفعيل حسابك."
    )

# تفعيل الاشتراك يدويًا
async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == 123456789:  # ضع هنا معرف (ID) حسابك كمشرف
        try:
            user_id = context.args[0]
            users[user_id] = {"active": True}
            save_users()
            await update.message.reply_text(f"تم تفعيل الاشتراك للمستخدم {user_id}.")
        except IndexError:
            await update.message.reply_text("استخدام: /activate <user_id>")
    else:
        await update.message.reply_text("هذا الأمر مخصص للمشرف فقط.")

# نشر الرسائل
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in users and users[user_id].get("active"):
        message = update.message.text
        for chat_id in users[user_id].get("groups", []):
            try:
                await context.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                await update.message.reply_text(f"فشل الإرسال إلى المجموعة: {e}")
    else:
        await update.message.reply_text("لا تملك صلاحية النشر. يرجى الاشتراك أولاً.")

# إضافة مجموعة للمستخدم
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in users and users[user_id].get("active"):
        chat_id = update.effective_chat.id
        if "groups" not in users[user_id]:
            users[user_id]["groups"] = []
        if chat_id not in users[user_id]["groups"]:
            users[user_id]["groups"].append(chat_id)
            save_users()
            await update.message.reply_text("تمت إضافة المجموعة بنجاح.")
        else:
            await update.message.reply_text("هذه المجموعة مضافة بالفعل.")
    else:
        await update.message.reply_text("لا تملك صلاحية إضافة مجموعات. يرجى الاشتراك أولاً.")

# إعداد البوت
def main():
    global users
    users = load_users()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("activate", activate))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, add_group))

    application.run_polling()

if name == "main":
    main()
