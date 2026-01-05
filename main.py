from pyrogram import Client, filters
import json
import os

# --- 1. إعدادات التشغيل (سحب البيانات من Koyeb) ---
# الكود الآن ذكي، سيبحث عن بياناتك في إعدادات الموقع ولن يحتاج لكتابتها هنا
try:
    api_id = int(os.environ.get("API_ID"))
    api_hash = os.environ.get("API_HASH")
    session_string = os.environ.get("SESSION_STRING")
except:
    print("⚠️ خطأ: لم يتم العثور على البيانات في متغيرات البيئة")
    print("تأكد من إضافة API_ID و API_HASH و SESSION_STRING في إعدادات Koyeb")
    exit()

if not session_string:
    print("⚠️ تنبيه: كود الجلسة (Session String) فارغ أو غير موجود!")
    exit()

# إعداد الكلاينت باستخدام كود الجلسة
app = Client("ziad_bot", api_id=api_id, api_hash=api_hash, session_string=session_string)

# --- 2. الذاكرة (قاعدة البيانات) ---
DB_FILE = "data.json"

def load_responses():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_all_responses(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. الأوامر (.اضف / .حذف) ---
@app.on_message(filters.me & filters.regex(r"^\.اضف"))
async def add_reply(client, message):
    try:
        content = message.text.replace(".اضف", "", 1).strip()
        if ":" in content:
            keyword, reply = content.split(":", 1)
            full_reply = reply.strip() + "\n\n🛒 **للشراء أرسل كلمة: شراء**\n❌ **للإلغاء أرسل كلمة: لا**"
            
            data = load_responses()
            data[keyword.strip()] = full_reply
            save_all_responses(data)
            await message.edit_text(f"✅ **تم الحفظ!**\nالكلمة: {keyword.strip()}")
        else:
            await message.edit_text("⚠️ الصيغة: `.اضف كلمة : رد`")
    except: pass

@app.on_message(filters.me & filters.regex(r"^\.حذف"))
async def delete_reply(client, message):
    keyword = message.text.replace(".حذف", "", 1).strip()
    data = load_responses()
    if keyword in data:
        del data[keyword]
        save_all_responses(data)
        await message.edit_text(f"🗑️ تم حذف: {keyword}")
    else:
        await message.edit_text("🚫 الكلمة غير موجودة.")

# --- 4. نظام الشراء والرد ---
@app.on_message(filters.private & filters.regex(r"^(شراء|1)$") & ~filters.me)
async def buy_order(client, message):
    await message.reply_text("✅ **تم تسجيل طلبك!**\nسنتواصل معك قريباً.")
    sender = message.from_user
    notify = f"🚨 **طلب جديد!**\n👤: {sender.first_name}\n🆔: `{sender.id}`\n💳: ضغط شراء"
    await client.send_message("me", notify)

@app.on_message(filters.private & filters.regex(r"^(لا|الغاء|إلغاء|2)$") & ~filters.me)
async def cancel_order(client, message):
    await message.reply_text("👌 ولا يهمك، نورتنا في أي وقت!")
    sender = message.from_user
    notify = f"⚠️ **تنبيه:** العميل {sender.first_name} ضغط على (عدم الشراء)."
    await client.send_message("me", notify)

@app.on_message(filters.private & ~filters.me)
async def auto_reply(client, message):
    data = load_responses()
    text = message.text.strip()
    # تأكدنا أنه لا يكتب أمر شراء
    if text not in ["شراء", "1", "لا", "الغاء"] and text in data:
        await message.reply_text(data[text])

# --- التشغيل ---
print("🚀 البوت يعمل الآن على Koyeb...")
app.run()
