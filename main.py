from pyrogram import Client, filters
from flask import Flask
from threading import Thread
import json
import os

# --- 1. سيرفر وهمي (عشان الاستضافة متفصلش) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "<b>Ziad Userbot is Running!</b>"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- 2. إعدادات الحساب (تم التعديل للأمان) ---
# الكود هنا هيجيب البيانات من إعدادات موقع Render مش من الملف
# عشان لما ترفعه على GitHub محدش يشوف أرقامك السرية
try:
    api_id = int(os.environ.get("API_ID"))
    api_hash = os.environ.get("API_HASH")
except:
    print("⚠️ خطأ: لم يتم العثور على API_ID أو API_HASH في متغيرات البيئة.")
    # لو بتجرب على جهازك ومحتاج تشغله، ممكن تكتب الأرقام هنا مؤقتاً
    # بس متنساش تمسحهم قبل الرفع!

app = Client("my_account_session", api_id=api_id, api_hash=api_hash)

# --- 3. الذاكرة (قاعدة البيانات) ---
DB_FILE = "data.json"

def load_responses():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_all_responses(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. أوامر التحكم (.اضف / .حذف) ---
@app.on_message(filters.me & filters.regex(r"^\.اضف"))
async def add_reply(client, message):
    try:
        content = message.text.replace(".اضف", "", 1).strip()
        if ":" in content:
            keyword, reply = content.split(":", 1)
            # إضافة جملة التوجيه تلقائياً للرد
            full_reply = reply.strip() + "\n\n🛒 **للشراء أرسل كلمة: شراء**\n❌ **للإلغاء أرسل كلمة: لا**"
            
            data = load_responses()
            data[keyword.strip()] = full_reply
            save_all_responses(data)
            await message.edit_text(f"✅ **تم الحفظ بذكاء!**\nأي حد هيقول ({keyword.strip()}) هيظهرله الرد وخيارات الشراء.")
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

# --- 5. نظام الشراء الذكي ---

# لو العميل قال "شراء"
@app.on_message(filters.private & filters.regex(r"^(شراء|1)$") & ~filters.me)
async def buy_order(client, message):
    # 1. رد على العميل
    await message.reply_text("✅ **تم تسجيل طلبك بنجاح!**\nسيقوم أحد ممثلي خدمة العملاء بالتواصل معك قريباً لإتمام العملية.")
    
    # 2. إشعار ليك أنت (في الرسائل المحفوظة)
    sender_name = message.from_user.first_name
    sender_link = f"tg://user?id={message.from_user.id}"
    notification = (
        f"🚨 **إشعار طلب جديد!** 🚨\n\n"
        f"👤 العميل: [{sender_name}]({sender_link})\n"
        f"💳 الحالة: **ضغط على شراء**\n"
        f"💬 شات العميل: اضغط هنا للدخول"
    )
    # يبعتلك الإشعار في "Saved Messages"
    await client.send_message("me", notification)

# لو العميل قال "لا" أو "إلغاء"
@app.on_message(filters.private & filters.regex(r"^(لا|الغاء|إلغاء|2)$") & ~filters.me)
async def cancel_order(client, message):
    await message.reply_text("👌 ولا يهمك، نورتنا في أي وقت!")
    
    # إشعار ليك برضه 
    sender_name = message.from_user.first_name
    notification = f"⚠️ **تنبيه:** العميل {sender_name} ضغط على (عدم الشراء)."
    await client.send_message("me", notification)

# --- 6. الرد التلقائي العادي ---
@app.on_message(filters.private & ~filters.me)
async def auto_reply(client, message):
    data = load_responses()
    text = message.text.strip()
    # نتأكد إنه مش بيكتب أمر شراء عشان منردش مرتين
    if text not in ["شراء", "1", "لا", "الغاء"] and text in data:
        await message.reply_text(data[text])

# --- التشغيل ---
keep_alive()
print("🚀 جاري الاتصال بالسيرفر...")
app.run()