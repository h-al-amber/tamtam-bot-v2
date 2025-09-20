import sys
import re
import time
import json
import threading
import datetime
import random
import inspect
# from datetime import datetime
sys.path.append(".pythonlibs/lib/python3.11/site-packages")
# ===============  بداية متغيرات ملف حفظ الترحيب =================
from welcome_manager import WelcomeManager  # لو وضعته في ملف خارجي
welcome_manager = WelcomeManager()
# ===== تعريف الانتظار =====
waiting = {
    "welcome": {},  # لتخزين انتظار الترحيب
    "reply": {},    # لتخزين انتظار الردود
    "delete_reply": {}  # لتخزين انتظار حذف الرد
}


waiting_data = {
    "reply": {}     # لتخزين الكلمة -> الرد بعد إرسالها
}
# مصفوفة الألعاب مع الكلمات المفتاحية لكل لعبة
games = {
    "لو خيروك": ["خيرني", "لو خيروك", "اختر", "خياري"],
    "اسالة - صراحه": ["اسالة", "اساله", "أساله", "اسالني", "صارحني", "صراحه"],
    "كت": ["كت", "كت كت"]
}

# دالة لعرض الألعاب بشكل منسق
def display_games(chat_id):
    lines = ["⊰❳ - الالعاب", "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"]
    for game_name, keywords in games.items():
        main_keyword = keywords[0] if keywords else ""
        lines.append(f"⧔︙{game_name} -› {main_keyword}")
        lines.append("﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎")
    message_text = "\n".join(lines)
    bot.send_message(message_text, chat_id)


# اختبار الطباعة
# print(display_games())

# ============== بداية قاموس الاوامر ==========
COMMANDS_REQUIRED_PRIORITY = {
    # ================= أوامر المطور الأساسي (أولوية 1) =================
    "رفع مطور": 1,
    "تنزيل مطور": 1,
    "المطورين": 1,
    "مسح المطورين": 1,
    "اوامر الحماية": 1,
    "تنضيف": 1,

    # ================= أوامر المطورين (أولوية 2) =================
    "اضف رد عام": 2,
    "حذف رد عام": 2,
    "الردود العامه": 2,
    "حذف الردود العامه": 2,

    # ================= أوامر المنشئ الأساسي (أولوية 3) =================
    "رفع منشئ": 3,
    "تنزيل منشئ": 3,
    "مسح المنشئين": 3,
    "المنشئين": 3,
    "مسح رسالة": 3,
    "مسح ترحيب": 3,
    "كشف": 3,

    # ================= أوامر المنشئين (أولوية 4) =================
    "اضف ترحيب": 4,
    "تنزيل ادمن": 4,
    "الادمنية": 4,
    "مسح الادمنية": 4,

    # ================= أوامر الأدمنية (أولوية 5) =================
    "اضف أمر": 5,
    "امسح أمر": 5,
    "رفع مميز": 5,
    "تنزيل مميز": 5,
    "المميزين": 5,
    "مسح المميزين": 5,
    "طرد": 5,
    "حضر": 5,
    "تثبيت": 5,
    "الغاء التثبيت": 5,
    "تنزيل الكل": 5,
    "تنزيل و طرد": 5,
    "اضف رد": 5,
    "حذف رد": 5,
    "مسح الردود": 5,
    "الردود": 5,
    "الاعدادات": 5,  # أخذت أولوية الأدمنية لأنها الأقل رتبة بين التكرارات
}
# تعريف الرتب مع أوامرها
ROLES_COMMANDS = {
    1: ["رفع مطور", "تنزيل مطور", "المطورين", "مسح المطورين"],
    2: ["اضف رد عام", "حذف رد عام", "الردود العامه", "حذف الردود العامه"],
    3: ["رفع منشئ", "تنزيل منشئ", "مسح المنشئين", "المنشئين", "مسح ترحيب","تنضيف"],
    4: ["اضف ترحيب", "تنزيل ادمن", "الادمنية", "مسح الادمنية","رفع ادمن","طرد البوتات "],
    5: [
        "اضف أمر", "امسح أمر", "رفع مميز", "تنزيل مميز", "المميزين", "مسح المميزين",
        "طرد", "حضر", "تثبيت", "الغاء التثبيت", "تنزيل الكل", "تنزيل و طرد","الاوامر المضافة",
        "اضف رد", "حذف رد", "مسح الردود", "الردود", "الاعدادات" ,"اوامر الحماية" ,"كشف","مسح رسالة","الاوامر"
    ],
    6: [
        "الردود العامه", "الردود", "المنشئين", "المطورين", "الادمنية", "المميزين"
    ],

}

# =================== بداية الالعاب ===========
# تحميل الأسئلة من ملف خارجي
with open("cut_game_questions.json", "r", encoding="utf-8") as f:
    cut_game_data = json.load(f)

cut_game_questions = cut_game_data["cut_game_questions"]
# ================= بداية لعبة لو خيروك =====================
with open("would_you_rather_questions.json", "r", encoding="utf-8") as f:
    would_you_rather_questions_data= json.load(f)

would_you_rather_questions= would_you_rather_questions_data["would_you_rather_general"]
# ================= بداية دالة اسالة صراحه ====================
with open("truth_questions.json", "r", encoding="utf-8") as f:
    truth_questions_data= json.load(f)

truth_questions_data_questions= truth_questions_data["truth_questions"]

# ================= نهاية دالة اسئلة صراحة ====================
# =================== نهاية الالعاب =============

# ============== نهاية قاموس الاوامر ===========

# ===============نهاية متغيرات ملف حفظ الترحيب =================
# =============== بداية  استدعاء ملف الردود العامه  ==============
from reply_manager import ReplyManager
reply_manager = ReplyManager()
waiting_for_reply = {}
# =============== نهاية استدعاء ملف الردود العامه  ===============
# قاموس لتخزين حالة انتظار الترحيب لكل مجموعة
waiting_for_welcome = {}
import tambotapi
from kvsqlite.sync import Client
import sqlite3
# import sqlite3

def init_db():
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    conn.commit()
    conn.close()

init_db()

# إعداد قاعدة بيانات kvsqlite
db = Client("bot_data.sqlite")
if not db.exists("devs"):
    db.set("devs", {"ids": ['910195286440']})  # المطور الأساسي

# جداول قاعدة البيانات
def create_db_and_tables():
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    # جدول المطورين
    # cursor.execute("""
    #     INSERT OR REPLACE INTO roles 
    #     (group_id, user_id, fullname, username, role, priority, added_by_admin)
    #     VALUES (?, ?, ?, ?, 'مطور أساسي', 1, 0)
    # """, ("global", "910195286440", "حوراء", "hawrakamell"))


    # جدول أنواع الحمايات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS protections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # جدول إعدادات الحمايات للمجموعات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_protection_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            protection_id INTEGER,
            status INTEGER DEFAULT 0,
            FOREIGN KEY(protection_id) REFERENCES protections(id)
        )
    """)
    # جدول المستخدمين 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            user_id TEXT,
            username TEXT,
            fullname TEXT,
            UNIQUE(group_id, user_id)
        )
    """)
# جدول المجموعات 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            group_id TEXT PRIMARY KEY,
            activated INTEGER DEFAULT 0,     
            bot_added INTEGER DEFAULT 0,     
            added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      """)

    # أوامر الحماية - مرة واحدة فقط
    protections_list = [
        "الروابط", "البوتات", "المتحركه", "الملصقات", "الملفات",
        "الصور", "الفيديو", "الالعاب", "الدردشه", "التوجيه", "الاغاني",
        "الصوت", "الجهات", "الهمسه", "التكرار", "التاك",
        "التعديل", "الفايروس", "الكلايش", "الهايشتاك", "الترحيب",
        "الفشار", "الخصوصية", "الردود", "الكل"
    ]

    # protections_list = [
    #     "الروابط", "البوتات", "المتحركه", "الملصقات", "الملفات",
    #     "الصور", "الفيديو", "الالعاب", "الدردشه", "التوجيه", "الاغاني",
    #     "الصوت", "الجهات", "الهمسه", "التكرار", "التاك",
    #     "التعديل", "الفايروس", "الكلايش", "الهايشتاك", "الترحيب",
    #     "الفشار", "الخصوصية", "الردود",
    # "الكل"]
    for name in protections_list:
        cursor.execute("INSERT OR IGNORE INTO protections (name) VALUES (?)", (name,))

    conn.commit()
    conn.close()

conn = sqlite3.connect("bot_data.sqlite")
cursor = conn.cursor()

# إضافة العمود is_bot إذا لم يكن موجودًا مسبقًا
try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_bot INTEGER DEFAULT 0")
    print("✅ تم إضافة العمود is_bot بنجاح")
except sqlite3.OperationalError as e:
    # إذا كان العمود موجود بالفعل
    if "duplicate column name: is_bot" in str(e):
        print("ℹ️ العمود is_bot موجود مسبقًا، تم تجاهل الإضافة")
    else:
        raise e
# إضافة العمود last_notified_username
try:
    cursor.execute("ALTER TABLE users ADD COLUMN last_notified_username TEXT")
    print("✅ تم إضافة العمود last_notified_username")
except sqlite3.OperationalError as e:
    if "duplicate column name: last_notified_username" in str(e):
        print("ℹ️ العمود last_notified_username موجود مسبقًا، تم تجاهل الإضافة")
    else:
        raise e

# إضافة العمود last_notified_fullname
try:
    cursor.execute("ALTER TABLE users ADD COLUMN last_notified_fullname TEXT")
    print("✅ تم إضافة العمود last_notified_fullname")
except sqlite3.OperationalError as e:
    if "duplicate column name: last_notified_fullname" in str(e):
        print("ℹ️ العمود last_notified_fullname موجود مسبقًا، تم تجاهل الإضافة")
    else:
        raise e
conn.commit()
conn.close()

# ================بداية دالة  لانشاء جدول لاضافة المرادفات للاوامر ===============
def create_command_aliases_table():
    with sqlite3.connect("bot_data.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_command TEXT NOT NULL,
                alias TEXT NOT NULL,
                group_id TEXT NOT NULL,
                added_by TEXT,
                UNIQUE(base_command, alias, group_id)
            )
        """)
        conn.commit()

create_command_aliases_table()

create_db_and_tables()
# ================ نهاية دالة لانشء جدول لاضافة المرادفات للاوامر  ===============
# ================ بداية دالة الاوامر المضافة ===================
def handle_added_commands(update):
    chat_id = str(bot.get_chat_id(update))

    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect("bot_data.sqlite")
    cursor = conn.cursor()

    # جلب جميع الأوامر الأساسية التي لها مرادفات في المجموعة الحالية
    cursor.execute("""
        SELECT base_command, alias
        FROM command_aliases
        WHERE group_id=?
        ORDER BY base_command, id
    """, (chat_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "⚠️ لا توجد أوامر مضافة في هذه المجموعة."

    # تنظيم البيانات: الأمر الأساسي كمفتاح، والمرادفات قائمة
    commands_dict = {}
    for base_command, alias in rows:
        if base_command not in commands_dict:
            commands_dict[base_command] = []
        commands_dict[base_command].append(alias)

    # بناء النص النهائي بالزخرفة
    response_lines = ["🗂️ ⌜ الاوامر المضافة ⌟", "┉┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉┉┉"]
    for command, aliases in commands_dict.items():
        response_lines.append(f"\n💠 {command}")
        response_lines.append("┉┉┉┉┉┉┉┉┉┉")
        for alias in aliases:
            response_lines.append(f"➤ {alias}")

    return "\n".join(response_lines)

# ================ نهاية دالة الاوامر المضافة ===================


# ✅ دالة لتسجيل مجموعة جديدة أو استكمال الحمايات الناقصة
def initialize_group_protection_settings(group_id):
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    # جلب جميع أنواع الحمايات
    cursor.execute("SELECT id FROM protections")
    protection_ids = [row[0] for row in cursor.fetchall()]

    # أضف فقط التي غير موجودة
    for pid in protection_ids:
        cursor.execute("""
            SELECT 1 FROM group_protection_settings
            WHERE group_id = ? AND protection_id = ?
        """, (str(group_id), pid))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO group_protection_settings (group_id, protection_id, status)
                VALUES (?, ?, 1)
            """, (str(group_id), pid))

    conn.commit()
    conn.close()
# import sqlite3


def show_developers():
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM developers")
    rows = cursor.fetchall()

    if not rows:
        print("🟡 جدول المطورين فارغ")
    else:
        print("✅ بيانات جدول المطورين:")
        for row in rows:
            # row[0] = user_id, row[1] = name, row[2] = added_on
            print(f"user_id: {row[0]}, name: {row[1]}, added_on: {row[2]}")

    conn.close()



# دالة لإضافة مطور جديد
# def add_developer_to_db(user_id, name):
    # دالة لإضافة مطور جديد
    # دالة عامة لإضافة أي رتبة
def add_role_to_db(user_id, fullname, username="", role="عضو عادي", priority=7, group_id="global", added_by_admin=1):
    try:
        conn = sqlite3.connect("bot_data.sqlite", timeout=10)
        cursor = conn.cursor()

        # فحص إذا المستخدم موجود في نفس المجموعة
        cursor.execute("""
            SELECT role FROM roles 
            WHERE group_id = ? AND user_id = ?
        """, (group_id, str(user_id)))
        result = cursor.fetchone()

        if result:
            old_role = result[0]
            if old_role == role:
                # نفس الرتبة موجودة مسبقًا
                conn.close()
                return f"ℹ️ المستخدم مرفوع مسبقًا برتبة: {old_role}"
            else:
                # عنده رتبة مختلفة بالفعل
                conn.close()
                return f"⚠️ لا يمكن إضافة رتبة جديدة. المستخدم يمتلك بالفعل رتبة: {old_role}. يجب حذفها أولاً."

        # إذا ما عنده أي رتبة → نضيف
        cursor.execute("""
            INSERT INTO roles 
            (group_id, user_id, fullname, username, role, priority, added_by_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (group_id, str(user_id), fullname, username, role, priority, added_by_admin))

        conn.commit()
        conn.close()
        return f"✅ تمت إضافة {role} للمستخدم {fullname}"

    except Exception as e:
        print(f"❌ خطأ أثناء إضافة {role} إلى قاعدة البيانات:", e)
        return f"❌ حدث خطأ أثناء إضافة {role}"


# جدول  الرتب 
conn = sqlite3.connect("bot_data.sqlite", timeout=10)
cursor = conn.cursor()

# التأكد من وجود جدول roles
cursor.execute("""
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id TEXT,
    user_id TEXT,
    fullname TEXT,
    username TEXT,
    role TEXT,
    priority INTEGER,
    UNIQUE(group_id, user_id)
)
""")

# محاولة إضافة العمود added_by_admin إذا لم يكن موجودًا مسبقًا
try:
    cursor.execute("ALTER TABLE roles ADD COLUMN added_by_admin INTEGER DEFAULT 0")
    print("[INFO] تم إضافة العمود 'added_by_admin' بنجاح")
except sqlite3.OperationalError:
    print("[INFO] العمود 'added_by_admin' موجود مسبقًا، تم تجاهل الإضافة")

# التحقق من بنية الجدول
cursor.execute("PRAGMA table_info(roles)")
columns = cursor.fetchall()
print("=== أعمدة جدول roles ===")
for col in columns:
    print(col)

conn.commit()
conn.close()

# تعريف البوت
bot = tambotapi.TamBot("f9LHodD0cOJKPxSDIWKZr7BpTPoLOg0WLt0FTVr02tbNaEwt8egJ3UWCGefZEdp1nRIyR6pQHbUg2rvdJ0mguQ")
# ======================= بداية  جلب الuserid and text  بداية الطرق الثلاثه(ايدي - تاك - رد على رساله) ============================
# ====== دوال استخراج المستخدم المستهدف ======

def extract_user_id_from_reply(update):
    """تحقق إذا كان الأمر عن طريق الرد على رسالة، أرجع user_id إن وجد"""
    updates = update.get("updates", [])
    if not updates:
        return None
    msg = updates[0].get("message", {})
    reply_msg = msg.get("reply_to_message")
    if reply_msg:
        user_data = reply_msg.get("sender") or reply_msg.get("from") or {}
        user_id = user_data.get("user_id")
        if user_id:
            print(f"[DEBUG] تم استخراج user_id من الرد: {user_id}")
            return int(user_id)
    return None


def extract_user_id_from_mention(text):
    """تحقق إذا كان الأمر عن طريق تاك، أرجع user_id إن وجد"""
    if text.startswith("@"):
        parts = text.split()
        if len(parts) > 1:
            mention = parts[0]
            # إزالة @
            user_id_or_name = mention[1:]
            print(f"[DEBUG] تم التعرف على تاك: {mention}")
            return user_id_or_name, "mention"
    return None, None


def extract_user_id_from_hash(text):
    """تحقق إذا كان الأمر عن طريق معرف #"""
    if text.startswith("#"):
        parts = text.split()
        if len(parts) > 1:
            hash_id = parts[0][1:]  # إزالة #
            print(f"[DEBUG] تم التعرف على معرف: {hash_id}")
            return hash_id, "hash"
    return None, None


def get_target_info(update):
    """توحيد جميع الطرق للحصول على user_id و text"""
    text = bot.get_text(update)
    print(f"[DEBUG] النص الأصلي للرسالة: {text}")

    # الحالة 1: الرد على رسالة
    user_id = extract_user_id_from_reply(update)

    # حالة التاك أو المعرف إذا لم يتم الحصول على user_id من الرد
    if not user_id:
        # التاك
        mention_user, method = extract_user_id_from_mention(text)
        if mention_user:
            text = text.replace(f"@{mention_user}", "").strip()
            user_id = mention_user
            print(f"[DEBUG] نص الأمر بعد إزالة التاك: {text}")

        # المعرف #
        hash_user, method = extract_user_id_from_hash(text)
        if hash_user:
            text = text.replace(f"#{hash_user}", "").strip()
            user_id = hash_user
            print(f"[DEBUG] نص الأمر بعد إزالة المعرف #: {text}")

    return user_id, text

# ======================= بداية  جلب الuserid and text  نهاية الطرق الثلاثه(ايدي - تاك - رد على رساله) ===========================
# دالة الحصول على رتب العضو 

# داله ازالة اضافة مدير
def on_admin_update(update):
    print("[INFO] تم تحديث صلاحيات الأدمنز في المجموعة")
    update_group_owner(update)

def update_group_owner(update):

    """
    إدارة جدول الرتب (roles):
    - تثبيت رتبة "المنشئ الأساسي" للمالك.
    - إضافة المسؤولين كمنشئين تلقائيًا مع التمييز بين طريقة الإضافة.
    - تحديث الاسم أو اليوزر إذا تغيّر.
    """
    group_id = bot.get_chat_id(update)
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    admins_info = None
    try:
        print(f"[DEBUG] محاولة جلب الأدمنز للمجموعة {group_id}")
        admins_info = bot.get_chat_admins(group_id)
    except Exception as e:
        print(f"[خطأ] فشل في get_chat_admins: {e}")
        conn.close()
        return

    if not admins_info:
        print(f"[INFO] لم يتم العثور على أدمنز للمجموعة {group_id}")
        conn.close()
        return


    # 1. معالجة مالك المجموعة
    owner_info = next((m for m in admins_info.get("members", []) if m.get("is_owner")), None)
    if owner_info:
        owner_id = str(owner_info.get("user_id"))
        owner_name = owner_info.get("name") or ""
        owner_username = owner_info.get("username") or ""

        cursor.execute("""
            SELECT user_id FROM roles 
            WHERE group_id = ? AND role = 'منشئ أساسي' AND priority=3
        """, (group_id,))
        existing_owner = cursor.fetchone()

        if existing_owner is None:
            cursor.execute("""
                INSERT OR REPLACE INTO roles (group_id, user_id, fullname, username, role, priority, added_by_admin)
                VALUES (?, ?, ?, ?, 'منشئ أساسي', 3, 0)
            """, (group_id, owner_id, owner_name, owner_username))
            print(f"[جديد] تمت إضافة المالك الأساسي {owner_name} @{owner_username}")
        elif existing_owner[0] != owner_id:
            old_id = existing_owner[0]
            cursor.execute("DELETE FROM roles WHERE group_id=? AND user_id=?", (group_id, old_id))
            cursor.execute("""
                INSERT OR REPLACE INTO roles (group_id, user_id, fullname, username, role, priority, added_by_admin)
                VALUES (?, ?, ?, ?, 'منشئ أساسي', 3, 0)
            """, (group_id, owner_id, owner_name, owner_username))
            print(f"[تغيير ملكية] تم تحديث المالك الأساسي إلى {owner_name} @{owner_username}")
        else:
            cursor.execute("""
                UPDATE roles SET fullname=?, username=? 
                WHERE group_id=? AND user_id=?
            """, (owner_name, owner_username, group_id, owner_id))
            print(f"[تحديث بيانات] تم تحديث بيانات المالك الحالي {owner_name} @{owner_username}")

        conn.commit()

    # 2. معالجة المسؤولين (is_admin) الآخرين
    for member in admins_info.get("members", []):
        if member.get("is_admin") and not member.get("is_owner"):
            user_id = str(member.get("user_id"))
            fullname = member.get("name") or ""
            username = member.get("username") or ""

            # التحقق من وجوده مسبقًا
            cursor.execute("""
                SELECT user_id FROM roles WHERE group_id=? AND user_id=?
                """, (group_id, user_id))
            row = cursor.fetchone()

            if row is None:
                # إضافة المسؤول كمنشئ تلقائي
                cursor.execute("""
                    INSERT OR REPLACE INTO roles (group_id, user_id, fullname, username, role, priority, added_by_admin)
                    VALUES (?, ?, ?, ?, 'منشئ', 4, 0)
                """, (group_id, user_id, fullname, username))
                print(f"[جديد] تم إضافة المسؤول {fullname} @{username} كمنشئ تلقائي")
            else:
                # تحديث الاسم أو اليوزر إذا تغيّر
                cursor.execute("""
                    UPDATE roles SET fullname=?, username=? 
                    WHERE group_id=? AND user_id=?
                """, (fullname, username, group_id, user_id))
                print(f"[تحديث بيانات] تم تحديث بيانات المسؤول {fullname} @{username}")

    # 3. حذف المنشئين الذين فقدوا صلاحيات المسؤول (added_by_admin=0 فقط)
    cursor.execute("""
        SELECT user_id, fullname, username FROM roles 
        WHERE group_id=? AND priority=4 AND added_by_admin=0
    """, (group_id,))
    all_admins = cursor.fetchall()
    current_admin_ids = [str(m.get("user_id")) for m in admins_info.get("members", []) if m.get("is_admin") and not m.get("is_owner")]

    for u_id, fullname, username in all_admins:
        if u_id not in current_admin_ids:
            cursor.execute("DELETE FROM roles WHERE group_id=? AND user_id=? AND priority=4", (group_id, u_id))
            print(f"[حذف] تم إزالة المنشئ {fullname} @{username} لفقدانه صلاحيات المسؤول")

    conn.commit()

    # طباعة محتويات الجدول للتحقق
    # cursor.execute("SELECT * FROM roles")
    # print("=== محتويات جدول roles ===")
    # for role in cursor.fetchall():
    #     print(role)

    conn.close()

# ================= بداية دالة اضافة البوت لاي مجموعه ==================
# ================= بداية دالة اضافة البوت ==================
# ====== معالجة إضافة البوت ======
# ================= بداية دالة إضافة البوت ==================
def handle_bot_added(update):
    import sqlite3

    group_id = bot.get_chat_id(update)
    print(f"[EVENT] حدث إضافة البوت في المجموعة {group_id}")

    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    # جلب حالة المجموعة
    cursor.execute("SELECT activated, bot_added FROM groups WHERE group_id=?", (group_id,))
    group = cursor.fetchone()

    if group is None:
        cursor.execute(
            "INSERT INTO groups (group_id, activated, bot_added) VALUES (?, 0, 0)", 
            (group_id,)
        )
        conn.commit()
        group = (0, 0)
        print(f"[INFO] تم إنشاء سجل جديد للمجموعة {group_id}")

    activated, bot_added = group
    print(f"[INFO] حالة المجموعة قبل الإضافة: activated={activated}, bot_added={bot_added}")

    # إرسال الترحيب إذا لم يُرسل مسبقًا
    if bot_added == 0:
        welcome_text = (
            "↯︙اهلا بك عزيزي انا بوت ‹ غول.د🧑🏻‍🏫🔹. ›\n"
            "↯︙للتفعيل : قم برفع البوت ‹ مسؤول ›\n"
            "↯︙بعدها ارسل الامر ‹ تفعيل ›\n"
            "↯︙سيتم رفع الادمنيه والمالك تلقائيا\n"
            "┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉"
        )
        bot.send_image_url(
            url=bot.get_bot_full_avatar_url(),
            chat_id=group_id,
            text=welcome_text
        )
        cursor.execute("UPDATE groups SET bot_added=1 WHERE group_id=?", (group_id,))
        conn.commit()
        print(f"[INFO] تم إرسال الترحيب وتحديث bot_added=1 للمجموعة {group_id}")
        protections_list = [
            "الروابط", "البوتات", "المتحركه", "الملصقات", "الملفات",
            "الصور", "الفيديو", "الالعاب", "الدردشه", "التوجيه", "الاغاني",
            "الصوت", "الجهات", "الهمسه", "التكرار", "التاك",
            "التعديل", "الفايروس", "الكلايش", "الهايشتاك", "الترحيب",
            "الفشار", "الكل", "الردود","الخصوصية"
        ]

        for protection_name in protections_list:
          # هنا نستدعي الدالة التي كتبناها سابقًا
          set_protection_status(group_id, protection_name, 1)  # 1 تعني مفعلة/افتراضية مفتوحة

    # منع أي أوامر قبل التفعيل
    if not activated:
        group_activation_state[group_id] = False
        print(f"[INFO] المجموعة {group_id} غير مفعلة بعد — سيتم انتظار أمر 'تفعيل'")
        conn.close()
        return True  # تعني: لا نتابع أي أوامر أخرى حتى يتم التفعيل

    conn.close()
    return False  # تعني: البوت مفعّل، يمكن متابعة باقي الأوامر
# ================= نهاية دالة إضافة البوت ==================

# ================= نهاية اضافة البوت ==================
# =================== فحص ومعالجة إضافة البوت ===================
def check_and_handle_bot_added(update):
    """
    تتحقق إذا تم إضافة البوت للمجموعة وتنفذ الترحيب.
    تعود True إذا تم التعامل مع حدث إضافة البوت لتخطي بقية المعالجة.
    """
    group_id = bot.get_chat_id(update)
    action = update.get("message", {}).get("action", {})

    if action.get("bot_added", False) or update.get("update_type") == "bot_added":
        print(f"[EVENT] تم إضافة البوت في المجموعة {group_id}")
        handle_bot_added(update)  # استدعاء دالة الترحيب الأصلية
        return True

    return False

# ================= بداية دالة التفعيل ==================


# كاش لحالات التفعيل
group_activation_state = {}
user_command_state = {}

# ======================= دالة التفعيل =======================
def handle_activation(update):
    group_id = bot.get_chat_id(update)
    user_id = str(bot.get_user_id(update))
    user_name = bot.get_name(update)
    user_username = bot.get_username(update)

    print(f"[ACTIVATION] محاولة تفعيل من المستخدم {user_id} في المجموعة {group_id}")

    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    try:
        admins_info = bot.get_chat_admins(group_id)
        print(f"[ACTIVATION] جلبت معلومات الأدمنز: {admins_info}")
    except Exception as e:
        print(f"[ERROR] فشل في جلب الأدمنز: {e}")
        bot.send_message(chat_id=group_id, text=  "⚠️ حدث خطأ أثناء جلب الأدمنز.")
        return False

    # جلب المالك (Owner فقط)
    owner_info = next((m for m in admins_info.get("members", []) if m.get("is_owner")), None)
   
    if not owner_info:
        print("[ACTIVATION] لم يتم العثور على مالك للمجموعة!")
        bot.send_message(chat_id=group_id, text= "❌ لم أستطع تحديد مالك المجموعة.")
        return False

    if str(owner_info.get("user_id")) != user_id:
        print(f"[ACTIVATION] المستخدم {user_id} ليس هو المالك {owner_info.get('user_id')}")
        bot.send_message(chat_id=group_id, text=  "❌ التفعيل مسموح فقط للمالك الأساسي.")
        return False

    # إضافة المالك كـ منشئ أساسي
    cursor.execute("""
        INSERT OR REPLACE INTO roles (group_id, user_id, fullname, username, role, priority, added_by_admin)
        VALUES (?, ?, ?, ?, 'منشئ أساسي', 3, 0)
    """, (group_id, user_id, user_name, user_username))
    print(f"[ACTIVATION] تمت إضافة المالك {user_id} كمنشئ أساسي")

    # إضافة باقي الأدمنز كـ منشئين
    for member in admins_info.get("members", []):
        if member.get("is_admin") and not member.get("is_owner"):
            uid = str(member.get("user_id"))
            fname = member.get("name") or ""
            uname = member.get("username") or ""
            cursor.execute("""
                INSERT OR REPLACE INTO roles (group_id, user_id, fullname, username, role, priority, added_by_admin)
                VALUES (?, ?, ?, ?, 'منشئ', 4, 0)
            """, (group_id, uid, fname, uname))
            print(f"[ACTIVATION] تمت إضافة الأدمن {uid} كمنشئ")

    # تحديث حالة التفعيل
    cursor.execute("UPDATE groups SET activated=1 WHERE group_id=?", (group_id,))
    conn.commit()
    conn.close()

    print(f"[ACTIVATION] ✅ تم تفعيل البوت في المجموعة {group_id}")
    bot.send_message(chat_id=group_id, text=  "✅ تم تفعيل البوت بنجاح!\nتم رفع المالك والمنشئين تلقائياً.\nيمكنك الآن استخدام الأوامر.")
    return True

# ================= نهاية دالة التفعيل ==================

# ======================== نهاية اضافة البوت لاي مجموعه ========================


# ----------------- دالة الحذف مع تتبع كامل -----------------
def handle_bot_removed(update, group_activation_state=None):
    group_id = bot.get_chat_id(update)
    gid = str(group_id)
    print("=" * 60)
    print(f"[EVENT] 🚨 تم رصد إزالة البوت من المجموعة {gid}")

    try:
        print("[DB] محاولة الاتصال بقاعدة البيانات...")
        conn = sqlite3.connect("bot_data.sqlite", timeout=10)
        cursor = conn.cursor()
        print("[DB] ✅ تم الاتصال بنجاح.")

        tables = [
            ("users", "group_id"),
            ("roles", "group_id"),
            ("group_protection_settings", "group_id"),
            ("groups", "group_id"),
            ("group_replies", "chat_id"),
            ("command_aliases", "group_id"),
        ]

        # طباعة محتويات قبل الحذف
        print("[STEP 1] 🔍 فحص محتويات الجداول قبل الحذف...")
        for tbl, col in tables:
            try:
                print(f"\n--- جدول {tbl} ---")
                cursor.execute(f"SELECT * FROM {tbl} WHERE {col}=?", (gid,))
                rows = cursor.fetchall()
                if rows:
                    print(f"🔹 {len(rows)} سجل/سجلات موجودة:")
                    for r in rows:
                        print(r)
                else:
                    print("❌ لا توجد بيانات للمجموعة.")
            except sqlite3.OperationalError:
                print(f"⚠ جدول {tbl} غير موجود — تم تجاهله.")

        # الحذف
        print("\n[STEP 2] 🗑️ بدء عملية حذف بيانات المجموعة...")
        for tbl, col in tables:
            try:
                cursor.execute(f"DELETE FROM {tbl} WHERE {col}=?", (gid,))
                print(f"✅ تم حذف بيانات من جدول {tbl}")
            except sqlite3.OperationalError:
                print(f"⚠ جدول {tbl} غير موجود — تجاهل الحذف.")

        conn.commit()
        print("[DB] ✅ تم حفظ التغييرات.")

        # طباعة للتأكد بعد الحذف
        print("\n[STEP 3] 🔍 التحقق من الجداول بعد الحذف...")
        for tbl, col in tables:
            try:
                cursor.execute(f"SELECT * FROM {tbl} WHERE {col}=?", (gid,))
                rows_after = cursor.fetchall()
                if rows_after:
                    print(f"⚠ ما زال هناك بيانات في جدول {tbl}: {rows_after}")
                else:
                    print(f"✅ جدول {tbl} فارغ الآن لهذه المجموعة.")
            except sqlite3.OperationalError:
                print(f"⚠ جدول {tbl} غير موجود (بعد الحذف).")
    except Exception as e:
        print(f"[ERROR] ❌ خطأ أثناء حذف بيانات المجموعة {gid}: {e}")
    finally:
        try:
            conn.close()
            print("[DB] 🔒 تم إغلاق الاتصال.")
        except Exception:
            pass

    # تحديث الكاش
    print("\n[STEP 4] 🧹 تحديث الكاش الداخلي...")
    try:
        if group_activation_state is not None:
            removed = False
            if gid in group_activation_state:
                del group_activation_state[gid]
                print(f"✅ تم إزالة {gid} من الكاش (string).")
                removed = True
            try:
                gid_int = int(group_id)
                if gid_int in group_activation_state:
                    del group_activation_state[gid_int]
                    print(f"✅ تم إزالة {gid_int} من الكاش (int).")
                    removed = True
            except Exception:
                pass
            if not removed:
                print("ℹ️ لم يكن موجودًا في الكاش.")
    except NameError:
        print("⚠ group_activation_state غير معرف — تم التجاهل.")

    print(f"[INFO] 🎉 تم مسح بيانات المجموعة {gid} بنجاح.")
    print("=" * 60)


# ----------------- دالة المساعدة -----------------
def check_and_handle_bot_removed(update, group_activation_state):
    updates_list = []
    if isinstance(update, dict) and "updates" in update:
        updates_list = update["updates"]
    elif isinstance(update, list):
        updates_list = update
    else:
        updates_list = [update]

    for single in updates_list:
        action = (single.get("message", {}) or {}).get("action", {}) if isinstance(single, dict) else {}
        update_type = single.get("update_type") if isinstance(single, dict) else None
        if action.get("bot_removed") or (update_type in ["bot_removed", "left", "kicked"]):
            print("[CHECK] ✅ تم رصد إشارة لحذف البوت.")
            handle_bot_removed(single, group_activation_state)
            return True

    print("[CHECK] ℹ️ لا يوجد حدث حذف للبوت في هذا التحديث.")
    return False


# كاش لحالة التفعيل
group_activation_state = {}
# import sqlite3

# def clear_group_protection_settings():
#     conn = sqlite3.connect("bot_data.sqlite")
#     cursor = conn.cursor()

#     print("🔹 بيانات جدول group_protection_settings قبل الحذف:")
#     rows = cursor.execute("""
#         SELECT group_id, protection_id, status FROM group_protection_settings
#     """).fetchall()
#     if rows:
#         for row in rows:
#             print(row)
#     else:
#         print("⚠️ الجدول فارغ بالفعل.")

#     # حذف جميع البيانات
#     cursor.execute("DELETE FROM group_protection_settings")
#     conn.commit()

#     print("\n🔹 بيانات جدول group_protection_settings بعد الحذف:")
#     rows_after = cursor.execute("""
#         SELECT group_id, protection_id, status FROM group_protection_settings
#     """).fetchall()
#     if rows_after:
#         for row in rows_after:
#             print(row)
#     else:
#         print("✅ الجدول فارغ الآن.")

#     conn.close()

# تنفيذ الدالة
# clear_group_protection_settings()

# ==========================
# دالة معالجة التحديثات
# ==========================

# إنشاء اتصال واحد مستمر للـ Thread
import sqlite3

# def print_users_table():
#     conn = sqlite3.connect("bot_data.sqlite")
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users")
#     rows = cursor.fetchall()

#     if not rows:
#         print("🟢 جدول users فارغ!")
#     else:
#         print("=== محتويات جدول users ===")
#         # طباعة رؤوس الأعمدة تلقائيًا
#         cursor.execute("PRAGMA table_info(users)")
#         columns = [col[1] for col in cursor.fetchall()]
#         print(" | ".join(columns))
#         print("-" * 100)
#         for row in rows:
#             print(" | ".join([str(item) for item in row]))

#     conn.close()


def handle_message(update):
    """معالجة تحديث واحد مع إدراج بيانات المستخدم بشكل صحيح"""
    try:
        print("\n[RAW UPDATE]--------------")
        print(json.dumps(update, ensure_ascii=False, indent=2))

        # محاولة استخراج البيانات الأساسية من التحديث
        message = update.get("message")
        if not message:
            print("[ERROR] لا يوجد مفتاح 'message' في التحديث")
            return

        sender = message.get("sender", {})
        recipient = message.get("recipient", {})

        # ===== استخراج بيانات المستخدم =====
        chat_id = recipient.get("chat_id")
        message_id = message.get("body", {}).get("mid")
        user_id = sender.get("user_id")
        username = sender.get("username") or f"user_{user_id}"
        fullname = sender.get("name") or "مستخدم"
        is_bot = int(sender.get("is_bot", False))

        text = message.get("body", {}).get("text", "")
        text_clean = text.lower() if text else ""

        # طباعة البيانات المستخرجة للمراجعة
        print(f"[DEBUG] chat_id={chat_id}, message_id={message_id}, user_id={user_id}")
        print(f"[DEBUG] username={username}, fullname={fullname}, is_bot={is_bot}")
        print(f"[DEBUG] text='{text}', text_clean='{text_clean}'")

        # ===== تحديث أو إضافة المستخدم في users =====
        conn = sqlite3.connect("bot_data.sqlite", timeout=10)
        cursor = conn.cursor()

        # التأكد أن الاستعلام يجلب الأعمدة الجديدة last_notified_*
        cursor.execute("""
            SELECT username, fullname, is_bot, last_notified_username, last_notified_fullname
            FROM users 
            WHERE group_id = ? AND user_id = ?
        """, (chat_id, user_id))
        row = cursor.fetchone()

        if row is None:
            print(f"[INFO] المستخدم {fullname} @{username} غير موجود في users → سيتم إضافته")
            cursor.execute("""
                INSERT INTO users (
                    group_id, user_id, username, fullname, is_bot, 
                    last_notified_username, last_notified_fullname
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (chat_id, user_id, username, fullname, is_bot, username, fullname))
            conn.commit()
            print("[INFO] تم إضافة المستخدم بنجاح")
        else:
            old_username, old_fullname, old_is_bot, last_notified_username, last_notified_fullname = row
            changes = []
            send_messages = []  # لتخزين الرسائل المرسلة

            # مقارنة fullname مع last_notified_fullname
            if last_notified_fullname != fullname:
                cursor.execute("""
                    UPDATE users 
                    SET fullname=?, last_notified_fullname=? 
                    WHERE group_id=? AND user_id=?
                """, (fullname, fullname, chat_id, user_id))
                # فقط أرسل رسالة إذا كانت القيمة السابقة ليست None
                if last_notified_fullname is not None:
                    changes.append("اسم")
                    send_messages.append(f"مو جان اسمك [{last_notified_fullname}] → [{fullname}] ......ليش غيرته؟")

            # مقارنة username مع last_notified_username
            if last_notified_username != username:
                cursor.execute("""
                    UPDATE users 
                    SET username=?, last_notified_username=? 
                    WHERE group_id=? AND user_id=?
                """, (username, username, chat_id, user_id))
                # فقط أرسل رسالة إذا كانت القيمة السابقة ليست None
                if last_notified_username is not None:
                    changes.append("معرف")
                    send_messages.append(f"مو جان معرفك [@{last_notified_username}] → [@{username}] ......ليش غيرته؟")

            # تحديث حالة البوت
            if old_is_bot != is_bot:
                cursor.execute("UPDATE users SET is_bot=? WHERE group_id=? AND user_id=?", (is_bot, chat_id, user_id))

            # إرسال الرسائل فقط إذا كانت موجودة
            if send_messages:
                conn.commit()
                msg = "\n".join(send_messages)
                bot.send_reply_message(
                    text=msg,
                    chat_id=chat_id,
                    mid=message_id
                )
                print(f"[تحديث] {msg}")

        conn.close()
        print("[DEBUG] الاتصال بقاعدة البيانات تم إغلاقه")

        print("[DEBUG] الاتصال بقاعدة البيانات تم إغلاقه")

    except Exception as e:
        print(f"[ERROR] أثناء handle_message: {e}")

def update_loop():
    while True:
        try:
            updates = bot.get_updates()
            for update in updates.get("updates", []):
                if update.get("update_type") == "bot_added":
                    print("[LOOP] اكتشاف حدث bot_added → استدعاء handle_bot_added")
                    handle_bot_added(update)
                    continue
                if update.get("update_type") == "message_created":
                    handle_message(update)
                    try:
                        update_group_owner(update)
                    except Exception as e:
                        print(f"[DEBUG] فشل في تحديث بيانات المالك: {e}")
        except Exception as e:
            print(f"[ERROR] حدث خطأ أثناء معالجة التحديثات: {e}")
        time.sleep(1)

# تشغيل الحلقة في Thread منفصل
thread = threading.Thread(target=update_loop, daemon=True)
thread.start()

# الآن أي كود هنا بعد هذا سيعمل
print("✅ البوت يعمل، يمكن تنفيذ باقي الدوال هنا")
# =============== بداية دالة جلب مالك المجموعه========================
def is_main_owner(chat_id, user_id):
    """
    التحقق هل المستخدم هو المالك الأساسي (منشئ المجموعة).
    تم تعديل شرط SQL ليكون ذو أقواس صحيحة.
    """
    try:
        conn = sqlite3.connect("bot_data.sqlite", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM roles 
            WHERE group_id=? 
              AND user_id=? 
              AND (role IN ('منشئ أساسي','منشئ'))
              AND (priority IN (3,4))
            LIMIT 1
        """, (str(chat_id), str(user_id)))
        row = cursor.fetchone()
        return row is not None
    except Exception as e:
        print(f"[ERROR][is_main_owner] خطأ في DB: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

# ===============  نهاية دالة جلب مالك المجموعه========================
# التحقق من المطور
def is_dev(user_id: int) -> bool:
    devs_data = db.get("devs")
    result = devs_data and str(user_id) in devs_data.get("ids", [])
    print(f"[TRACE] is_dev check for user_id={user_id}: {result}")
    return result

# التحقق من المطور الأساسي
def is_main_dev(user_id: int) -> bool:
    devs_data = db.get("devs")
    return devs_data and devs_data["ids"] and str(user_id) == devs_data["ids"][0]

# استخراج user_id من الرد
def get_target_user_id(update):
    updates = update.get("updates", [])
    if not updates:
        return None
    msg = updates[0].get("message", {})
    reply_msg = msg.get("reply_to_message")
    if reply_msg:
        user_data = reply_msg.get("sender") or reply_msg.get("from") or {}
        user_id = user_data.get("user_id")
        if user_id:
            return int(user_id)
    link = msg.get("link")
    if link:
        sender_data = link.get("sender")
        if sender_data:
            user_id = sender_data.get("user_id")
            if user_id:
                return int(user_id)
    return None
# دالة الرد على الرسائل 
def send_reply_message(text, chat_id, message_id):
    bot.send_reply_message(text=text, chat_id=chat_id, mid=message_id)
# دالة جلب اوامر الحماية
# def set_protection_status(group_id, protection_name, status):
#     conn = sqlite3.connect("bot_data.sqlite", timeout=10)
#     cursor = conn.cursor()
#     cursor.execute("SELECT id FROM protections WHERE name = ?", (protection_name,))
#     row = cursor.fetchone()
#     if row:
#         protection_id = row[0]
#         cursor.execute("""
#             UPDATE group_protection_settings
#             SET status = ?
#             WHERE group_id = ? AND protection_id = ?
#         """, (status, str(group_id), protection_id))
#     conn.commit()
#     conn.close()
# دالة اضافة اوامر الحماية لمجموعه جديده
def get_protection_status(group_id, protection_name):
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gps.status FROM group_protection_settings gps
        JOIN protections p ON gps.protection_id = p.id
        WHERE gps.group_id = ? AND p.name = ?
    """, (str(group_id), protection_name))
    row = cursor.fetchone()
def set_protection_status(group_id, protection_name, status):
    conn = sqlite3.connect("bot_data.sqlite", timeout=10)
    cursor = conn.cursor()

    # الحصول على protection_id
    cursor.execute("SELECT id FROM protections WHERE name = ?", (protection_name,))
    row = cursor.fetchone()
    if row:
        protection_id = row[0]

        # التحقق إذا السجل موجود
        cursor.execute("""
            SELECT 1 FROM group_protection_settings
            WHERE group_id = ? AND protection_id = ?
        """, (str(group_id), protection_id))
        exists = cursor.fetchone()

        if exists:
            # تحديث فقط
            cursor.execute("""
                UPDATE group_protection_settings
                SET status = ?
                WHERE group_id = ? AND protection_id = ?
            """, (status, str(group_id), protection_id))
        else:
            # إدخال جديد
            cursor.execute("""
                INSERT INTO group_protection_settings (group_id, protection_id, status)
                VALUES (?, ?, ?)
            """, (str(group_id), protection_id, status))

    conn.commit()
    conn.close()

    
#     conn.close()
#     return row[0] if row else 1  # افتراضي مفتوح

# =============== بداية دالة اضافة مرادفات للاوامر =====================
def add_command_alias(base_command, new_alias, group_id, added_by):
    """
    يضيف مرادف جديد للأمر الأساسي إذا كان ضمن حدود 3 مرادفات.
    يتحقق من الصلاحيات حسب COMMANDS_REQUIRED_PRIORITY.
    """
    print(f"[TRACE] محاولة إضافة المرادف '{new_alias}' للأمر '{base_command}' في المجموعة {group_id} بواسطة {added_by}")

    # تحقق من وجود الأمر الأساسي في القاموس
    if base_command not in COMMANDS_REQUIRED_PRIORITY:
        print(f"[ERROR] الأمر الأساسي '{base_command}' غير موجود في القاموس.")
        return f"❌ الأمر الأساسي '{base_command}' غير موجود."

    with sqlite3.connect("bot_data.sqlite") as conn:
        cursor = conn.cursor()

        # تحقق عدد المرادفات الحالية
        cursor.execute("""
            SELECT COUNT(*) FROM command_aliases
            WHERE base_command=? AND group_id=?
        """, (base_command, group_id))
        count = cursor.fetchone()[0]
        print(f"[DEBUG] عدد المرادفات الحالية للأمر '{base_command}': {count}")

        if count >= 3:
            print("[WARN] لا يمكن إضافة أكثر من 3 مرادفات.")
            return f"❌ لا يمكن إضافة أكثر من 3 مرادفات للأمر '{base_command}'."

        # تحقق من وجود المرادف مسبقًا
        cursor.execute("""
            SELECT 1 FROM command_aliases
            WHERE base_command=? AND alias=? AND group_id=?
        """, (base_command, new_alias, group_id))
        if cursor.fetchone():
            print(f"[INFO] المرادف '{new_alias}' موجود مسبقًا للأمر '{base_command}'.")
            return f"ℹ️ المرادف '{new_alias}' موجود مسبقًا."

        # أضف المرادف
        cursor.execute("""
            INSERT INTO command_aliases (base_command, alias, group_id, added_by)
            VALUES (?, ?, ?, ?)
        """, (base_command, new_alias, group_id, added_by))
        conn.commit()
        print(f"[SUCCESS] تم إضافة المرادف '{new_alias}' بنجاح.")
        return f"✅ تم إضافة المرادف '{new_alias}' للأمر '{base_command}'."

# =================== نهاية داله اضافة مرادفات للاوامر ======================


# =================== بداية دالة حذف مرادفات للاوامر =======================
def remove_command_alias(base_command, alias, group_id):
    """
    يحذف مرادف موجود للأمر الأساسي بعد التحقق من وجوده.
    """
    print(f"[TRACE] محاولة حذف المرادف '{alias}' للأمر '{base_command}' في المجموعة {group_id}")

    with sqlite3.connect("bot_data.sqlite") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM command_aliases
            WHERE base_command=? AND alias=? AND group_id=?
        """, (base_command, alias, group_id))
        if not cursor.fetchone():
            print(f"[INFO] المرادف '{alias}' غير موجود للأمر '{base_command}'.")
            return f"ℹ️ المرادف '{alias}' غير موجود للأمر '{base_command}'."

        cursor.execute("""
            DELETE FROM command_aliases
            WHERE base_command=? AND alias=? AND group_id=?
        """, (base_command, alias, group_id))
        conn.commit()
        print(f"[SUCCESS] تم حذف المرادف '{alias}' بنجاح.")
        return f"✅ تم حذف المرادف '{alias}' للأمر '{base_command}'."
# =================== نهاية دالة حذف مرادفات للاوامر =======================
# ================================================
def get_command_aliases(base_command, chat_id):
    """
    تسترجع قائمة المرادفات للأمر في الدردشة المحددة.
    """
    conn = sqlite3.connect("bot_data.sqlite")  # تأكد من اسم قاعدة البيانات الصحيح
    cursor = conn.cursor()
    cursor.execute(
        "SELECT alias FROM command_aliases WHERE base_command=? AND group_id=?",
        (base_command, str(chat_id))
    )
    aliases = [row[0] for row in cursor.fetchall()]
    conn.close()
    return aliases

# ================================================
# ================================================
def get_command_from_text(text, chat_id):
    """
    تفحص النص لمعرفة إذا كان أمر أساسي أو أحد مرادفاته.
    ترجع base_command أو None إذا لم يكن موجود.
    """
    if not text:
        return None
    lower_text = text.strip().lower()
    # تحقق من القاموس الأساسي
    if lower_text in COMMANDS_REQUIRED_PRIORITY:
        return lower_text

    # تحقق من جدول المرادفات
    with sqlite3.connect("bot_data.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT base_command FROM command_aliases
            WHERE alias=? AND group_id=?
        """, (lower_text, str(chat_id)))
        row = cursor.fetchone()
        if row:
            return row[0]
    return None

# ===============================================

# ================  بداية دالة استخراج البيانات من التحديث =======================
def extract_message_data(update):
    """
    استخرج البيانات الأساسية من أي تحديث:
    - chat_id
    - message_id
    - user_id
    - username
    - text
    - target_user_id, target_name, target_username (لرسائل الرد)
    """
    chat_id = None
    message_id = None
    user_id = None
    username = None
    text = ""
    target_user_id = ""
    target_name = "مستخدم"
    target_username = ""

    try:
        updates = update.get("updates", [])
        msg = updates[0].get("message", {}) if updates else {}

        # البيانات الأساسية للمرسل
        sender = msg.get("sender") or msg.get("from") or {}
        chat = msg.get("recipient") or {}
        chat_id = chat.get("chat_id")
        message_id = msg.get("mid")
        user_id = sender.get("user_id")
        username = sender.get("username", f"user_{user_id}")
        text = (msg.get("body", {}).get("text") or "").strip()

        # بيانات هدف الرد (reply) أو link
        reply_sender = {}
        if "reply_to_message" in msg:
            reply_msg = msg.get("reply_to_message", {})
            reply_sender = reply_msg.get("sender") or reply_msg.get("from") or {}
        elif "link" in msg and msg["link"].get("type") == "reply":
            link = msg.get("link")
            reply_sender = link.get("sender") or {}

        if reply_sender:
            target_user_id = str(reply_sender.get("user_id", ""))
            target_name = reply_sender.get("name", "مستخدم")
            target_username = reply_sender.get("username", "")

        return {
            "chat_id": chat_id,
            "message_id": message_id,
            "user_id": user_id,
            "username": username,
            "text": text,
            "target_user_id": target_user_id,
            "target_name": target_name,
            "target_username": target_username,
            "raw_msg": msg
        }

    except Exception as e:
        print(f"[ERROR] فشل استخراج بيانات الرسالة: {e}")
        return None
# ================ نهاية دالة استخراج البيانات من التحديث =======================
#================== بداية دالة استخراج الاشخاص المصرح لهم =====================
def is_authorized(user_id, chat_id, max_priority=7):
    """
    التحقق هل المستخدم مصرح له باستخدام الأوامر بناءً على جدول roles.
    🔹 يرجع True إذا كان لديه رتبة priority <= max_priority
    🔹 يأخذ بالاعتبار group_id (إما نفس المجموعة أو 'global')
    """
    try:
        conn = sqlite3.connect("bot_data.sqlite")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, priority
            FROM roles 
            WHERE user_id=? 
              AND priority <= ? 
              AND group_id IN (?, 'global')
            LIMIT 1
        """, (str(user_id), max_priority, str(chat_id)))
        row = cursor.fetchone()
        conn.close()

        if row:
            role, priority = row
            print(f"[TRACE] is_authorized → user_id={user_id}, chat_id={chat_id}, role={role}, priority={priority}, result=True")
            return True
        else:
            print(f"[TRACE] is_authorized → user_id={user_id}, chat_id={chat_id}, result=False")
            return False

    except Exception as e:
        print(f"[ERROR] خطأ أثناء التحقق من صلاحيات المستخدم: {e}")
        return False

#==================  نهاية دالة استخراج الاشخاص المصرح لهم =====================
# ================== البحث عن الأمر الأساسي من نص المستخدم =======================
def get_base_command_from_text(text, group_id):
    """
    إذا كان النص مطابقًا لأمر أساسي → يرجع الأمر الأساسي.
    إذا كان نص مطابق لأي مرادف → يرجع الأمر الأساسي.
    """
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)
    print(f"[TRACE] البحث عن الأمر الأساسي للنص: '{lower_text}' في المجموعة {group_id}")

    # أولًا تحقق من القاموس الأساسي
    if lower_text in COMMANDS_REQUIRED_PRIORITY:
        print(f"[FOUND] النص يطابق الأمر الأساسي مباشرة: '{lower_text}'")
        return lower_text

    # تحقق من جدول المرادفات
    with sqlite3.connect("bot_data.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT base_command FROM command_aliases
            WHERE alias=? AND group_id=?
        """, (lower_text, group_id))
        row = cursor.fetchone()
        if row:
            print(f"[FOUND] النص يطابق مرادف للأمر الأساسي: '{row[0]}'")
            return row[0]

    print("[INFO] لا يوجد أمر مطابق للنص.")
    return None  # لا يوجد أمر مطابق
# ================== نهاية البحث عن الأمر الأساسي من نص المستخدم =======================


# -========بداية  دالة انتظار ارسال رساله (الانتظار) ====================
def process_waiting_response(chat_id, user_id, msg_text, message_id):
    try:
        # ===== معالجة الترحيب =====
        if str(chat_id) in waiting.get("welcome", {}):
            expected_user_id = waiting["welcome"][str(chat_id)]
            if str(user_id) == expected_user_id:
                welcome_manager.add_welcome(chat_id, msg_text)
                send_reply_message(f"✅ تم حفظ الترحيب:\n{msg_text}", chat_id, message_id)
                del waiting["welcome"][str(chat_id)]
                print(f"[DEBUG] تم حفظ الترحيب للمجموعة {chat_id} من المستخدم {user_id}")
                return  # الرجوع بعد حفظ الترحيب

        # ===== معالجة إضافة الرد =====
        if str(chat_id) in waiting.get("reply", {}):
            expected_user_id = waiting["reply"][str(chat_id)]
            if str(user_id) == expected_user_id:
                # إذا لم تُرسل الكلمة بعد
                if str(chat_id) not in waiting_data["reply"]:
                    waiting_data["reply"][str(chat_id)] = msg_text.strip()
                    send_reply_message(
                        "✍️ الآن أرسل الرد النصي المرتبط بهذه الكلمة.",
                        chat_id,
                        message_id
                    )
                    print(f"[DEBUG] تم استقبال الكلمة '{msg_text.strip()}' من المستخدم {user_id}")
                else:
                    # النص الحالي هو الرد نفسه
                    keyword = waiting_data["reply"].pop(str(chat_id))
                    reply_manager.add_reply(chat_id, keyword, msg_text.strip())
                    send_reply_message(
                        f"✅ تم حفظ الرد بنجاح:\n`{keyword}` -> `{msg_text.strip()}`",
                        chat_id,
                        message_id
                    )
                    del waiting["reply"][str(chat_id)]
                    print(f"[DEBUG] تم حفظ الرد للمجموعة {chat_id} من المستخدم {user_id}: {keyword} -> {msg_text.strip()}")
        # ===== معالجة حذف الرد =====
        if str(chat_id) in waiting.get("delete_reply", {}):
            expected_user_id = waiting["delete_reply"][str(chat_id)]
            if str(user_id) == expected_user_id:
                keyword = msg_text.strip()
                if reply_manager.delete_reply(chat_id, keyword):
                    send_reply_message(f"✅ تم حذف الرد للكلمة '{keyword}'.", chat_id, message_id)
                    print(f"[DEBUG] تم حذف الرد للمجموعة {chat_id} من المستخدم {user_id}: {keyword}")
                else:
                    send_reply_message(f"⚠ لا يوجد رد مرتبط بالكلمة '{keyword}'.", chat_id, message_id)
                    print(f"[TRACE] لا يوجد رد مرتبط بالكلمة '{keyword}' للمجموعة {chat_id}")
                del waiting["delete_reply"][str(chat_id)]
                return

    except Exception as e:
        print(f"[ERROR] خطأ أثناء معالجة الانتظار: {e}")
# ================== انتظار الردود متعددة الخطوات ==================
user_command_state_response2 = {}  # لكل المستخدم/مجموعة

def handle_reply_state(state_key, lower_text, chat_id, message_id, user_id):
    """
    إدارة حالة إضافة/حذف الردود أو الترحيب.
    """
    state = user_command_state_response2[state_key]
    step = state.get("step")
    action = state.get("action")

    # ===== الخطوة الأولى: استقبال الكلمة الأساسية =====
    if step == 1:
        keyword = lower_text.strip()
        user_priority = get_user_priority(chat_id, user_id)

        if action == "add_reply":
            send_reply_message(f"✍️ الآن أرسل الرد المرتبط بالكلمة '{keyword}'", chat_id, message_id)
            user_command_state_response2[state_key]["step"] = 2
            user_command_state_response2[state_key]["keyword"] = keyword

        elif action == "remove_reply":
            existing_replies = reply_manager.get_all_replies(chat_id)
            if keyword in existing_replies:
                reply_manager.delete_reply(chat_id, keyword)
                send_reply_message(f"✅ تم حذف الرد للكلمة '{keyword}'", chat_id, message_id)
            else:
                send_reply_message(f"⚠ لا يوجد رد مرتبط بالكلمة '{keyword}'", chat_id, message_id)
            # إنهاء حالة المستخدم مباشرة بعد الحذف أو عدم وجود الرد
            user_command_state_response2.pop(state_key)
            return

        elif action == "add_welcome":
            # send_reply_message("📌 أرسل نص الترحيب الجديد للمجموعة:", chat_id, message_id)
            user_command_state_response2[state_key]["step"] = 2

    # ===== الخطوة الثانية: استقبال الرد أو الترحيب =====
    elif step == 2:
        keyword = state.get("keyword")

        if action == "add_reply":
            reply_manager.add_reply(chat_id, keyword, lower_text)
            send_reply_message(f"✅ تم حفظ الرد: '{keyword}' -> '{lower_text}'", chat_id, message_id)

        elif action == "add_welcome":
            welcome_manager.add_welcome(chat_id, lower_text)
            send_reply_message(f"✅ تم تحديث الترحيب:\n{lower_text}", chat_id, message_id)

        # إنهاء حالة المستخدم بعد أي عملية
        user_command_state_response2.pop(state_key)

# -========نهاية دالة انتظار ارسال رساله (الانتظار) ====================
# أوامر المطورين المشتركة
def handle_common_dev_commands(text, chat_id, message_id):
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)
    if lower_text == "هلو":
        bot.send_reply_message(text=" 🌟", chat_id=chat_id, mid=message_id)
    elif lower_text == "شلونك؟":
        bot.send_reply_message(text="تمام والحمد لله، شلونك أنت؟", chat_id=chat_id, mid=message_id)
    elif lower_text == "بوت":
        bot.send_reply_message(text="ها", chat_id=chat_id, mid=message_id)
    elif lower_text == "وجعا":
        bot.send_reply_message(text="وجعا توجعك", chat_id=chat_id, mid=message_id)
    else:
        return False
    return True

def handle_general_responses(update, text, chat_id, message_id):
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)

    responses = {
        "بوت": "عيون Gol D 😎",
        "شلونك": "الحمد لله بخير و انت؟ 🌟",
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته 👋",
        "مرحبا": "هلا وغلا 🌹",
        "هاي": "هاي نورت ✨",
        "منور": "بوجودك ⚡️",
        "باي": "مع السلامة 🤍",
        "مساء الخير": "مساء النور 🌙",
        "صباح الخير": "صباح الورد ☀️",
        "هلو": "هلا بيك 🌼"
    }

    if lower_text in responses:
        bot.send_reply_message(
            text=responses[lower_text],
            chat_id=chat_id,
            mid=message_id
        )
        return True

    return False

# باقي الدوال مثل handle_main_dev_commands و main وغيرها
# يجب ترتيبها أيضًا بنفس الشكل، وإذا رغبت بإكمال ترتيب كامل الكود أخبرني وسأكمله لك بالكامل بنفس الدقة.
# متغير عالمي لتخزين آخر 100 رسالة لكل دردشة
last_messages_per_chat = {}
# هذه الدالة يجب أن تستدعى عند استقبال أي رسالة جديدة (في دالة معالجة الرسائل لديك)
# def on_new_message(update):
#     try:
#         message_obj = update.get("updates", [{}])[0].get("message", {})
#         chat_id = message_obj.get("recipient", {}).get("chat_id")
#         message_id = message_obj.get("body", {}).get("mid")
#         if chat_id and message_id:
#             store_message_id(chat_id, message_id)
#     except Exception as e:
#         print(f"[ERROR] أثناء تخزين معرف الرسالة: {e}")
def on_new_message(update):
    try:
        message_obj = update.get("updates", [{}])[0].get("message", {})
        chat_id = message_obj.get("recipient", {}).get("chat_id")
        message_id = message_obj.get("body", {}).get("mid")
        if chat_id and message_id:
            save_message(chat_id, message_id, from_bot=False)  # رسالة مستخدم
    except Exception as e:
        print(f"[ERROR] أثناء تخزين معرف الرسالة: {e}")

# داله حفظ رسائل


# def save_message(chat_id, message_id, from_bot=False):
#     if chat_id not in last_messages_per_chat:
#         last_messages_per_chat[chat_id] = []
#     last_messages_per_chat[chat_id].append((message_id, from_bot))
#     # نحافظ على آخر 100 رسالة فقط
#     if len(last_messages_per_chat[chat_id]) > 100:
#         removed = last_messages_per_chat[chat_id].pop(0)
#         print(f"[DEBUG] حذف أقدم رسالة محفوظة من القائمة: {removed}")

# def save_message(chat_id, message_id, from_bot=False):
#     if chat_id not in last_messages_per_chat:
#         last_messages_per_chat[chat_id] = []
#     last_messages_per_chat[chat_id].append((message_id, from_bot))
#     # نحافظ على آخر 100 رسالة فقط
#     if len(last_messages_per_chat[chat_id]) > 100:
#         removed = last_messages_per_chat[chat_id].pop(0)
#         print(f"[DEBUG] حذف أقدم رسالة محفوظة من القائمة: {removed}")

# # دالة تنضيف
# def clean_messages(chat_id):
#     print("[INFO] بدأ التنظيف...")
#     sent_message_response = bot.send_message(chat_id=chat_id, text="جارِ التنظيف...")
#     sent_message_id = sent_message_response.get('message', {}).get('body', {}).get('mid')
#     if sent_message_id:
#         save_message(chat_id, sent_message_id, from_bot=True)  # رسالة البوت

#     messages_to_delete = last_messages_per_chat.get(chat_id, [])[-100:]
#     deleted_count = 0
#     for (mid, from_bot_flag) in messages_to_delete:
#         # تجاهل رسالة التنظيف (حسب معرف الرسالة فقط)
#         if mid == sent_message_id:
#             print(f"[DEBUG] تخطي حذف رسالة التنظيف ID={mid}")
#             continue
#         try:
#             print(f"[DEBUG] محاولة حذف رسالة ID=({mid}, {from_bot_flag})")
#             bot.delete_message(mid)
#             deleted_count += 1
#             print(f"[INFO] ✅ تم حذف الرسالة ID=({mid}, {from_bot_flag})")
#         except Exception as e:
#             print(f"[ERROR] فشل حذف رسالة ID=({mid}, {from_bot_flag}): {e}")

#     # إزالة الرسائل المحذوفة من القائمة مع الاحتفاظ برسالة التنظيف
#     last_messages_per_chat[chat_id] = [
#         (mid, fb) for (mid, fb) in last_messages_per_chat[chat_id]
#         if (mid, fb) not in messages_to_delete or mid == sent_message_id
#     ]

#     bot.send_message(chat_id=chat_id, text=f"اكتمل التنظيف. تم حذف {deleted_count} رسالة.")
#     print(f"[INFO] اكتمل التنظيف. تم حذف {deleted_count} رسالة.")
# تخزين آخر الرسائل لكل محادثة
# ==============================
# ==============================
# # ✅ متغير عالمي لتخزين آخر الرسائل لكل محادثة
# last_messages_per_chat = {}
# ✅ مصفوفة لحفظ الرسائل لكل محادثة
last_messages_per_chat = {}
import uuid

# ========= متغير تخزين الرسائل (global)
# كل عنصر: (mid, from_bot:bool, ts:float)
last_messages_per_chat = {}

# -----------------------------
def save_message(chat_id, mid, from_bot=False, ts=None):
    """حفظ أي رسالة واردة أو مُرسلة. نضيف طابع زمني للمساعدة بالـ polling."""
    if not chat_id or not mid:
        print(f"[WARNING] save_message استلم قيم فارغة: chat_id={chat_id}, mid={mid}")
        return

    if ts is None:
        ts = time.time()

    chat_list = last_messages_per_chat.setdefault(chat_id, [])

    # تجنّب التكرار بنفس mid
    if any(existing_mid == mid for existing_mid, _, _ in chat_list):
        print(f"[DEBUG] تم تخطي تسجيل رسالة مكررة: mid={mid}")
        return

    chat_list.append((mid, from_bot, ts))
    print(f"[DEBUG] تم تسجيل رسالة: chat_id={chat_id}, mid={mid}, from_bot={from_bot}, ts={ts}")
    # نحافظ على آخر 200 عنصر (قابل للتعديل)
    if len(chat_list) > 200:
        removed = chat_list.pop(0)
        print(f"[TRACE] إزالة رسالة قديمة من الذاكرة: {removed}")

# -----------------------------
def on_new_message(update):
    """تُستدعى عند استقبال أي تحديث جديد (message_created) — تحفظ الرسائل الواردة."""
    try:
        message_obj = update.get("message", {})
        chat_id = message_obj.get("recipient", {}).get("chat_id")
        body = message_obj.get("body", {})
        mid = body.get("mid")
        sender = message_obj.get("sender", {})
        is_bot = sender.get("is_bot", False)

        if not chat_id or not mid:
            print(f"[WARNING] on_new_message: بيانات ناقصة، لن يتم الحفظ: chat_id={chat_id}, mid={mid}")
            return

        save_message(chat_id, mid, from_bot=bool(is_bot), ts=time.time())
        print(f"[INFO] on_new_message: سجلنا mid={mid}, is_bot={is_bot}")

    except Exception as e:
        print(f"[ERROR] on_new_message فشل: {e}")

# -----------------------------
def send_and_track(chat_id, text, wait_for_update_sec=2.0):
    """
    إرسال رسالة البوت مع محاولة موثوقة للحصول على MID فعلي.
    ستطبع الاستجابة الكاملة. إن لم تُرجع الاستجابة MID، سننتظر وصول تحديث رسالة البوت.
    """
    try:
        print(f"[DEBUG] send_and_track: إرسال نص إلى chat_id={chat_id} text={text!r}")
        response = bot.send_message(chat_id=chat_id, text=text)
        print("[DEBUG] Response from send_message:", response)

        # محاولة استخراج mid من response
        mid = None
        try:
            mid = response.get("message", {}).get("body", {}).get("mid")
        except Exception:
            mid = None

        if mid:
            print(f"[DEBUG] send_and_track: MID مُستخرج من الاستجابة: {mid}")
            save_message(chat_id, mid, from_bot=True, ts=time.time())
            return {"response": response, "mid": mid, "source": "response"}

        # لو لم نتحصل على mid مباشرة — نستخدم polling قصير لالتقاط تحديث رسالة البوت
        print("[WARNING] send_and_track: لم يتم العثور على MID في الاستجابة، سننتظر وصول تحديث رسالة البوت (polling)...")
        start = time.time()
        found_mid = None

        # راقب أي mid جديد مُسجل من نوع from_bot في الفترة الزمنية بعد الإرسال
        while time.time() - start < wait_for_update_sec:
            time.sleep(0.15)  # فاصل صغير
            chat_list = last_messages_per_chat.get(chat_id, [])
            # نبحث عن أول رسالة from_bot تمت بعد بداية الإرسال
            for (m_mid, m_from_bot, m_ts) in reversed(chat_list):
                # لو كان من بوت وتم إضافته بعد start
                if m_from_bot and m_ts >= start - 0.1:
                    found_mid = m_mid
                    break
            if found_mid:
                break

        if found_mid:
            print(f"[DEBUG] send_and_track: MID تم التقاطه عبر التحديث: {found_mid}")
            return {"response": response, "mid": found_mid, "source": "update"}
        else:
            # لم نعثر على MID حقيقي — نسجل مُعرّف بديل لكن نعلمك بالتحذير
            fake_mid = f"bot-fake-{uuid.uuid4()}"
            print(f"[ERROR] send_and_track: لم يوصل MID فعلي. تسجيل MID وهمي: {fake_mid}")
            save_message(chat_id, fake_mid, from_bot=True, ts=time.time())
            return {"response": response, "mid": fake_mid, "source": "fake"}

    except Exception as e:
        print(f"[ERROR] send_and_track فشل إرسال رسالة: {e}")
        return {"response": None, "mid": None, "error": str(e)}

# -----------------------------
def print_storage(chat_id=None):
    """طباعة تخزين الرسائل الحالي لمتابعة السبب. إذا chat_id None -> يطبع كل التخزين."""
    if chat_id is None:
        print("[TRACE] كل التخزين last_messages_per_chat:")
        for c, lst in last_messages_per_chat.items():
            print(f"  chat_id={c}: {lst}")
    else:
        print(f"[TRACE] محتويات last_messages_per_chat[{chat_id}]: {last_messages_per_chat.get(chat_id, [])}")

# -----------------------------
def clean_messages(chat_id, delete_delay=0.05):
    """
    حذف كل الرسائل المُخزنة للمحادثة (من المستخدم والبوت).
    يستخدم bot.delete_message(mid) — MID فقط كما في أمر 'مسح رساله'.
    يعرض طباعات مفصّلة لكل محاولة.
    """
    print("[INFO] بدء عملية التنظيف...")
    messages_to_delete = list(last_messages_per_chat.get(chat_id, []))  # نسخة
    print(f"[TRACE] الرسائل قبل الحذف ({len(messages_to_delete)}): {messages_to_delete}")

    deleted_count = 0
    failed = []

    for mid, from_bot, ts in messages_to_delete:
        try:
            print(f"[DEBUG] محاولة حذف الرسالة mid={mid} | from_bot={from_bot}")
            # نمرر MID فقط — هذه الطريقة تعمل عندك في أمر 'مسح رساله'
            result = bot.delete_message(mid)
            print(f"[DEBUG] نتيجة delete_message(mid={mid}): {result!r}")
            # ملاحظة: بعض مكتبات API تُرجع None حتى لو نجحت؛ لذلك لا نعتمد فقط على ال-return.
            deleted_count += 1
            # فاصل بسيط حتى لا نغمر الـ API بركض سريع
            time.sleep(delete_delay)
        except Exception as e:
            print(f"[ERROR] فشل حذف الرسالة mid={mid}: {e}")
            failed.append((mid, str(e)))

    # بعد المحاولة، ننظف التخزين (أو نترك الفاشلة حسب رغبتك)
    last_messages_per_chat[chat_id] = []
    print(f"[INFO] ✅ اكتمل التنظيف، مجموع الرسائل التي حاولنا حذفها: {deleted_count}")
    if failed:
        print(f"[WARNING] فشل حذف {len(failed)} رسائل: {failed}")
    print(f"[TRACE] القائمة بعد التنظيف: {last_messages_per_chat.get(chat_id, [])}")

# # ==============================
# # ✅ دالة حفظ الرسائل (موحدة، تدعم from_bot=True/False)
# def save_message(chat_id, message_id, from_bot=False):
#     if chat_id not in last_messages_per_chat:
#         last_messages_per_chat[chat_id] = []
#         print(f"[DEBUG] إنشاء قائمة جديدة للمحادثة chat_id={chat_id}")

#     # تحقق من التكرار
#     if any(mid == message_id for mid, _ in last_messages_per_chat[chat_id]):
#         print(f"[DEBUG] تم تخطي تسجيل رسالة مكررة ID={message_id}, from_bot={from_bot}")
#         return

#     # تسجيل الرسالة
#     last_messages_per_chat[chat_id].append((message_id, from_bot))
#     print(f"[DEBUG] تم تسجيل رسالة: chat_id={chat_id}, message_id={message_id}, from_bot={from_bot}")
#     print(f"[TRACE] قائمة الرسائل الحالية: {last_messages_per_chat[chat_id]}")

# # ==============================
# # ✅ دالة إرسال رسالة بوت وحفظها تلقائيًا مع تتبع كامل
# def send_and_track(chat_id, text):
#     try:
#         response = bot.send_message(chat_id=chat_id, text=text)
#         print("[DEBUG] Response from send_message:", response)

#         # محاولة جلب MID بشكل موثوق
#         mid = None
#         if "message" in response and "body" in response["message"]:
#             mid = response["message"]["body"].get("mid")
#         if not mid:
#             print("[WARNING] لم يتم العثور على MID، توليد مؤقت")
#             import uuid
#             mid = f"bot-{uuid.uuid4()}"

#         print(f"[DEBUG] MID لرسالة البوت: {mid}")
#         save_message(chat_id, mid, from_bot=True)
#         return response
#     except Exception as e:
#         print(f"[ERROR] فشل إرسال رسالة البوت: {e}")
#         return {}

# def clean_messages(chat_id):
#     print("[INFO] بدأ التنظيف...")
#     messages_to_delete = last_messages_per_chat.get(chat_id, [])
#     print(f"[TRACE] قائمة الرسائل قبل التنظيف: {messages_to_delete}")

#     deleted_count = 0
#     for mid, from_bot in messages_to_delete:
#         try:
#             result = bot.delete_message(mid)
#             print(f"[INFO] تم حذف الرسالة ID={mid} | from_bot={from_bot} | result={result}")
#             deleted_count += 1
#         except Exception as e:
#             print(f"[ERROR] فشل حذف رسالة ID={mid}: {e}")

#     last_messages_per_chat[chat_id] = []
#     print(f"[INFO] اكتمل التنظيف. تم حذف {deleted_count} رسالة.")

# # ==============================
# # ✅ دالة تنظيف كل الرسائل (بوت + مستخدم)
# def clean_messages(chat_id):
#     print("[INFO] بدأ التنظيف...")
#     messages_to_delete = last_messages_per_chat.get(chat_id, [])
#     print(f"[TRACE] عدد الرسائل قبل الحذف: {len(messages_to_delete)}")
#     print(f"[TRACE] الرسائل قبل الحذف: {messages_to_delete}")

#     deleted_count = 0
#     for mid, from_bot in messages_to_delete:
#         try:
#             print(f"[DEBUG] محاولة حذف رسالة ID={mid} | from_bot={from_bot}")
#             result = bot.delete_message(mid)
#             print(f"[DEBUG] نتيجة delete_message: {result}")
#             deleted_count += 1
#         except Exception as e:
#             print(f"[ERROR] فشل حذف رسالة ID={mid}: {e}")
#             # إذا لم ينجح الحذف الفعلي، سجلها كمحذوف داخليًا
#             print(f"[INFO] ✅ علامة حذف داخلي فقط للرسالة ID={mid}")

#     # بعد الحذف، تنظيف القائمة بالكامل
#     last_messages_per_chat[chat_id] = []
#     print(f"[INFO] اكتمل التنظيف. إجمالي الرسائل التي حاولنا حذفها: {deleted_count}")
#     print(f"[TRACE] الرسائل المتبقية في chat_id={chat_id}: {last_messages_per_chat[chat_id]}")

# ==============================
# ✅ دالة طباعة كل الرسائل لتتبع الوضع الحالي
def print_all_messages(chat_id):
    print(f"[INFO] جميع الرسائل في chat_id={chat_id}:")
    for mid, from_bot in last_messages_per_chat.get(chat_id, []):
        role = "BOT" if from_bot else "USER"
        print(f" - {role} | ID={mid}")

# ================= قاعدة البيانات =================
# =================بداية داله حفظ الترحيب=============
def save_welcomes(welcome_messages):
    try:
        with open("welcome_messages.json", "w", encoding="utf-8") as f:
            json.dump(welcome_messages, f, ensure_ascii=False, indent=4)
        print("[DEBUG] تم حفظ الترحيب في welcome_messages.json")
    except Exception as e:
        print(f"[ERROR] فشل حفظ الترحيب: {e}")
# =================نهاية  داله حفظ  الترحيب=============
# دالة الحذف الموحده لاحد الرتب
def remove_role_from_db(user_id, role=None, group_id="global",priority=0):
    """
    حذف رتبة مستخدم من جدول roles
    - إذا role=None يحذف المستخدم بالكامل من الجدول (بغض النظر عن رتبته).
    - إذا role محدد، يحذف فقط تلك الرتبة.
    """
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            if role:
                cursor.execute("""
                    DELETE FROM roles WHERE user_id=? AND role=? AND group_id=?
                """, (str(user_id), role, group_id))
            else:
                cursor.execute("""
                    DELETE FROM roles WHERE user_id=? AND group_id=?
                """, (str(user_id), group_id))
            changes = cursor.rowcount
        if changes > 0:
            print(f"[INFO] ✅ تم حذف {role or 'كل الرتب'} للمستخدم ID={user_id}")
        else:
            print(f"[INFO] ℹ️ المستخدم ID={user_id} غير موجود بالرتبة {role or 'أي رتبة'}")
        return changes > 0
    except Exception as e:
        print(f"[ERROR] ❌ خطأ أثناء حذف الرتبة: {e}")
        return False

# دالة الحذف الموحده لجميع الاعضاء في رتبه واحده في المجوعه
def remove_all_roles(role, group_id="global",priority=0):
    """حذف جميع المستخدمين من رتبة محددة"""
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM roles WHERE role=? AND group_id=? AND priority = ?
            """, (role, group_id , priority))
        print(f"[INFO] ✅ تم حذف جميع {role} من قاعدة البيانات")
    except Exception as e:
        print(f"[ERROR] ❌ خطأ أثناء مسح {role}: {e}")

# داله عرض الاعضاء الموجودين ب احد الرتب
def list_roles(role, group_id="global",priority=0):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fullname, username 
                FROM roles
                WHERE role LIKE ? AND group_id = ? AND priority = ?
            """, (f"%{role}%", str(group_id) , priority))
            rows = cursor.fetchall()

        if not rows:
            if role == "حماية":
                return "ℹ️ لا يوجد محميين مسجلين."
            else:
                return f"ℹ️ لا يوجد {role}ين مسجلين."
        else:
            if role == "حماية":
                lines = ["🛡️ قائمة المحميين:\n"]
            else:
                lines = [f"👥 قائمة {role}ين:\n"]

            for idx, (fullname, username) in enumerate(rows, 1):
                if username:
                    lines.append(f"{idx}. {fullname} (@{username})")
                else:
                    lines.append(f"{idx}. {fullname}")

            return "\n".join(lines)

    except Exception as e:
        return f"❌ خطأ أثناء جلب {role}ين: {e}"




#================== بداية أوامر المطور الأساسي=====================
last_messages_per_chat = {}
def handle_main_dev_commands(update, text, chat_id, message_id, user_id):
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)
    updates = update.get("updates", [])
    msg = updates[0].get("message", {}) if updates else {}
    # ===== تحقق من صلاحيات أوامر المطورين =====
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM roles 
                WHERE user_id=? AND priority =1 AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))
            if not cursor.fetchone():
                return  # المستخدم لا يمتلك صلاحية مطور
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من الصلاحيات: {e}", chat_id, message_id)
        return
    # ===== رفع مطور بالرد أو link.reply =====
    if "رفع مطور" in [lower_text, base_command]:
        updates = update.get("updates", [])
        msg = updates[0].get("message", {}) if updates else {}

        # محاولة الحصول على الرسالة التي تم الرد عليها
        reply_msg = None
        new_dev_id = None
        user_name = "مستخدم"
        username = ""

        if "reply_to_message" in msg:
            reply_msg = msg["reply_to_message"]
            sender = reply_msg.get("sender") or reply_msg.get("from") or {}
            new_dev_id = sender.get("user_id")
            user_name = sender.get("name", "مستخدم")
            username = sender.get("username", "")
        elif "link" in msg and msg["link"].get("type") == "reply":
            link = msg["link"]
            reply_msg = link.get("message")
            sender = link.get("sender") or {}
            new_dev_id = sender.get("user_id")
            user_name = sender.get("name", "مستخدم")
            username = sender.get("username", "")

        if not new_dev_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد رفعه كمطور", chat_id, message_id)
        else:
            result_msg = add_role_to_db(
                user_id=new_dev_id,
                fullname=user_name,
                username=username,
                role="مطور",
                priority=2,
                group_id="global",
                added_by_admin=1
            )
            send_reply_message(result_msg, chat_id, message_id)

    # ===== تنزيل مطور بالرد =====
    # ===== تنزيل مطور =====
    elif "تنزيل مطور" in [lower_text, base_command]:
        target_user_id = get_target_user_id(update)
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد تنزيله من المطورين", chat_id, message_id)
        else:
            if remove_role_from_db(target_user_id, "مطور", group_id="global",priority=2):
                send_reply_message("✅ تم تنزيل المطور من القائمة.", chat_id, message_id)
            else:
                send_reply_message("ℹ️ المستخدم غير موجود كمطور.", chat_id, message_id)

    # ===== مسح جميع المطورين =====
    elif "مسح مطورين" in [lower_text, base_command]:
        try:
            remove_all_roles("مطور", group_id="global",priority=2)
            send_reply_message("✅ تم حذف جميع المطورين من قاعدة البيانات.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء مسح المطورين: {e}", chat_id, message_id)

# ========================= بداية داله الاوامر مشتركه الاقل من 4  ==============================
def handle_shared_rank_common_owner_commands(update, text, chat_id, message_id, user_id):
    """
    أوامر مشتركة لجميع المستخدمين ذوي الأولوية <= 4
    (المنشئ الأساسي + المنشئ العادي + أي رتبة مؤهلة)
    """
    if not text:
        return
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)
    state_key = f"{chat_id}:{user_id}"

    # التحقق من أن المستخدم لديه صلاحية <= 4
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM roles
                WHERE user_id=? AND priority <= 4 AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))
            role = cursor.fetchone()
            if not role:
                return  # ليس لديه صلاحية
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من الصلاحيات: {e}", chat_id, message_id)
        return

    # ========== الأوامر المشتركة ==========

    # ===== أمر إضافة ترحيب =====
    if "اضف ترحيب" in [lower_text, base_command]:
        user_command_state_response2[state_key] = {"step": 1, "action": "add_welcome"}
        send_reply_message(
            "✍️ أرسل الآن كليشة الترحيب الجديدة\n"
            "لاستخدام المتغيرات:\n"
            "- لعرض الاسم: #name\n"
            "- لعرض المعرف: #username",
            chat_id,
            message_id
        )
    if state_key in user_command_state_response2:
         handle_reply_state(state_key, lower_text, chat_id, message_id, user_id)

    # ===== معالجة الرسائل الجديدة =====

# =========================  نهاية داله الاوامر مشتركه الاقل من 4  ==============================

# ========================= Response function  ==============================

def Response_function(update, text, chat_id, message_id, user_id):
    if not text:
     return
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)
    state_key = f"{chat_id}:{user_id}"
    # التحقق من أن المستخدم لديه صلاحية <= 4
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM roles
                WHERE user_id=? AND priority <=5 AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))

            role = cursor.fetchone()
            if not role:
                return  # ليس لديه صلاحية
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من الصلاحيات: {e}", chat_id, message_id)
        return

    # ===== أوامر الردود باستخدام الحالة =====
    if "اضف رد" in [lower_text, base_command]:
        user_command_state_response2[state_key] = {"step": 1, "action": "add_reply"}
        send_reply_message("📌 أرسل الكلمة التي تريد ربط رد لها:", chat_id, message_id)
        return

    elif "مسح رد" in [lower_text, base_command]:
        user_command_state_response[state_key] = {"step": 1, "action": "remove_reply"}
        send_reply_message("📌 أرسل الكلمة التي تريد حذف الرد المرتبط بها:", chat_id, message_id)
        return
    elif  "الردود" in [lower_text, base_command]:
        all_replies = reply_manager.get_all_replies(chat_id)
        if not all_replies:
            send_reply_message("⚠ لا توجد ردود محفوظة في هذه المجموعة.", chat_id, message_id)
        else:
            text_list = ["› قائمة الردود ⬇️🔖.", "— — — — — — — — —"]
            for idx, (keyword, response) in enumerate(all_replies.items(), start=1):
                text_list.append(f"{idx}- {keyword} -> {response}")
            final_text = "\n".join(text_list)
            send_reply_message(final_text, chat_id, message_id)
        return
    # ===== أمر مسح كل الردود =====
    elif  "مسح الردود" in [lower_text, base_command]:
        if reply_manager.delete_all_replies(chat_id):  # نفترض أن هذه الدالة موجودة في reply_manager
            send_reply_message(
                "🗑️ تم مسح جميع الردود الخاصة بهذه المجموعة.",
                chat_id,
                message_id
            )
            print(f"[DEBUG] تم مسح كل الردود للمجموعة {chat_id}")
        else:
            send_reply_message(
                "⚠️ لا توجد ردود محفوظة لهذه المجموعة.",
                chat_id,
                message_id
            )
            print(f"[TRACE] لم يتم العثور على ردود للمجموعة {chat_id}")
        return

    # ===== إذا كان المستخدم في حالة انتظار =====
    # state_key = f"{chat_id}:{user_id}"
    if state_key in user_command_state_response2:
        handle_reply_state(state_key, lower_text, chat_id, message_id, user_id)

# =========================  Response function  ==============================
# ================== (المدير)بداية دالة اوامر المنشئ  ====================
def handle_Manager_command(update, text, chat_id, message_id, user_id):
    """
    أوامر المنشئ (المدير) للتحكم بالادمنية
    """
    if text is None:
        return

    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)

    # تحقق إن المرسل منشئ أو أعلى (priority <= 4)
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM roles 
                WHERE user_id=? AND priority <= 4 AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))

            if not cursor.fetchone():
                return  # ليس منشئ أو أعلى
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من الصلاحيات: {e}", chat_id, message_id)
        return

    # الحصول على بيانات المستخدم المردود عليه
    updates = update.get("updates", [])
    msg = updates[0].get("message", {}) if updates else {}

    sender = {}
    if "reply_to_message" in msg:
        reply_msg = msg.get("reply_to_message", {})
        sender = reply_msg.get("sender") or reply_msg.get("from") or {}
    elif "link" in msg and msg.get("link", {}).get("type") == "reply":
        sender = msg["link"].get("sender") or {}

    target_user_id = str(sender.get("user_id", ""))
    target_name = sender.get("name", "مستخدم")
    username = sender.get("username", "")

    # ===== رفع ادمن =====
    if "رفع ادمن" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد رفعه.", chat_id, message_id)
            return

        msg_text = add_role_to_db(
            user_id=target_user_id,
            fullname=target_name,
            username=username,
            role="ادمن",
            priority=5,
            group_id=str(chat_id),
            added_by_admin=1
        )
        send_reply_message(msg_text, chat_id, message_id)

    # ===== تنزيل ادمن =====
    elif "تنزيل ادمن" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد تنزيله.", chat_id, message_id)
            return

        if remove_role_from_db(user_id=target_user_id, role="ادمن", group_id=str(chat_id), priority=5):
            send_reply_message(f"✅ تم تنزيل المستخدم {target_name} من رتبة ادمن.", chat_id, message_id)
        else:
            send_reply_message(f"ℹ️ المستخدم {target_name} ليس ادمنًا.", chat_id, message_id)

    # ===== عرض الادمنية =====
    elif "الادمنية" in [lower_text, base_command]:
        reply_text = list_roles("ادمن", group_id=str(chat_id), priority=5)
        send_reply_message(reply_text, chat_id, message_id)

    # ===== مسح الادمنية =====
    elif "مسح الادمنية" in [lower_text, base_command]:
        try:
            remove_all_roles("ادمن", group_id=str(chat_id), priority=5)
            send_reply_message("✅ تم مسح جميع الادمنية من المجموعة.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء مسح الادمنية: {e}", chat_id, message_id)
    elif lower_text in ["طرد البوتات", "طرد بوتات"]:
        print(f"[DEBUG] الأمر 'طرد البوتات' استُدعي في المجموعة {chat_id} من {user_id}")

        kicked = kick_all_bots(bot, chat_id, user_id, message_id)
        if kicked:
            msg = "✅ تم طرد جميع البوتات من المجموعة."
            print(f"[RESULT] {msg}")
            bot.send_reply_message(msg, chat_id, message_id)
        else:
            msg = "ℹ️ ماكو بوتات بالمجموعة حتى تنطرد."
            print(f"[RESULT] {msg}")
            bot.send_reply_message(msg, chat_id, message_id)

# =========================== نهاية اوامر المنشئ(المدير) ======================
# =======================بداية دالة جلب الرتب  =======================
import sqlite3

def get_user_priority(chat_id, user_id, message_id=None):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT priority FROM roles 
                WHERE user_id=? AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))    
            row = cursor.fetchone()
            user_priority = row[0] if row else 99  # عضو عادي افتراضي
            if user_priority <= 5:
                return 99  # نرجع أضعف صلاحية بدل None
            return user_priority
    except Exception as e:
        if message_id:
            send_reply_message(f"❌ خطأ في التحقق: {e}", chat_id, message_id)
        return 99  # افتراضي في حال الخطأ

# ======================= نهااية دالة جلب الرتب=======================
# ================== إدارة حالات الأوامر المتعددة الخطوات ==================
user_command_state = {} 

def handle_command_state(state_key, lower_text, chat_id, message_id, user_id):
    """
    إدارة حالة الأوامر (اضف امر / امسح امر).
    state_key = (str(chat_id), str(user_id))
    """
    # تحقق إذا كانت الحالة موجودة قبل أي شيء
    if state_key not in user_command_state:
        send_reply_message("⚠️ لا توجد عملية نشطة لهذا المستخدم.", chat_id, message_id)
        return

    state = user_command_state[state_key]
    step = state.get("step")
    action = state.get("action")

    # ===== الخطوة الأولى: تحديد الأمر الأساسي =====
    if step == 1:
        base_command = lower_text.strip()

        # تحقق إذا الأمر موجود فعلاً
        if base_command not in COMMANDS_REQUIRED_PRIORITY:
            send_reply_message(f"❌ الأمر الأساسي '{base_command}' غير موجود.", chat_id, message_id)
            user_command_state.pop(state_key, None)
            return

        # تحقق من الصلاحيات
        required_priority = COMMANDS_REQUIRED_PRIORITY[base_command]
        user_priority = get_user_priority(chat_id, user_id)
        if user_priority is None:
            user_priority = 99  # عضو عادي افتراضي

        if user_priority <= required_priority:
            send_reply_message(f"❌ ليس لديك صلاحيات لإضافة/حذف مرادف لـ '{base_command}'.", chat_id, message_id)
            user_command_state.pop(state_key, None)
            return

        # جلب المرادفات الحالية
        current_aliases = get_command_aliases(base_command, str(chat_id))

        if action == "add_alias":
            if len(current_aliases) >= 3:
                send_reply_message("❌ لا يمكن إضافة أكثر من 3 مرادفات.", chat_id, message_id)
                user_command_state.pop(state_key, None)
                return
            send_reply_message(f"📌 أرسل المرادف الجديد للأمر '{base_command}'", chat_id, message_id)

        elif action == "remove_alias":
            if not current_aliases:
                send_reply_message("ℹ️ لا يوجد مرادفات لحذفها.", chat_id, message_id)
                user_command_state.pop(state_key, None)
                return
            aliases_list = "\n".join(f"- {alias}" for alias in current_aliases)
            send_reply_message(
                f"📌 مرادفات '{base_command}':\n{aliases_list}\n✏️ أرسل المرادف الذي تريد حذفه.",
                chat_id, message_id
            )

        # حفظ التقدم
        user_command_state[state_key]["step"] = 2
        user_command_state[state_key]["base_command"] = base_command

    # ===== الخطوة الثانية: استقبال المرادف =====
    elif step == 2:
        base_command = state.get("base_command")
        target_alias = lower_text.strip()

        if not base_command:
            send_reply_message("❌ خطأ: لم يتم تحديد الأمر الأساسي بشكل صحيح.", chat_id, message_id)
            user_command_state.pop(state_key, None)
            return

        if action == "add_alias":
            msg_text = add_command_alias(base_command, target_alias, str(chat_id), added_by=str(user_id))
        elif action == "remove_alias":
            msg_text = remove_command_alias(base_command, target_alias, str(chat_id))
        else:
            msg_text = "❌ خطأ داخلي: نوع العملية غير معروف."

        send_reply_message(msg_text, chat_id, message_id)
        user_command_state.pop(state_key, None)

    else:
        send_reply_message("⚠️ خطوة غير معروفة في إدارة الأوامر.", chat_id, message_id)
        user_command_state.pop(state_key, None)
# def check_protection_status(chat_id):
#     try:
#         conn = sqlite3.connect("bot_data.sqlite")
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT p.name, gps.status
#             FROM group_protection_settings gps
#             JOIN protections p ON gps.protection_id = p.id
#             WHERE gps.group_id = ?
#         """, (str(chat_id),))
#         rows = cursor.fetchall()
#         conn.close()

#         if not rows:
#             print("ℹ️ لا توجد إعدادات حماية لهذه المجموعة.")
#         else:
#             for name, status in rows:
#                 print(f"{name} ➜ {'✅ مفتوح' if status == 1 else '❌ مغلق'}")
#     except Exception as e:
#         print(f"❌ خطأ أثناء جلب أوامر الحماية: {e}")

# # استدعاء الدالة
# check_protection_status(-104601244926120)

# ======================= =======================
# ================== بداية اوامر الادمنية  ====================
# user_command_state = {} 
def handle_distinguished_members(update, text, chat_id, message_id, user_id):
    """
    إدارة الأعضاء المميزين باستخدام الدوال العامة.
    """
    if text is None:
        return
    state_key = (str(chat_id), str(user_id))
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)

    # ===== تحقق من صلاحيات استخدام الأوامر (ادمن أو أعلى) =====
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT priority FROM roles 
                WHERE  user_id=? AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))
            row = cursor.fetchone()
            user_priority = row[0] if row else 99  # عضو عادي افتراضي
            if user_priority > 5:
                return  # ليس ادمن أو أعلى
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق: {e}", chat_id, message_id)
        return

    # ===== عرض قائمة الأوامر الرئيسية =====
    if lower_text in ["الاوامر", "م1", "م2", "م3","م4"]:
        # بيانات البوت
        BOT_NAME = bot.get_bot_name()
        BOT_USER = '@' + bot.get_bot_username()


        if lower_text == "الاوامر":
            reply = (
                "⊰❳ - هناك 〈𝟒⦒ اوامر للعرض\n"
                "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                "⧔︙م1 -› لعرض اوامر الحماية\n"
                "﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎\n"
                "⧔︙م2 -› لعرض اوامر المنشئين / الادمنية\n"
                "﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎\n"
                "⧔︙م3 -› لعرض اوامر المطورين 👨🏻‍💻\n"
                "﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎\n"
                "⧔︙م4 -› لعرض الاوامر العامة 🌐\n"
                "﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎\n"
                f"•━━━━━ ِ{BOT_NAME} ━━━━━•\n"
                "➹ all protection orders\n"
                f"⌫︎- For more➙({BOT_USER})"
            )

            bot.send_reply_message(text=reply, chat_id=chat_id, mid=message_id)
            return
        elif "م4" in [lower_text, base_command]:
            # الأوامر العامة (index 6)
            cmds_general = ROLES_COMMANDS[6]

            reply = "⌁︙الأوامر العامة ↯.↯.\n"
            reply += "━─━─────━─────━─━\n"
            reply += "\n".join(f"› {cmd}" for cmd in cmds_general) + "\n"
            reply += "— — — — — — — — —"

            bot.send_reply_message(text=reply, chat_id=chat_id, mid=message_id)
            return

        # ===== أوامر الم1 / م2 / م3 حسب الرتب =====
        elif "م3" in  [lower_text, base_command]:
            # أوامر المطور الأساسي (index 1)
            cmds_basic = ROLES_COMMANDS[1]
            # أوامر المطور 2 (index 2)
            cmds_dev2 = ROLES_COMMANDS[2]

            reply = "⌁︙اوامر مطورين البوت ↯.↯.\n"
            reply += "━─━─────━─────━─━\n"
            reply += "› #اوامر المطور الاساسي\n— — — — —\n"
            reply += "\n".join(f"› {cmd}" for cmd in cmds_basic) + "\n"
            reply += "— — — — — — — — —\n"
            reply += "› #اوامر - المطور 2.\n— — — —\n"
            reply += "\n".join(f"› {cmd}" for cmd in cmds_dev2) + "\n"
            reply += "— — — — — — — — —"

            bot.send_reply_message(text=reply, chat_id=chat_id, mid=message_id)
            return


        elif lower_text == "م2":
            reply = "#اوامر_المنشئ الاساسي↫⤈\nٴ━──⬇️──━ٴ\n"
            reply += "\n".join(f"✵│{cmd}" for cmd in ROLES_COMMANDS[3]) + "\n"
            reply += "ٴ━───━ ✵ ━───━\n"
            reply += "#اوامر المنشـئين : ↫مدير\nٴ━──⬇️──━ٴ\n"
            reply += "\n".join(f"✵│{cmd}" for cmd in ROLES_COMMANDS[4]) + "\n"
            reply += "ٴ━───━ ✵ ━───━ٴ\n"
            reply += "#اوامر الادمنيه↫⤈\nٴ━──⬇️──━ٴ\n"
            reply += "\n".join(f"✵│{cmd}" for cmd in ROLES_COMMANDS[5]) + "\n"
            reply += "— — — — — — — — —\n› جميع الاوامر بـالبوت الاقل رتبة منه."
            bot.send_reply_message(text=reply, chat_id=chat_id, mid=message_id)
            return

    # ===== الحصول على المستخدم المردود عليه =====
    # ===== استخراج البيانات الموحدة =====
    updates = update.get("updates", [])
    msg = updates[0].get("message", {}) if updates else {}
    sender = {}
    if "reply_to_message" in msg:
        reply_msg = msg.get("reply_to_message", {})
        sender = reply_msg.get("sender") or reply_msg.get("from") or {}
    elif "link" in msg and msg["link"].get("type") == "reply":
        link = msg["link"]
        sender = link.get("sender") or {}

    target_user_id = str(sender.get("user_id", ""))
    target_name = sender.get("name", "مستخدم")
    username = sender.get("username", "")
    # ===== مرحلة "اضف امر" =====

    if lower_text == "اضف امر":
          send_reply_message("📌 أرسل الآن الأمر الأساسي الذي تريد إضافة له مرادف:", chat_id, message_id)
          user_command_state[state_key] = {"step": 1, "action": "add_alias"}
          return

    if lower_text == "امسح امر":
          send_reply_message("📌 أرسل الآن الأمر الأساسي الذي تريد حذف مرادف له:", chat_id, message_id)
          user_command_state[state_key] = {"step": 1, "action": "remove_alias"}
          return



    # ===== رفع عضو مميز =====
    if "رفع مميز" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد رفعه.", chat_id, message_id)
            return
        msg_text = add_role_to_db(
            user_id=target_user_id,
            fullname=target_name,
            username=username,
            role="عضو مميز",
            priority=6,
            group_id=str(chat_id),
            added_by_admin=1
        )
        send_reply_message(msg_text, chat_id, message_id)

    # ===== تنزيل عضو مميز =====
    elif "تنزيل مميز" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد تنزيله.", chat_id, message_id)
            return
        if remove_role_from_db(user_id=target_user_id, role="عضو مميز", group_id=str(chat_id), priority=6):
            send_reply_message(f"✅ تم تنزيل المستخدم {target_name} من رتبة الأعضاء المميزين.", chat_id, message_id)
        else:
            send_reply_message(f"ℹ️ المستخدم {target_name} ليس عضو مميز.", chat_id, message_id)

    # ===== مسح جميع الأعضاء المميزين =====
    elif "مسح المميزين" in [lower_text, base_command]:
        try:
            remove_all_roles("عضو مميز", group_id=str(chat_id), priority=6)
            send_reply_message("✅ تم مسح جميع الأعضاء المميزين من هذه المجموعة.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء مسح الأعضاء المميزين: {e}", chat_id, message_id)

    # ===== عرض جميع الأعضاء المميزين =====
    elif "المميزين" in [lower_text, base_command]:
        try:
            reply_text = list_roles("عضو مميز", group_id=str(chat_id), priority=6)
            if not reply_text:
                reply_text = "ℹ️ لا يوجد أعضاء مميزين في هذه المجموعة."
            send_reply_message(reply_text, chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء جلب الأعضاء المميزين: {e}", chat_id, message_id)
    elif "طرد" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد طرده.", chat_id, message_id)
            return
        try:
            with sqlite3.connect("bot_data.sqlite") as conn:
                cursor = conn.cursor()

                # جلب أولوية المنفذ
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                executor_priority = cursor.fetchone()
                executor_priority = executor_priority[0] if executor_priority else 99

                # جلب أولوية الهدف
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE user_id=? AND group_id IN (?, 'global')
                    """, (str(target_user_id), str(chat_id)))
                target_priority = cursor.fetchone()
                target_priority = target_priority[0] if target_priority else 99

            # تحقق من حماية الشخص المستهدف
            is_protected = is_user_protected(target_user_id, chat_id)
            executor_is_owner, owner_name = is_executor_primary_owner(str(user_id), str(chat_id))
            group_owner_name = get_primary_owner_name(chat_id)  # اسم المنشئ لعرضه عند الحماية

            # إذا الشخص محمي والمنفذ ليس منشئ أساسي
            if is_protected and not executor_is_owner:
                send_reply_message(
                    f"⊰❳ عذرآ تم تفعيل الحماية للشخص : \n"
                    f"┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                    f"🛡️ بواسطة: {group_owner_name}",
                    chat_id,
                    message_id
                )
                return



            # تحقق من الصلاحيات العادية
            if executor_priority > target_priority:
                send_reply_message("❌ لا يمكنك طرد هذا المستخدم لأنه أعلى رتبة منك.", chat_id, message_id)
                return

            # تنفيذ الطرد
            bot.remove_member(chat_id, target_user_id)
            send_reply_message(f"🚫 تم طرد المستخدم {target_name}.", chat_id, message_id)

        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء طرد المستخدم: {e}", chat_id, message_id)


    # ===== حظر عضو =====
    elif "حظر" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد حظره.", chat_id, message_id)
            return
        try:
            with sqlite3.connect("bot_data.sqlite") as conn:
                cursor = conn.cursor()
                # جلب أولوية المنفذ
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE  user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                executor_priority = cursor.fetchone()
                executor_priority = executor_priority[0] if executor_priority else 99

                # جلب أولوية الهدف
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE  user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                target_priority = cursor.fetchone()
                target_priority = target_priority[0] if target_priority else 99
            is_protected = is_user_protected(target_user_id, chat_id)
            executor_is_owner, owner_name = is_executor_primary_owner(str(user_id), str(chat_id))
            group_owner_name = get_primary_owner_name(chat_id)  # اسم المنشئ لعرضه عند الحماية

            # إذا الشخص محمي والمنفذ ليس منشئ أساسي
            if is_protected and not executor_is_owner:
                send_reply_message(
                    f"⊰❳ عذرآ تم تفعيل الحماية للشخص : \n"
                    f"┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                    f"🛡️ بواسطة: {group_owner_name}",
                    chat_id,
                    message_id
                )
                return


            # تحقق من الصلاحيات
            if executor_priority > target_priority:
                send_reply_message("❌ لا يمكنك حظر هذا المستخدم لأنه أعلى رتبة منك.", chat_id, message_id)
                return

            bot.ban_member(chat_id, target_user_id)
            send_reply_message(f"⛔ تم حظر المستخدم {target_name}.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء حظر المستخدم: {e}", chat_id, message_id)

    # ===== تثبيت رسالة =====
    # ===== تثبيت الرسالة =====
    elif "تثبيت" in [lower_text, base_command]:
        # تحقق من وجود رد
        if not msg.get("link") or msg["link"].get("type") != "reply":
            send_reply_message("❌ يجب الرد على الرسالة التي تريد تثبيتها.", chat_id, message_id)
            return

        try:
            # جلب معرف الرسالة المُراد تثبيتها
            reply_message_id = msg["link"]["message"]["mid"]

            # تنفيذ التثبيت
            bot.pin_message(chat_id, reply_message_id)

            send_reply_message("📌 تم تثبيت الرسالة بنجاح.", chat_id, message_id)

        except Exception as e:
            send_reply_message(f"❌ حدث خطأ أثناء التثبيت: {e}", chat_id, message_id)

    # ===== إلغاء التثبيت =====
    elif "الغاء التثبيت" in [lower_text, base_command]:
        try:
            bot.unpin_message(chat_id)
            send_reply_message("📌 تم إلغاء تثبيت الرسالة.", chat_id, message_id)
        except Exception as e:
           send_reply_message(f"❌ حدث خطأ أثناء إلغاء التثبيت: {e}", chat_id, message_id)
    elif "تنزيل الكل" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد تنزيله.", chat_id, message_id)
            return
        try:
            with sqlite3.connect("bot_data.sqlite") as conn:
                cursor = conn.cursor()

                # جلب أولوية المنفذ
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE  user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                executor_priority = cursor.fetchone()
                executor_priority = executor_priority[0] if executor_priority else 99

                # جلب أولوية الهدف
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE  user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                target_priority = cursor.fetchone()
                target_priority = target_priority[0] if target_priority else 99
                is_protected = is_user_protected(target_user_id, chat_id)
                executor_is_owner, owner_name = is_executor_primary_owner(str(user_id), str(chat_id))
                group_owner_name = get_primary_owner_name(chat_id)  # اسم المنشئ لعرضه عند الحماية

                # إذا الشخص محمي والمنفذ ليس منشئ أساسي
                if is_protected and not executor_is_owner:
                    send_reply_message(
                        f"⊰❳ عذرآ تم تفعيل الحماية للشخص : \n"
                        f"┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                        f"🛡️ بواسطة: {group_owner_name}",
                        chat_id,
                        message_id
                    )
                    return


                # تحقق من الصلاحيات
                if executor_priority > target_priority:
                    send_reply_message("❌ لا يمكنك تنزيل هذا المستخدم لأنه أعلى رتبة منك.", chat_id, message_id)
                    return

                # إزالة كل الصلاحيات للهدف في هذه المجموعة
                cursor.execute("""
                    DELETE FROM roles 
                    WHERE user_id=? AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))
                conn.commit()

            send_reply_message(f"✅ تم تنزيل جميع صلاحيات المستخدم {target_name}.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء تنزيل المستخدم: {e}", chat_id, message_id)
    elif "تنزيل وطرد" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد تنزيله وطرده.", chat_id, message_id)
            return
        try:
            with sqlite3.connect("bot_data.sqlite") as conn:
                cursor = conn.cursor()

                # جلب أولوية المنفذ
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                executor_priority = cursor.fetchone()
                executor_priority = executor_priority[0] if executor_priority else 99

                # جلب أولوية الهدف
                cursor.execute("""
                    SELECT priority FROM roles 
                    WHERE user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                target_priority = cursor.fetchone()
                target_priority = target_priority[0] if target_priority else 99
                is_protected = is_user_protected(target_user_id, chat_id)
                executor_is_owner, owner_name = is_executor_primary_owner(str(user_id), str(chat_id))
                group_owner_name = get_primary_owner_name(chat_id)  # اسم المنشئ لعرضه عند الحماية

                # إذا الشخص محمي والمنفذ ليس منشئ أساسي
                if is_protected and not executor_is_owner:
                    send_reply_message(
                        f"⊰❳ عذرآ تم تفعيل الحماية للشخص : \n"
                        f"┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                        f"🛡️ بواسطة: {group_owner_name}",
                        chat_id,
                        message_id
                    )
                    return


                # تحقق من الصلاحيات
                if executor_priority > target_priority:
                    send_reply_message("❌ لا يمكنك تنزيل أو طرد هذا المستخدم لأنه أعلى رتبة منك.", chat_id, message_id)
                    return

                # ===== تنزيل كل الصلاحيات =====
                cursor.execute("""
                    DELETE FROM roles 
                    WHERE user_id=? AND group_id IN (?, 'global')
                    """, (str(user_id), str(chat_id)))
                conn.commit()
                # send_reply_message(f"✅ تم تنزيل جميع صلاحيات المستخدم {target_name}.", chat_id, message_id)

            # ===== طرد المستخدم من المجموعة =====
            try:
                bot.remove_member(chat_id, target_user_id)
                send_reply_message(
                    f"✅ تم تنزيل جميع صلاحيات المستخدم {target_name} "
                    f"🚫 وتم طرده من المجموعة.", chat_id, message_id
                )
            except Exception as e:
                send_reply_message(f"⚠ تم تنزيل الصلاحيات ولكن حدث خطأ أثناء الطرد: {e}", chat_id, message_id)

        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء تنزيل وطرد المستخدم: {e}", chat_id, message_id)
    elif lower_text.startswith("قفل ") or lower_text.startswith("اغلاق ") or lower_text.startswith("فتح "):
        words = lower_text.split()
        if len(words) == 2:
            action = words[0]
            protection_name = words[1]
            protections_list = [
                "الروابط", "البوتات", "المتحركه", "الملصقات", "الملفات",
                "الصور", "الفيديو", "الالعاب", "الدردشه", "التوجيه", "الاغاني",
                "الصوت", "الجهات", "الهمسه", "التكرار", "التاك",
                "التعديل", "الفايروس", "الكلايش", "الهايشتاك", "الترحيب",
                "الفشار", "الكل", "الردود","الخصوصية"
            ]
            if protection_name not in protections_list:
                # لا تفعل أي شيء إذا الكلمة غير موجودة
                return
            status = 0 if action in ["قفل", "اغلاق"] else 1

            try:
                if protection_name == "الكل":
                    conn = sqlite3.connect("bot_data.sqlite")
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE group_protection_settings
                        SET status = ?
                        WHERE group_id = ?
                    """, (status, str(chat_id)))
                    conn.commit()
                    conn.close()

                    bot.send_reply_message(
                        text=f"🔒 تم {'قفل' if status == 0 else 'فتح'} جميع أوامر الحماية بنجاح.",
                        chat_id=chat_id,
                        mid=message_id
                    )
                else:
                    set_protection_status(chat_id, protection_name, status)
                    bot.send_reply_message(
                        text=f"🔐 تم {'قفل' if status == 0 else 'فتح'} {protection_name} بنجاح.",
                        chat_id=chat_id,
                        mid=message_id
                    )
            except Exception as e:
                bot.send_reply_message(
                    text=f"❌ حدث خطأ أثناء تعديل الحماية: {e}",
                    chat_id=chat_id,
                    mid=message_id
                )
    elif lower_text in ["اوامر الحماية", "م1", "الاعدادات"] or base_command in ["اوامر الحماية", "م1", "الاعدادات"]:
        try:
            conn = sqlite3.connect("bot_data.sqlite")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, gps.status
                FROM group_protection_settings gps
                JOIN protections p ON gps.protection_id = p.id
                WHERE gps.group_id = ?
            """, (str(chat_id),))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                bot.send_reply_message(
                    text="ℹ️ لا توجد إعدادات حماية لهذه المجموعة.",
                    chat_id=chat_id,
                    mid=message_id
                )
            else:
                # عنوان الرسالة
                message_lines = ["⊰❳ - اوامر الحماية لهذه المجموعة", "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"]

                for name, status in rows:
                    # اختيار الرمز واللون بناءً على الحالة
                    if status == 1:
                        symbol = "🟢"
                        lock_text = "⬅🔓"
                    else:
                        symbol = "🔴"
                        lock_text = "⬅🔒"

                    # إضافة السطر بصيغة جديدة
                    message_lines.append(f"{symbol} ⊰❳ {name} {lock_text}")

                bot.send_reply_message(
                    text="\n".join(message_lines),
                    chat_id=chat_id,
                    mid=message_id
                )
        except Exception as e:
            bot.send_reply_message(
                text=f"❌ حدث خطأ أثناء جلب أوامر الحماية: {e}",
                chat_id=chat_id,
                mid=message_id
            )

            # ===== أمر كشف =====
            # ===== مسح رسالة =====
    elif "مسح رسالة" in [lower_text, base_command]:
        try:
            if "link" not in msg or msg["link"].get("type") != "reply":
                send_reply_message("❌ يجب الرد على الرسالة التي تريد حذفها.", chat_id, message_id)
                return
            is_protected = is_user_protected(target_user_id, chat_id)
            executor_is_owner, owner_name = is_executor_primary_owner(str(user_id), str(chat_id))
            group_owner_name = get_primary_owner_name(chat_id)  # اسم المنشئ لعرضه عند الحماية

            # إذا الشخص محمي والمنفذ ليس منشئ أساسي
            if is_protected and not executor_is_owner:
                send_reply_message(
                    f"⊰❳ عذرآ تم تفعيل الحماية للشخص : \n"
                    f"┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                    f"🛡️ بواسطة: {group_owner_name}",
                    chat_id,
                    message_id
                )
                return


            # جلب معرف الرسالة المردود عليها
            reply_message_id = msg["link"]["message"]["mid"]

            bot.delete_message(reply_message_id)
            send_reply_message("🗑️ تم حذف الرسالة بنجاح.", chat_id, message_id)

        except Exception as e:
            send_reply_message(f"❌ حدث خطأ أثناء الحذف: {e}", chat_id, message_id)
    elif "الاوامر المضافه" in [lower_text, base_command]:
        response = handle_added_commands(update)  # استدعاء الدالة
        bot.send_reply_message(
            text=response,
            chat_id=bot.get_chat_id(update),
            mid=bot.get_message_id(update)
        )
    elif "كشف" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد كشفه.", chat_id, message_id)
            return
        try:
            with sqlite3.connect("bot_data.sqlite") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role FROM roles 
                    WHERE group_id=? AND user_id=?
                """, (str(chat_id), target_user_id))
                row = cursor.fetchone()

            role = row[0] if row else "عضو عادي"
            send_reply_message(
                f"👤 الاسم: {target_name}\n"
                f"🔖 الرتبة: {role}",
                chat_id,
                message_id
            )
        except Exception as e:
            send_reply_message(f"❌ حدث خطأ أثناء جلب بيانات العضو: {e}", chat_id, message_id)
    # بعدين فقط لو عنده state نكمل
    # state = user_command_state.get(state_key)
    # if not state:
    #       return
# =========================== نهاية اوامر الادمنية ===================

# ================== بداية دالة الأوامر العامة ====================
def handle_general_commands(update, text, chat_id, message_id, user_id, bot, cursor):
    """
    أوامر عامة يمكن لأي عضو استخدامها في المجموعة.
    """
    if text is None:
        return

    lower_text = text.strip().lower()
    text_clean = lower_text
    base_command = get_command_from_text(lower_text, chat_id)

    chat_id_str = str(chat_id)
    user_id_str = str(user_id)

    # ===== أمر إظهار الايدي =====
    if text_clean == "ايدي":
        response = handle_id_command(update)
        bot.send_reply_message(
            text=response,
            chat_id=chat_id,
            mid=message_id
        )

    # ===== أمر الألعاب =====
    elif text_clean == "الالعاب":
        display_games(chat_id)

    elif text_clean == "مطورين":
        reply_text = list_roles("مطور", group_id="global", priority=2)
        send_reply_message(reply_text, chat_id, message_id)

    # ===== عرض جميع المنشئين =====
    elif "المنشئين" in [lower_text, base_command]:
        try:
            reply_text = list_roles("منشئ", group_id=chat_id_str, priority=4)
            if not reply_text:
                reply_text = "ℹ️ لا يوجد منشئين في هذه المجموعة."
            send_reply_message(reply_text, chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء جلب المنشئين: {e}", chat_id, message_id)

    # ===== عرض الادمنية =====
    elif "الادمنية" in [lower_text, base_command]:
        reply_text = list_roles("ادمن", group_id=chat_id_str, priority=5)
        send_reply_message(reply_text, chat_id, message_id)

    # ===== عرض الأعضاء المميزين =====
    elif "المميزين" in [lower_text, base_command]:
        try:
            reply_text = list_roles("عضو مميز", group_id=chat_id_str, priority=6)
            if not reply_text:
                reply_text = "ℹ️ لا يوجد أعضاء مميزين في هذه المجموعة."
            send_reply_message(reply_text, chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء جلب الأعضاء المميزين: {e}", chat_id, message_id)

    # ===== عرض منشئ واحد (الأساسي فقط) =====
    elif text_clean == "منشئ":
        try:
            cursor.execute("""
                SELECT fullname, username, user_id 
                FROM roles 
                WHERE group_id = ? AND role = ? 
                ORDER BY priority ASC 
                LIMIT 1
            """, (chat_id_str, "منشئ أساسي"))
            row = cursor.fetchone()

            if not row:
                response = "ℹ️ لا يوجد منشئ أساسي في هذه المجموعة."
            else:
                fullname, user_tag, user_id = row
                role_text = "المنشئ الأساسي"

                response = (
                    "⊰❳ معلومات المنشئ الأساسي :\n"
                    "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
                    f"👤 الاسم : {fullname}\n"
                    f"🔹 يوزرك : @{user_tag if user_tag else 'غير متوفر'}\n"
                    f"🆔 المعرف : {user_id}\n"
                    f"🏷️ الرتبة : {role_text}\n"
                    "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"
                )

            bot.send_reply_message(
                text=response,
                chat_id=chat_id,
                mid=message_id
            )

        except Exception as e:
            bot.send_reply_message(
                text=f"❌ خطأ أثناء جلب المنشئ الأساسي: {e}",
                chat_id=chat_id,
                mid=message_id
            )

# def handle_general_commands(update, text, chat_id, message_id, user_id, bot, cursor):
#     """
#     أوامر عامة يمكن لأي عضو استخدامها في المجموعة.
#     """
#     if text is None:
#         return

#     lower_text = text.strip().lower()
#     text_clean = lower_text  # هنا ممكن تستبدل بمعالجة إضافية إذا عندك
#     base_command = get_command_from_text(lower_text, chat_id)

#     # ===== أمر إظهار الايدي =====
#     if text_clean == "ايدي":
#         response = handle_id_command(update)
#         bot.send_reply_message(
#             text=response,
#             chat_id=chat_id,
#             mid=message_id
#         )

#     # ===== أمر الألعاب =====
#     elif text_clean == "الالعاب":
#         display_games(chat_id)

#     # ===== عرض المطورين =====

#     elif text_clean == "مطورين":
#         print(f"[DEBUG] شرط مطورين تحقق: lower_text={lower_text}")
#         reply_text = list_roles("مطور", group_id="global", priority=2)
#         print(f"[DEBUG] نتيجة استعلام list_roles:\n{reply_text}")
#         send_reply_message(reply_text, chat_id, message_id)

#     # ===== عرض جميع المنشئين =====
#     elif "المنشئين" in [lower_text, base_command]:
#         try:
#             reply_text = list_roles("منشئ", group_id=str(chat_id), priority=4)
#             if not reply_text:
#                 reply_text = "ℹ️ لا يوجد منشئين في هذه المجموعة."
#             send_reply_message(reply_text, chat_id, message_id)
#         except Exception as e:
#             send_reply_message(f"❌ خطأ أثناء جلب المنشئين: {e}", chat_id, message_id)

#     # ===== عرض الادمنية =====
#     elif "الادمنية" in [lower_text, base_command]:
#         reply_text = list_roles("ادمن", group_id=str(chat_id), priority=5)
#         send_reply_message(reply_text, chat_id, message_id)

#     # ===== عرض الأعضاء المميزين =====
#     elif "المميزين" in [lower_text, base_command]:
#         try:
#             reply_text = list_roles("عضو مميز", group_id=str(chat_id), priority=6)
#             if not reply_text:
#                 reply_text = "ℹ️ لا يوجد أعضاء مميزين في هذه المجموعة."
#             send_reply_message(reply_text, chat_id, message_id)
#         except Exception as e:
#             send_reply_message(f"❌ خطأ أثناء جلب الأعضاء المميزين: {e}", chat_id, message_id)

#     # ===== عرض منشئ واحد (الأساسي فقط) =====
#     elif text_clean == "منشئ":
#         try:
#             cursor.execute("""
#                 SELECT fullname, username, user_id 
#                 FROM roles 
#                 WHERE group_id = ? AND role = ? 
#                 ORDER BY priority ASC 
#                 LIMIT 1
#             """, (str(chat_id), "منشئ أساسي"))
#             row = cursor.fetchone()

#             if not row:
#                 response = "ℹ️ لا يوجد منشئ أساسي في هذه المجموعة."
#             else:
#                 fullname, user_tag, user_id = row
#                 role_text = "المنشئ الأساسي"

#                 response = (
#                     "⊰❳ معلومات المنشئ الأساسي :\n"
#                     "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
#                     f"👤 الاسم : {fullname}\n"
#                     f"🔹 يوزرك : @{user_tag if user_tag else 'غير متوفر'}\n"
#                     f"🆔 المعرف : {user_id}\n"
#                     f"🏷️ الرتبة : {role_text}\n"
#                     "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"
#                 )

#             bot.send_reply_message(
#                 text=response,
#                 chat_id=chat_id,
#                 mid=message_id
#             )

#         except Exception as e:
#             bot.send_reply_message(
#                 text=f"❌ خطأ أثناء جلب المنشئ الأساسي: {e}",
#                 chat_id=chat_id,
#                 mid=message_id
#             )

# ======================== بداية دالة طرد البوتات ====================

def kick_all_bots(bot, chat_id, requester_id, message_id):
    """
    طرد جميع البوتات من المجموعة المحددة حتى لو كانت منشئ.
    """
    try:
        conn = sqlite3.connect("bot_data.sqlite")
        cursor = conn.cursor()

        # جلب كل البوتات الحقيقية من الجدول بدون أي شروط إضافية
        cursor.execute(
            "SELECT DISTINCT user_id, username FROM users WHERE group_id=? AND is_bot=1",
            (str(chat_id),)
        )
        bots = cursor.fetchall()
        print("DEBUG: البوتات المراد طردها:", bots)
        conn.close()

        if not bots:
            return False

        for user_id, username in bots:
            try:
                # إزالة البوت ثم حظره
                bot.remove_member(chat_id, int(user_id))
                bot.ban_member(chat_id, int(user_id))
                print(f"[INFO] 🚫 تم طرد البوت @{username or 'بدون_يوزر'} (ID={user_id}) من المجموعة {chat_id}")
            except Exception as e:
                print(f"[ERROR] فشل طرد البوت {user_id} من المجموعة {chat_id}: {e}")

        return True

    except Exception as e:
        print(f"[FATAL] خطأ في دالة kick_all_bots: {e}")
        return False


# ======================== نهاية دالة طرد البوتات ====================
# ================ دالة جلب الاشخاص المحمين ===========

def is_user_protected(user_id: str, chat_id: str) -> bool:
    """
    ترجع True إذا كان المستخدم محمي (role="حماية") في المجموعة المحددة.
    ترجع False إذا لم يكن محمي.
    """
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM roles WHERE user_id=? AND group_id=? AND role=?",
                (user_id, chat_id, "حماية")
            )
            result = cursor.fetchone()
            return bool(result)  # True إذا وجد صف، False إذا لم يوجد
    except Exception as e:
        print(f"❌ خطأ أثناء التحقق من الحماية: {e}")
        return False

# =========== دالة جلب اسم المنشئ الاساسي ===========
import sqlite3

def get_primary_owner_name(chat_id: str) -> str:
    """
    ترجع اسم المنشئ الأساسي في المجموعة حسب group_id.
    إذا لم يوجد، ترجع فراغ ''.
    """
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fullname FROM roles WHERE group_id=? AND role=? AND priority=?",
                (chat_id, "منشئ أساسي", 3)
            )
            result = cursor.fetchone()
            if result:
                return result[0]  # اسم المنشئ الأساسي
            else:
                return ''
    except Exception as e:
        print(f"❌ خطأ أثناء جلب اسم المنشئ الأساسي: {e}")
        return ''

import sqlite3
# from typing import tuple
def is_executor_primary_owner(user_id: str, chat_id: str) -> tuple[bool, str]:
    """
    ترجع True + fullname إذا كان المستخدم هو المنشئ الأساسي للمجموعة.
    """
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fullname FROM roles WHERE group_id=? AND role=? AND priority=? AND user_id=?",
                (chat_id, "منشئ أساسي", 3, user_id)
            )
            result = cursor.fetchone()
            if result:
                return True, result[0]
            else:
                return False, ''
    except Exception as e:
        print(f"❌ خطأ أثناء التحقق من المنشئ الأساسي: {e}")
        return False, ''

# ================== بداية دالة اوامر المنشئ الاساسي ====================
def handle_main_owner_commands(update, text, chat_id, message_id, user_id,bot):
    """
    أوامر المنشئ الأساسي فقط، نسخة محسنة وسريعة، باستخدام الدوال العامة.
    """
    if text is None:
        return
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)

    # التحقق من أن المرسل هو منشئ أساسي
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM roles 
                WHERE user_id=? AND priority <=4  AND group_id IN (?, 'global')
                """, (str(user_id), str(chat_id)))
            if not cursor.fetchone():
                return  
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من المنشئ الأساسي: {e}", chat_id, message_id)
        return

    # الحصول على المستخدم المردود عليه
    updates = update.get("updates", [])
    msg = updates[0].get("message", {}) if updates else {}

    sender = {}
    if "reply_to_message" in msg:
        reply_msg = msg.get("reply_to_message", {})
        sender = reply_msg.get("sender") or reply_msg.get("from") or {}
    elif "link" in msg and msg["link"].get("type") == "reply":
        link = msg["link"]
        sender = link.get("sender") or {}

    target_user_id = str(sender.get("user_id", ""))
    target_name = sender.get("name", "مستخدم")
    username = sender.get("username", "")

    # ===== رفع منشئ =====
    if lower_text in ["رفع منشئ", "رفع منشى"]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد رفعه.", chat_id, message_id)
            return

        msg_text = add_role_to_db(
            user_id=target_user_id,
            fullname=target_name,
            username=username,
            role="منشئ",
            priority=4,
            group_id=str(chat_id),
            added_by_admin=1
        )
        send_reply_message(msg_text, chat_id, message_id)

    # ===== تنزيل منشئ =====
    elif "تنزيل منشئ" in [lower_text, base_command]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد تنزيله.", chat_id, message_id)
            return
        if  remove_role_from_db(user_id=target_user_id,role="منشئ",group_id=str(chat_id),priority=4):
            send_reply_message(f"✅ تم تنزيل المستخدم {target_name} من رتبة المنشئ.", chat_id, message_id)
        else:
            send_reply_message(f"ℹ️ المستخدم {target_name} ليس منشئ.", chat_id, message_id)

    # ===== مسح جميع المنشئين =====
    elif "مسح المنشئين" in [lower_text, base_command]:
        try:
            remove_all_roles("منشئ", group_id=str(chat_id), priority=4)
            send_reply_message("✅ تم مسح جميع المنشئين من هذه المجموعة.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء مسح المنشئين: {e}", chat_id, message_id)


    # # ===== أمر مسح ترحيب =====
    elif "مسح ترحيب" in [lower_text, base_command]:
        result = welcome_manager.delete_welcome(chat_id)
        if result:
            send_reply_message("🗑️ تم مسح الترحيب الخاص بهذه المجموعة.", chat_id, message_id)
            print(f"[DEBUG] تم مسح الترحيب للمجموعة {chat_id}")
        else:
            send_reply_message("⚠️ لا يوجد ترحيب محفوظ لهذه المجموعة.", chat_id, message_id)
            print(f"[TRACE] لا يوجد ترحيب مخزن للمجموعة {chat_id}")
        return
    elif "تنضيف" in [lower_text, base_command]:
      print("[INFO] استدعاء أمر التنضيف من المستخدم:", user_id)
      clean_messages(chat_id)
    # ===== أمر إضافة رد =====
    # ===== رفع حماية =====
    # ===== رفع حماية =====
    elif lower_text in ["رفع حماية"]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد منحه حماية.", chat_id, message_id)
            return

        msg_text = add_role_to_db(
            user_id=target_user_id,
            fullname=target_name,
            username=username,
            role="حماية",
            priority=8,
            group_id=str(chat_id),
            added_by_admin=1
        )
        send_reply_message(msg_text, chat_id, message_id)

    # ===== تنزيل حماية =====
    elif lower_text in ["تنزيل حماية"]:
        if not target_user_id:
            send_reply_message("❌ يجب الرد على رسالة المستخدم الذي تريد إزالة الحماية منه.", chat_id, message_id)
            return

        if remove_role_from_db(user_id=target_user_id, role="حماية", group_id=str(chat_id), priority=8):
            send_reply_message(f"✅ تم تنزيل المستخدم {target_name} من رتبة الحماية.", chat_id, message_id)
        else:
            send_reply_message(f"ℹ️ المستخدم {target_name} ليس لديه حماية.", chat_id, message_id)

    # ===== مسح جميع الحمايات =====
    elif "مسح الحماية" in [lower_text, base_command]:
        try:
            remove_all_roles("حماية", group_id=str(chat_id), priority=8)
            send_reply_message("✅ تم مسح جميع رتب الحماية من هذه المجموعة.", chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء مسح الحمايات: {e}", chat_id, message_id)

    # ===== عرض قائمة الحماية =====
    elif lower_text in ["عرض الحماية", "الحماية"]:
        try:
            reply_text = list_roles("حماية", group_id=str(chat_id), priority=8)
            if not reply_text:
                 msg_text = "ℹ️ لا يوجد محمين في هذه المجموعة."
            send_reply_message(reply_text, chat_id, message_id)
        except Exception as e:
            send_reply_message(f"❌ خطأ أثناء جلب المحمين: {e}", chat_id, message_id)


    # ===== معالجة الرسائل الجديدة =====
    updates = update.get("updates", [])
    if updates:
        msg_data = updates[0].get("message", {})
        msg_text = ""
        if "body" in msg_data and "text" in msg_data["body"]:
            msg_text = msg_data["body"]["text"]
        elif "text" in msg_data:
            msg_text = msg_data["text"]
        elif "caption" in msg_data:
            msg_text = msg_data["caption"]

        msg_user_id = str(user_id)
        print(f"[TRACE] نص الرسالة المستلم: {msg_text} (من المستخدم {msg_user_id})")

        # معالجة الترحيب والردود وحذف الردود
        # process_waiting_response(chat_id, user_id, msg_text, message_id)

# =========================== نهاية داله اوامر المنشئ الاساسي======================
# ====================== الدوال الخاصه ب الردود العامه ======================

import sqlite3

# ===== إنشاء جدول الردود العامة =====
def create_global_replies_table():
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT UNIQUE NOT NULL,
                    reply TEXT NOT NULL
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"[ERROR] خطأ عند إنشاء جدول الردود العامة: {e}")

create_global_replies_table()

# ===== دوال إدارة الردود العامة =====

def add_global_reply(keyword, reply, chat_id, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            # تحقق من الحد الأقصى 100 رد
            cursor.execute("SELECT COUNT(*) FROM global_replies")
            count = cursor.fetchone()[0]
            if count >= 100:
                send_reply_message("⚠ لا يمكن إضافة رد جديد، الحد الأقصى 100 رد.", chat_id, message_id)
                return
            cursor.execute("INSERT OR REPLACE INTO global_replies (keyword, reply) VALUES (?, ?)",
                           (keyword, reply))
            conn.commit()
            send_reply_message(f"✅ تم إضافة الرد العام: '{keyword}' -> '{reply}'", chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء إضافة الرد العام: {e}", chat_id, message_id)

def delete_global_reply(keyword, chat_id, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM global_replies WHERE keyword=?", (keyword,))
            conn.commit()
            if cursor.rowcount:
                send_reply_message(f"✅ تم حذف الرد العام للكلمة '{keyword}'", chat_id, message_id)
            else:
                send_reply_message(f"⚠ لا يوجد رد عام مرتبط بالكلمة '{keyword}'", chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء حذف الرد العام: {e}", chat_id, message_id)

def delete_all_global_replies(chat_id, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM global_replies")
            conn.commit()
            send_reply_message("🗑️ تم مسح جميع الردود العامة.", chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء مسح الردود العامة: {e}", chat_id, message_id)

def list_global_replies(chat_id, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT keyword, reply FROM global_replies")
            rows = cursor.fetchall()
            if not rows:
                send_reply_message("⚠ لا توجد ردود عامة محفوظة.", chat_id, message_id)
                return
            text_list = ["› قائمة الردود العامة ⬇️", "— — — — — — — — —"]
            for idx, (keyword, reply) in enumerate(rows, start=1):
                text_list.append(f"{idx}- {keyword} -> {reply}")
            send_reply_message("\n".join(text_list), chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء جلب الردود العامة: {e}", chat_id, message_id)
# ================== بداية الدوال الخاصه ب الردود الخاصه ========================
import sqlite3

# ===== إنشاء جدول الردود لكل مجموعة =====
def create_group_replies_table():
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    reply TEXT NOT NULL,
                    UNIQUE(chat_id, keyword)
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"[ERROR] خطأ عند إنشاء جدول الردود لكل مجموعة: {e}")

create_group_replies_table()

# ===== دوال إدارة الردود لكل مجموعة =====

def add_group_reply(chat_id, keyword, reply, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            # تحقق من الحد الأقصى 30 رد لكل مجموعة
            cursor.execute("SELECT COUNT(*) FROM group_replies WHERE chat_id=?", (str(chat_id),))
            count = cursor.fetchone()[0]
            if count >= 30:
                send_reply_message("⚠ لا يمكن إضافة رد جديد، الحد الأقصى 30 رد لكل مجموعة.", chat_id, message_id)
                return
            cursor.execute("""
                INSERT OR REPLACE INTO group_replies (chat_id, keyword, reply) VALUES (?, ?, ?)
            """, (str(chat_id), keyword, reply))
            conn.commit()
            send_reply_message(f"✅ تم إضافة الرد: '{keyword}' -> '{reply}'", chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء إضافة الرد: {e}", chat_id, message_id)

def delete_group_reply(chat_id, keyword, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM group_replies WHERE chat_id=? AND keyword=?", (str(chat_id), keyword))
            conn.commit()
            if cursor.rowcount:
                send_reply_message(f"✅ تم حذف الرد للكلمة '{keyword}'", chat_id, message_id)
            else:
                send_reply_message(f"⚠ لا يوجد رد مرتبط بالكلمة '{keyword}' في هذه المجموعة.", chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء حذف الرد: {e}", chat_id, message_id)

def delete_all_group_replies(chat_id, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM group_replies WHERE chat_id=?", (str(chat_id),))
            conn.commit()
            send_reply_message("🗑️ تم مسح جميع الردود لهذه المجموعة.", chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء مسح الردود: {e}", chat_id, message_id)

def list_group_replies(chat_id, message_id):
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT keyword, reply FROM group_replies WHERE chat_id=?", (str(chat_id),))
            rows = cursor.fetchall()
            if not rows:
                send_reply_message("⚠ لا توجد ردود محفوظة لهذه المجموعة.", chat_id, message_id)
                return
            text_list = ["› قائمة الردود ⬇️", "— — — — — — — — —"]
            for idx, (keyword, reply) in enumerate(rows, start=1):
                text_list.append(f"{idx}- {keyword} -> {reply}")
            send_reply_message("\n".join(text_list), chat_id, message_id)
    except Exception as e:
        send_reply_message(f"❌ خطأ أثناء جلب الردود: {e}", chat_id, message_id)

# ===== دالة مستقلة لإدارة أوامر الردود لكل مجموعة =====
import sqlite3
import unicodedata

def auto_reply_handler(text, chat_id, message_id):
    if not text:
        print("[DEBUG] النص فارغ، لا يوجد رد.")
        return

    # تنظيف النص: إزالة الفراغات وتحويله لحروف صغيرة
    lower_text = text.strip().lower()
    # إزالة التشكيل
    lower_text = ''.join(c for c in unicodedata.normalize('NFKD', lower_text) if not unicodedata.combining(c))

    print(f"[DEBUG] النص بعد التنظيف: '{lower_text}'")

    # ===== تحقق من الردود الخاصة بالمجموعة =====
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT reply FROM group_replies
                WHERE chat_id=? AND keyword=?
            """, (str(chat_id), lower_text))
            group_reply = cursor.fetchone()
            if group_reply:
                print(f"[DEBUG] تم العثور على رد خاص: '{group_reply[0]}'")
                send_reply_message(group_reply[0], chat_id, message_id)
                return
            else:
                print("[DEBUG] لم يتم العثور على رد خاص بالمجموعة.")
    except Exception as e:
        print(f"[ERROR] فحص الردود الخاصة: {e}")

    # ===== تحقق من الردود العامة =====
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT reply FROM global_replies
                WHERE keyword=?
            """, (lower_text,))
            global_reply = cursor.fetchone()
            if global_reply:
                print(f"[DEBUG] تم العثور على رد عام: '{global_reply[0]}'")
                send_reply_message(global_reply[0], chat_id, message_id)
                return
            else:
                print("[DEBUG] لم يتم العثور على رد عام.")
    except Exception as e:
        print(f"[ERROR] فحص الردود العامة: {e}")

    print("[DEBUG] لا يوجد رد متاح للنص المرسل.")

# ================ نهابة دالة الردود ==================
user_command_state_group = {}  # لتخزين حالة المستخدم لكل مجموعة

def group_replies_handler(text, chat_id, message_id, user_id):
    if not text:
        return
    lower_text = text.strip().lower()
    base_command = get_command_from_text(lower_text, chat_id)
    # التحقق من صلاحية المستخدم (priority 1-5)
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM roles WHERE user_id=? AND priority <= 5", (str(user_id),))
            # if not cursor.fetchone():
            #     send_reply_message("❌ ليس لديك صلاحية لاستخدام أوامر الردود.", chat_id, message_id)
            #     return
    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من الصلاحيات: {e}", chat_id, message_id)
        return

    state_key = f"group_replies:{chat_id}:{user_id}"

    # ===== أوامر البداية =====
    if "اضف رد" in [lower_text, base_command]:
        user_command_state_group[state_key] = {"step": 1, "action": "add_group_reply"}
        send_reply_message("📌 أرسل الكلمة التي تريد ربط رد لها:", chat_id, message_id)
        return

    elif "حذف رد" in [lower_text, base_command]:
        user_command_state_group[state_key] = {"step": 1, "action": "remove_group_reply"}
        send_reply_message("📌 أرسل الكلمة التي تريد حذف الرد المرتبط بها:", chat_id, message_id)
        return

    elif "مسح الردود" in [lower_text, base_command]:
        delete_all_group_replies(chat_id, message_id)
        return

    elif "الردود" in [lower_text, base_command]:
        list_group_replies(chat_id, message_id)
        return

    # ===== معالجة حالة إضافة/حذف الرد =====
    if state_key in user_command_state_group:
        state = user_command_state_group[state_key]
        step = state.get("step")
        action = state.get("action")
        keyword = lower_text.strip()

        if action == "add_group_reply" and step == 1:
            user_command_state_group[state_key]["step"] = 2
            user_command_state_group[state_key]["keyword"] = keyword
            send_reply_message(f"✍️ أرسل الرد للكلمة '{keyword}':", chat_id, message_id)

        elif action == "remove_group_reply" and step == 1:
            delete_group_reply(chat_id, keyword, message_id)
            user_command_state_group.pop(state_key)

        elif action == "add_group_reply" and step == 2:
            keyword = state.get("keyword")
            add_group_reply(chat_id, keyword, lower_text, message_id)
            user_command_state_group.pop(state_key)

# =================== نهاية الدوال الخاصه ب الردود اخاصه =======================
# ===== دالة مستقلة لإدارة أوامر الردود العامة =====
user_command_state_global = {}  # لتخزين حالة المستخدم
# ================== بداية دالة المطورين ======================
def global_replies_handler(text, chat_id, message_id, user_id):
    if not text:
        return
    lower_text = text.strip().lower()

    # التحقق من صلاحية المستخدم (priority 1 أو 2)
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM roles WHERE user_id=? AND priority <= 2 AND group_id IN ('global')", (str(user_id),))

    except Exception as e:
        send_reply_message(f"❌ خطأ في التحقق من الصلاحيات: {e}", chat_id, message_id)
        return
    base_command = get_command_from_text(lower_text, chat_id)
    state_key = f"global_replies:{user_id}"

    if "اضف رد عام" in [lower_text, base_command]:
        user_command_state_global[state_key] = {"step": 1, "action": "add_global_reply"}
        send_reply_message("📌 أرسل الآن الكلمة التي تريد ربط رد عام لها:", chat_id, message_id)
        return

    elif "حذف رد عام" in [lower_text, base_command]:
        user_command_state_global[state_key] = {"step": 1, "action": "remove_global_reply"}
        send_reply_message("📌 أرسل الآن الكلمة التي تريد حذف الرد العام المرتبط بها:", chat_id, message_id)
        return

    elif "مسح الردود العامه" in [lower_text, base_command]:
        delete_all_global_replies(chat_id, message_id)
        return

    elif "الردود العامه" in [lower_text, base_command]:
        list_global_replies(chat_id, message_id)
        return

    # ===== معالجة حالة إضافة/حذف الرد العام =====
    if state_key in user_command_state_global:
        state = user_command_state_global[state_key]
        step = state.get("step")
        action = state.get("action")
        keyword = lower_text.strip()

        if action == "add_global_reply" and step == 1:
            user_command_state_global[state_key]["step"] = 2
            user_command_state_global[state_key]["keyword"] = keyword
            send_reply_message(f"✍️ أرسل الرد العام للكلمة '{keyword}':", chat_id, message_id)

        elif action == "remove_global_reply" and step == 1:
            delete_global_reply(keyword, chat_id, message_id)
            user_command_state_global.pop(state_key)

        elif action == "add_global_reply" and step == 2:
            keyword = state.get("keyword")
            add_global_reply(keyword, lower_text, chat_id, message_id)
            user_command_state_global.pop(state_key)

# ======================  نهاية الدوال الخاصه ب الردود العامه =================
# ==================  نهاية دالة المطورين ======================
# ====================== بداية دالة منع التكرار ======================
last_messages = {}

# def check_and_handle_repetition(bot, chat_id, user_id, message_content, message_id, username, developer_ids=None):
#     global last_messages

#     if developer_ids is None:
#         developer_ids = []

#     message_content = message_content.strip()
#     print(f"[Trace] فحص رسالة من user_id={user_id}، محتوى: {message_content[:30]}...")

#     if not message_content:
#         print("[Debug] رسالة فارغة، تجاهل")
#         return False

#     if is_dev(user_id):
#         print("[Debug] مستخدم مطور، تجاهل")
#         return False

#     if chat_id not in last_messages:
#         last_messages[chat_id] = {}
#     if user_id not in last_messages[chat_id]:
#         last_messages[chat_id][user_id] = {
#             "last_message": None,
#             "count": 0,
#             "message_ids": [],
#             "is_banned": False
#         }

#     user_data = last_messages[chat_id][user_id]

#     if user_data["is_banned"]:
#         print("[Debug] المستخدم محظور مسبقاً، تجاهل")
#         return False

#     user_data["message_ids"].append({
#         "message_id": message_id,
#         "content": message_content,
#         "timestamp": datetime.datetime.now()
#     })

#     if message_content == user_data["last_message"]:
#         user_data["count"] += 1
#     else:
#         user_data["last_message"] = message_content
#         user_data["count"] = 1

#     print(f"[Trace] الرسالة الأخيرة: {user_data['last_message']}, العدد الحالي: {user_data['count']}")

#     is_link = bool(re.search(r"\b(?:[a-zA-Z][a-zA-Z0-9+.-]*://|www\.)\S+", message_content))
#     print(f"[Trace] is_link = {is_link}")
#     max_count = 3 if is_link else 5

#     if user_data["count"] >= max_count:
#         notice_name = f"@{username}" if username else f"ID:{user_id}"
#         print(f"[Debug] تم الوصول لعدد التكرار المطلوب: {user_data['count']}, سيتم حظر المستخدم وحذف الرسائل")
#         try:
#             bot.ban_member(chat_id, user_id)
#         except Exception as e:
#             print(f"[Debug] خطأ بالحظر: {e}")

#         now = datetime.datetime.now()
#         one_minute = datetime.timedelta(minutes=5)

#         total_msgs = len(user_data["message_ids"])
#         print(f"[Debug] عدد الرسائل المخزنة قبل الحذف: {total_msgs} - وقت التحقق: {now}")

#         to_remove = []
#         deleted_count = 0
#         bot.send_message(chat_id=chat_id,
#              text=f"🚫 تم حظر المستخدم {notice_name} بسبب إرسال {'روابط' if is_link else 'رسائل'} مكررة.")
#         for msg in list(user_data["message_ids"]):
#             msg_age = now - msg["timestamp"]
#             print(f"[Trace] Message ID={msg['message_id']} | Content={msg['content'][:20]}... | Age={msg_age} | Last message={user_data['last_message'][:20]}...")
#             if msg["content"] == user_data["last_message"] and msg_age <= one_minute:
#                 try:
#                     bot.delete_message(msg["message_id"])
#                     to_remove.append(msg)
#                     deleted_count += 1
#                     print(f"[Debug] حذف رسالة ID={msg['message_id']} | محتوى مطابق | عمر الرسالة: {msg_age}")
#                 except Exception as e:
#                     print(f"[Debug] فشل في حذف رسالة ID={msg['message_id']}, خطأ: {e}")
#             else:
#                 print(f"[Debug] تجاهل رسالة ID={msg['message_id']} | محتوى غير مطابق أو عمرها {msg_age} أكبر من الفترة المحددة")

#         for msg in to_remove:
#             user_data["message_ids"].remove(msg)

#         print(f"[Debug] عدد الرسائل المحذوفة: {deleted_count}")
#         try:
#             bot.send_message(chat_id=chat_id,
#                              text=f"🚫 تم حظر المستخدم {notice_name} بسبب إرسال {'روابط' if is_link else 'رسائل'} مكررة.")
#         except Exception as e:
#             print(f"[Debug] خطأ في إرسال رسالة الحظر: {e}")

#         user_data["is_banned"] = True
#         user_data["last_message"] = None
#         user_data["count"] = 0
#         user_data["message_ids"].clear()

#         return True

#     print(f"[Debug] لا حاجة لحذف الرسالة. عدد التكرارات: {user_data['count']}, الحد المطلوب: {max_count}")
#     return False


last_messages = {}
def check_and_handle_repetition(bot, chat_id, user_id, message_content, message_id, username, developer_ids=None):
    global last_messages

    if developer_ids is None:
        developer_ids = []

    message_content = message_content.strip()
    print(f"[Trace] فحص رسالة من user_id={user_id}، محتوى: {message_content[:30]}...")

    if not message_content:
        print("[Debug] رسالة فارغة، تجاهل")
        return False

    if is_dev(user_id):
        print("[Debug] مستخدم مطور، تجاهل")
        return False

    if chat_id not in last_messages:
        last_messages[chat_id] = {}
    if user_id not in last_messages[chat_id]:
        last_messages[chat_id][user_id] = {
            "last_message": None,
            "count": 0,
            "message_ids": [],
            "is_banned": False
        }

    user_data = last_messages[chat_id][user_id]

    if user_data["is_banned"]:
        print("[Debug] المستخدم محظور مسبقاً، تجاهل")
        return False

    user_data["message_ids"].append({
        "message_id": message_id,
        "content": message_content,
        "timestamp": datetime.datetime.now()
    })

    if message_content == user_data["last_message"]:
        user_data["count"] += 1
    else:
        user_data["last_message"] = message_content
        user_data["count"] = 1

    print(f"[Trace] الرسالة الأخيرة: {user_data['last_message']}, العدد الحالي: {user_data['count']}")

    is_link = bool(re.search(r"\b(?:[a-zA-Z][a-zA-Z0-9+.-]*://|www\.)\S+", message_content))
    print(f"[Trace] is_link = {is_link}")
    max_count = 3 if is_link else 5

    if user_data["count"] >= max_count:
        notice_name = f"@{username}" if username else f"ID:{user_id}"
        print(f"[Debug] تم الوصول لعدد التكرار المطلوب: {user_data['count']}, سيتم حظر المستخدم وحذف الرسائل")
        try:
            bot.ban_member(chat_id, user_id)
        except Exception as e:
            print(f"[Debug] خطأ بالحظر: {e}")

        now = datetime.datetime.now()
        one_minute = datetime.timedelta(minutes=5)

        total_msgs = len(user_data["message_ids"])
        print(f"[Debug] عدد الرسائل المخزنة قبل الحذف: {total_msgs} - وقت التحقق: {now}")

        to_remove = []
        deleted_count = 0
        bot.send_message(chat_id=chat_id,
             text=f"🚫 تم حظر المستخدم {notice_name} بسبب إرسال {'روابط' if is_link else 'رسائل'} مكررة.")
        for msg in list(user_data["message_ids"]):
            msg_age = now - msg["timestamp"]
            print(f"[Trace] Message ID={msg['message_id']} | Content={msg['content'][:20]}... | Age={msg_age} | Last message={user_data['last_message'][:20]}...")
            if msg["content"] == user_data["last_message"] and msg_age <= one_minute:
                try:
                    bot.delete_message(msg["message_id"])
                    to_remove.append(msg)
                    deleted_count += 1
                    print(f"[Debug] حذف رسالة ID={msg['message_id']} | محتوى مطابق | عمر الرسالة: {msg_age}")
                except Exception as e:
                    print(f"[Debug] فشل في حذف رسالة ID={msg['message_id']}, خطأ: {e}")
            else:
                print(f"[Debug] تجاهل رسالة ID={msg['message_id']} | محتوى غير مطابق أو عمرها {msg_age} أكبر من الفترة المحددة")

        for msg in to_remove:
            user_data["message_ids"].remove(msg)

        print(f"[Debug] عدد الرسائل المحذوفة: {deleted_count}")
        try:
            bot.send_message(chat_id=chat_id,
                             text=f"🚫 تم حظر المستخدم {notice_name} بسبب إرسال {'روابط' if is_link else 'رسائل'} مكررة.")
        except Exception as e:
            print(f"[Debug] خطأ في إرسال رسالة الحظر: {e}")

        user_data["is_banned"] = True
        user_data["last_message"] = None
        user_data["count"] = 0
        user_data["message_ids"].clear()

        return True

    print(f"[Debug] لا حاجة لحذف الرسالة. عدد التكرارات: {user_data['count']}, الحد المطلوب: {max_count}")
    return False

# ====================== نهاية دالة منع التكرار ======================


def check_and_kick_added_bots(bot, update):
        try:
            update_data = update.get("updates", [])[0]
            chat_id = update_data.get("chat_id")
            user = update_data.get("user", {})
            user_id = user.get("user_id")
            username = user.get("username", "مجهول")
            is_bot = user.get("is_bot", False)
            inviter_id = update_data.get("inviter_id")

            # التحقق هل من أضاف العضو مطور
            is_dev_user = is_dev(inviter_id)

            print(f"[TRACE] فحص البوت المضاف: user_id={user_id}, username={username}, is_bot={is_bot}")
            print(f"[TRACE] معرف من أضاف العضو: inviter_id={inviter_id}, is_dev_user={is_dev_user}")

            protection_enabled = get_protection_status(chat_id, "البوتات")
            print(f"[TRACE] حالة حماية البوتات من قاعدة البيانات: {protection_enabled}")

            # إذا كانت الحماية مفعلة (مثلاً 0 يعني مفعلة حسب منطقك)، والعضو بوت، و"من أضافه" ليس مطوراً
            if protection_enabled == 0 and is_bot :
                bot.remove_member(chat_id, user_id)
                bot.ban_member(chat_id, user_id)
                print(f"[INFO] ✅ تم طرد البوت @{username} (ID: {user_id}) من المجموعة {chat_id}")
                return True
            else:
                print("[TRACE] لم يتم طرد أي بوت في حدث user_added بسبب الحماية أو لأن من أضاف العضو مطور")
                return False
        except Exception as e:
             print(f"[ERROR] ❌ خطأ في check_and_kick_added_bots: {e}")
             return False


def contains_whisper_link(message):
    whisper_pattern = re.compile(r"https://tt\.me/[^/]+/start/[-\w_]+", re.IGNORECASE)

    # فحص النص العادي
    if "body" in message and "text" in message["body"]:
        if whisper_pattern.search(message["body"]["text"]):
            return True

    # فحص الأزرار في المرفقات
    if "body" in message and "attachments" in message["body"]:
        for attachment in message["body"]["attachments"]:
            if attachment.get("type") == "inline_keyboard":
                buttons = attachment.get("payload", {}).get("buttons", [])
                for row in buttons:
                    for button in row:
                        url = button.get("url", "")
                        if whisper_pattern.search(url):
                            return True
    return False
def check_and_delete_whisper(bot, update, text, message_id, chat_id, user_id):
    print("[TRACE] بدء check_and_delete_whisper")

    try:
        keywords = [
            "همسه", "الهمسه", "همسة", "الهمسة",
            "فتح الهمسة", "فتح الهمسه",  "وصلتك الهمسة", "فتح همسة", "فتح همسه",
            "اظهار الرساله", "اظهار الرسالة", "اهمس"
            # ممكن تضيف كلمات أخرى هنا
        ]

        if not any(keyword in text for keyword in keywords):
            print("[DEBUG] النص لا يحتوي على أي كلمة مفتاحية للهمسة، لا حذف")
            return False

        if not message_id or not chat_id:
            print("[ERROR] بيانات الرسالة أو الشات مفقودة")
            return False

        try:
            bot.delete_message(message_id)
            print(f"[INFO] تم حذف رسالة الهمسة (message_id={message_id})")
            return True
        except Exception as e:
            print(f"[ERROR] فشل حذف رسالة الهمسة: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] خطأ في check_and_delete_whisper: {e}")
        return False
def welcome_new_member(bot, update):
    try:
        print("[TRACE] بدء تنفيذ welcome_new_member...")
        update_data = update.get("updates", [])[0]
        update_type = update_data.get("update_type")
        print(f"[TRACE] نوع التحديث: {update_type}")

        if update_type != "user_added":
            print("[TRACE] الحدث ليس user_added، تم التجاهل")
            return False

        chat_id = update_data.get("chat_id")
        user_info = update_data.get("user", {})
        user_name = user_info.get("name", "مستخدم")
        user_username = user_info.get("username", "")
        is_bot = user_info.get("is_bot", False)
        print(f"[TRACE] معلومات العضو: name={user_name}, username={user_username}, is_bot={is_bot}")

        welcome_enabled = get_protection_status(chat_id, "الترحيب")
        print(f"[TRACE] حالة حماية الترحيب: {welcome_enabled}")

        if welcome_enabled != 1:
            print("[TRACE] الترحيب معطل، تم التجاهل")
            return False

        if is_bot:
            print("[TRACE] العضو بوت، تم التجاهل")
            return False

        DEFAULT_WELCOME = "أهلاً وسهلاً #username نورت المجموعة ✨"
        print(f"[TRACE] الترحيب الافتراضي: {DEFAULT_WELCOME}")

        # تتبع استرجاع الترحيب من الجيسون
        stored_welcome = welcome_manager.get_welcome(str(chat_id))
        print(f"[TRACE] الترحيب المسترجع من الجيسون: {repr(stored_welcome)} (type={type(stored_welcome)})")

        # تحقق إضافي إذا كان الترحيب موجود وصالح
        if stored_welcome is not None and isinstance(stored_welcome, str) and stored_welcome.strip():
            welcome_text = stored_welcome
            print("[TRACE] سيتم استخدام الترحيب المخزن")
        else:
            welcome_text = DEFAULT_WELCOME
            print("[TRACE] سيتم استخدام الترحيب الافتراضي")

        welcome_text = welcome_text.replace("#name", user_name).replace("#username", user_username)
        print(f"[TRACE] نص الترحيب النهائي: {welcome_text}")

        bot.send_message(chat_id=chat_id, text=welcome_text)
        print(f"[INFO] ✅ تم الترحيب بالعضو @{user_username} في المجموعة {chat_id}")
        return True

    except Exception as e:
        print(f"[ERROR] ❌ خطأ في welcome_new_member: {e}")
        return False

def detect_message_type(bot, update):
    text = bot.get_text(update) or ""

    # Check for links
    if re.search(r"\b(?:[a-zA-Z][a-zA-Z0-9+.-]*://|www\.)\S+", text):
        return "الروابط"

    # Check for mentions
    if re.search(r"@\w+", text):
        return "المعرف"

    # Check for hashtags
    if re.search(r"#\w+", text):
        return "الهايشتاك"

    # Check for forwarded messages
    try:
        message = update.get("updates", [{}])[0].get("message", {})
        if "link" in message and message["link"].get("type") == "forward":
            return "التوجيه"
    except Exception:
        pass

    # ✅ Check for reply messages
    try:
        message = update.get("updates", [{}])[0].get("message", {})
        if "link" in message and message["link"].get("type") == "reply":
            return "الردود"
    except Exception:
        pass

    # Check for attachments
    attach_type = bot.get_attach_type(update)
    if attach_type:
        print(f"[INFO] نوع المرفق المكتشف: {attach_type}")
    if attach_type:
        mapping = {
            "image": "الصور",
            "video": "الفيديو",
            "audio": "الاغاني",
            "file": "الملفات",
            "sticker": "الملصقات",
            "animation": "المتحركه",
            "voice": "الصوت",
            "contact": "الجهات",
            "document": "الملفات",
            "gif": "المتحركه",
        }
        protection_name = mapping.get(attach_type)
        if protection_name:
            return protection_name

    return None
def send_group_info(bot, update):
    print("[TRACE] بدء تنفيذ send_group_info")

    try:
        update_type = bot.get_update_type(update)
        print(f"[DEBUG] نوع التحديث: {update_type}")

        if update_type != "message_created":
            print("[DEBUG] ليس تحديث رسالة جديدة، تم التخطي")
            return False

        message_obj = update.get("updates", [{}])[0].get("message", {})
        sender = message_obj.get("sender", {})
        user_id = sender.get("user_id")
        chat_id = message_obj.get("recipient", {}).get("chat_id")
        text = message_obj.get("body", {}).get("text", "").strip()

        print(f"[DEBUG] رسالة من المستخدم {user_id} في المجموعة {chat_id}: {text}")

        # تحقق هل المستخدم مطور (حسب تعريفك الخاص)
        if not is_dev(user_id):
            print("[DEBUG] المستخدم ليس مطور، تم التخطي")
            return False

        # تحقق هل الرسالة هي كلمة 'معلومات' (يمكنك تعديلها)
        if text != "معلومات":
            print("[DEBUG] النص ليس 'معلومات'، تم التخطي")
            return False

        # الحصول على أعضاء المجموعة
        members = bot.get_members(chat_id)
        if members is None:
            print("[ERROR] فشل في جلب أعضاء المجموعة")
            return False
        total_members = len(members)
        print(f"[DEBUG] عدد أعضاء المجموعة: {total_members}")

        # الحصول على المطورين في المجموعة (مثلاً من بين الأعضاء أو باستخدام دالة أخرى)
        # هنا نفترض أنك تملك دالة is_dev() تفحص المعرفات خارجياً
        # devs_in_group = [m for m in members if is_dev(m.get("user_id"))]
        # total_devs = len(devs_in_group)
        # print(f"[DEBUG] عدد المطورين في المجموعة: {total_devs}")

        # تكوين نص الرسالة
        # msg = f"عدد أعضاء المجموعة: {total_members}\nعدد المطورين في المجموعة: {total_devs}"

        # إرسال الرسالة بدون رد
        bot.send_message(chat_id, msg)
        print("[INFO] تم إرسال معلومات المجموعة بنجاح")

        return True

    except Exception as e:
        print(f"[ERROR] خطأ في send_group_info: {e}")
        return False

def check_and_delete_links(bot, update):
    update_type = bot.get_update_type(update)
    print(f"[TRACE] بدء الدالة check_and_delete_links، نوع التحديث: {update_type}")
    forbidden_words = ["مطي", "جلب", "حقير", "تف"]
    # print("[DEBUG] كامل محتوى update:\n", json.dumps(update, indent=2, ensure_ascii=False))
    # أولاً، نفحص إضافة بوتات
    if update_type == "user_added":
        chat_id = update.get("chat_id")
        print("[TRACE] حدث user_added تم استلامه، سيتم فحص البوتات المضافة")
        if check_and_kick_added_bots(bot, update):
            print("[TRACE] تم معالجة إضافة بوت وطُرد من المجموعة، إنهاء المعالجة هنا")
            return  # إذا طرد البوت، ننهي هنا
        else:
            print("[TRACE] لم يتم طرد أي بوت في حدث user_added")

    try:
        update_type = bot.get_update_type(update)
        print(f"[DEBUG] نوع التحديث: {update_type}")

        if update_type not in ["message_created", "message_edited","user_added"]:
            print("[DEBUG] التحديث ليس رسالة أو تعديل. تم التجاهل.")
            return False

        if update_type == "message_created":
            message_obj = update.get("updates", [{}])[0].get("message", {})
            body = message_obj.get("body", {})
            sender = message_obj.get("sender", {})
            recipient = message_obj.get("recipient", {})

            text = body.get("text") or ""
            message_id = body.get("mid")
            user_id = sender.get("user_id")
            username = sender.get("username", f"user_{user_id}")
            chat_id = recipient.get("chat_id")

        elif update_type == "message_edited":
            try:
                message = update.get("updates", [{}])[0].get("message", {})
                body = message.get("body", {})
                sender = message.get("sender", {})
                recipient = message.get("recipient", {})

                text = body.get("text") or ""
                message_id = body.get("mid")
                user_id = sender.get("user_id")
                chat_id = recipient.get("chat_id")
                username = sender.get("username", f"user_{user_id}")
            except Exception as e:
                print(f"[ERROR] فشل استخراج البيانات من الرسالة المعدلة: {e}")
                return False

        if not chat_id or not user_id or not message_id:
            print("[DEBUG] أحد الحقول الأساسية مفقودة. تم التجاهل.")
            return False
        if get_protection_status(chat_id, "الدردشه") == 0:
            try:
                bot.delete_message(message_id)
                print(f"[DEBUG] 🔒 تم حذف الرسالة بسبب قفل الدردشة من المستخدم {user_id}")
                return True
            except Exception as e:
                print(f"[ERROR] فشل حذف الرسالة بسبب قفل الدردشة: {e}")
            return True
        message_content = text.strip() if text else ""
        if  check_and_handle_repetition(bot, chat_id, user_id, message_content, message_id, username):
            return True

        if update_type == "message_edited" and get_protection_status(chat_id, "التعديل") == 0:
            try:
                bot.delete_message(message_id)
                print(f"[DEBUG] 🔒 تم حذف الرسالة المعدلة من المستخدم {user_id}")
            except Exception as e:
                print(f"[ERROR] فشل حذف الرسالة المعدلة: {e}")
            return True


        lower_text = text.lower()
        # word_count = len(lower_text.split())

        # حماية الفشار: حذف إذا تحتوي على كلمات ممنوعة
        if get_protection_status(chat_id, "الفشار") == 0:
            if any(word in lower_text for word in forbidden_words):
                try:
                    bot.delete_message(message_id)
                    print(f"[DEBUG] 🔒 تم حذف رسالة تحتوي على كلمات محظورة (الفشار) من المستخدم {user_id}")
                except Exception as e:
                    print(f"[ERROR] فشل حذف رسالة الفشار: {e}")
                return True
        if get_protection_status(chat_id, "الكلايش") == 0:
            if 400 <= len(lower_text) <= 499:
                try:
                    bot.delete_message(message_id)
                    print(f"[DEBUG] 🔒 تم حذف رسالة تجاوزت 400 حرف من المستخدم {user_id}")
                except Exception as e:
                    print(f"[ERROR] فشل حذف الرسالة: {e}")
                return True
        if get_protection_status(chat_id, "الفايروس") == 0:
            if len(lower_text) > 500:
                try:
                    # حذف الرسالة
                    bot.delete_message(message_id)
                    print(f"[DEBUG] 🔒 تم حذف رسالة تجاوزت 600 حرف من المستخدم {user_id}")

                    # طرد المستخدم
                    bot.ban_member(chat_id, user_id)
                    print(f"[DEBUG] 🚫 تم طرد المستخدم {user_id} بسبب إرسال فايروس")

                    # اسم المستخدم أو المعرف
                    notice_name = f"@{username}" if username else f"ID:{user_id}"

                    # إرسال رسالة تنبيه في المجموعة
                    bot.send_message(
                        chat_id=chat_id,
                        text=f"🚫 تم طرد المستخدم {notice_name} بسبب إرسال فايروس."
                    )

                except Exception as e:
                    print(f"[ERROR] فشل تنفيذ إجراء الفايروس: {e}")
                return True


        # فحص حماية الهمسة أولاً
        if get_protection_status(chat_id, "الهمسه") == 0:
            if check_and_delete_whisper(bot, update, text, message_id, chat_id, user_id):
                print("[TRACE] تم حذف رسالة الهمسة بنجاح داخل check_and_delete_links")
                return True
            else:
                print("[TRACE] لم يتم حذف رسالة الهمسة داخل check_and_delete_links")


        # باقي الحمايات
        protection_type = detect_message_type(bot, update)

        protection_type = detect_message_type(bot, update)
        if not protection_type:
            return False

        protection_status = get_protection_status(chat_id, protection_type)
        if protection_status == 0:
            try:
                bot.delete_message(message_id)
                print(f"[DEBUG] 🔒 تم حذف الرسالة التي تحتوي على {protection_type} من المستخدم {user_id}")
            except Exception as e:
                print(f"[ERROR] فشل حذف الرسالة: {e}")
            return True

        print("[DEBUG] لا حاجة لحذف الرسالة.")
        return False

    except Exception as e:
        print(f"[ERROR] خطأ في check_and_delete_links: {e}")
        return False

# def is_dev_command(text):
#             lower_text = text.strip().lower()
#             # base_command = get_command_from_text(lower_text, chat_id)
#             dev_commands = [
#                 "رفع مطور", "تنزيل مطور", "مطورين", "اوامر الحماية",
#                 "قفل ", "فتح ", "اغلاق ",
#                 "هلو", "شلونك؟", "بوت", "وجعا"
#             ]
#             return any(lower_text == cmd or lower_text.startswith(cmd) for cmd in dev_commands)

# الحلقة الرئيسية لتشغيل البوت
# ==========================
# الحلقة الرئيسية لتشغيل البوت
# نمرّ على كل الدوال داخل الكلاس TamBot

# ==========================
# # دالة لجلب بيانات الايدي
# def handle_id_command(update):
#     chat_id = bot.get_chat_id(update)

#     # جلب بيانات المرسل
#     sender = update["updates"][0]["message"].get("sender", {})
#     user_id = sender.get("user_id", "غير معروف")
#     fullname = sender.get("name", "غير معروف")
#     username = sender.get("username", "")
#     tag = f"#{username}" if username else "لا يوجد"

#     # النبذة إن وجدت
#     bio = bot.get_construct_text(update)
#     bio_text = bio if bio else "لا يوجد"

#     # استعلام الرتبة من قاعدة البيانات
#     conn = sqlite3.connect("bot_data.sqlite")
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT role FROM roles WHERE user_id=? AND group_id IN (?, 'global')",
#         (str(user_id), str(chat_id))
#     )
#     role_row = cursor.fetchone()
#     conn.close()

#     role = role_row[0] if role_row else "عضو"

#     # صياغة الرد بشكل مرتب وجميل
#     response = (
#         "⊰❳ معلومات المستخدم :\n"
#         "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
#         f"👤 الاسم : {fullname}\n"
#         f"🔹 المعرف : {tag}\n"
#         f"📝 النبذة : {bio_text}\n"
#         f"🏷️ الرتبة : {role}\n"
#         f"🆔 الايدي : {user_id}\n"
#         "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"
#     )
#     return response
import sqlite3

def show_roles_table():
    try:
        with sqlite3.connect("bot_data.sqlite") as conn:
            cursor = conn.cursor()
            # جلب كل البيانات من جدول roles
            cursor.execute("SELECT * FROM roles")
            rows = cursor.fetchall()

            if not rows:
                print("❌ جدول الرتب فارغ.")
                return

            # عرض أسماء الأعمدة
            cursor.execute("PRAGMA table_info(roles)")
            columns = [col[1] for col in cursor.fetchall()]
            print(" | ".join(columns))
            print("-" * 70)

            # عرض الصفوف
            for row in rows:
                print(" | ".join(str(item) for item in row))

    except Exception as e:
        print(f"❌ خطأ أثناء عرض جدول الرتب: {e}")

# استدعاء الدالة
show_roles_table()

# ==========================
# دالة لجلب بيانات الايدي
def handle_id_command(update):
    chat_id = bot.get_chat_id(update)

    # جلب بيانات المرسل
    message = update.get("message", {}) or update.get("updates", [{}])[0].get("message", {})
    sender = message.get("sender", {})
    print("[DEBUG] Sender Data:", sender)

    user_id = sender.get("user_id", "غير معروف")
    fullname = sender.get("name", "غير معروف")
    username = sender.get("username", "")
    user_tag = f"@{username}" if username else "لا يوجد"

    # استعلام جميع الرتب من قاعدة البيانات
    conn = sqlite3.connect("bot_data.sqlite")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, group_id FROM roles WHERE user_id=?",
        (str(user_id),)
    )
    roles_rows = cursor.fetchall()
    conn.close()

    # اختيار الرتب المرتبطة فقط بالمجموعة الحالية أو global
    roles_list = []
    for role_name, gid in roles_rows:
        if gid == str(chat_id) or gid == "global":
            roles_list.append(role_name)

    # إزالة التكرار والحفاظ على الترتيب
    roles_list = list(dict.fromkeys(roles_list))
    if not roles_list:
        roles_list.append("عضو")

    role_text = " ✦ ".join(roles_list)

    # صياغة الرد
    response = (
        "⊰❳ معلومات المستخدم :\n"
        "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
        f"👤 الاسم : {fullname}\n"
        f"🔹 يوزرك : {user_tag}\n"
        f"🆔 المعرف : {user_id}\n"
        f"🏷️ الرتبة : {role_text}\n"
        "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"
    )
    return response

# def handle_id_command(update):
#     chat_id = bot.get_chat_id(update)

#     # جلب بيانات المرسل
#     message = update.get("message", {}) or update.get("updates", [{}])[0].get("message", {})
#     sender = message.get("sender", {})
#     print("[DEBUG] Sender Data:", sender)  # نطبع بيانات أساسية

#     user_id = sender.get("user_id", "غير معروف")
#     fullname = sender.get("name", "غير معروف")
#     username = sender.get("username", "")
#     user_tag = f"@{username}" if username else "لا يوجد"

#     # استعلام جميع الرتب من قاعدة البيانات
#     conn = sqlite3.connect("bot_data.sqlite")
#     cursor = conn.cursor()
#     # استعلام جميع الرتب للمستخدم سواء بالمجموعة الحالية أو global
#     cursor.execute(
#         "SELECT role, group_id FROM roles WHERE user_id=?",
#         (str(user_id),)
#     )
#     roles_rows = cursor.fetchall()

#     roles_list = []
#     for role_name, gid in roles_rows:
#         if gid == str(chat_id):
#             roles_list.append(role_name + " (المجموعة)")
#         elif gid == "global":
#             roles_list.append(role_name + " (عالمي)")

#     # إزالة التكرار
#     roles_list = list(dict.fromkeys(roles_list))  # يحافظ على ترتيب الظهور

#     role = " + ".join(roles_list) if roles_list else "عضو"


#     # صياغة الرد
#     response = (
#         "⊰❳ معلومات المستخدم :\n"
#         "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉\n"
#         f"👤 الاسم : {fullname}\n"
#         f"🔹 يوزرك : {user_tag}\n"
#         f"🏷️ الرتبة : {role}\n"
#         f"🆔 المعرف : {user_id}\n"
#         "┉┉┉┉┉┉┉⦖┉┉┉┉┉┉┉"
#     )
#     return response  # 👈 نرجع النص فقط

# import sqlite3

# def print_users_table():
#     conn = sqlite3.connect("bot_data.sqlite")
#     cursor = conn.cursor()

#     # استعلام كل السجلات من جدول users
#     cursor.execute("SELECT * FROM users")
#     rows = cursor.fetchall()

#     # الحصول على أسماء الأعمدة
#     column_names = [description[0] for description in cursor.description]

#     print("=== محتويات جدول users ===")
#     if not rows:
#         print("الجدول فارغ!")
#     else:
#         # طباعة العنوان
#         print(" | ".join(column_names))
#         print("-" * (len(column_names) * 20))

#         # طباعة كل سجل
#         for row in rows:
#             print(" | ".join(str(item) for item in row))

#     conn.close()

# # تجربة الدالة
# print_users_table()




def main():
    print("✅ البوت يعمل الآن. انتظر رسائل...")

    while True:
        update = bot.get_updates()
        if not update:
            continue
        if check_and_handle_bot_removed(update, group_activation_state):
            print("[MAIN] ⏭️ تم التعامل مع حدث حذف البوت — تخطي هذا التحديث.")
            continue
        # if check_and_handle_bot_added(update):
        #     print("[MAIN] ⏭️ تم التعامل مع حدثاضافة  البوت — تخطي هذا التحديث.")
        #     continue

        user_id_str = str(bot.get_user_id(update))
        chat_id_str = str(bot.get_chat_id(update))

        if not is_authorized(user_id_str, chat_id_str, max_priority=7):
            if check_and_delete_links(bot, update):
                continue


        print("[RAW UPDATE USER DATA]--------------")
        print(json.dumps(update, indent=2, ensure_ascii=False))

        # جلب معلومات أساسية
        text = bot.get_text(update) or ""
        group_id = bot.get_chat_id(update)
        user_id = bot.get_user_id(update)
        message_id = bot.get_message_id(update)
        text_clean = text.strip().lower()
        # ===== تحديث حالة التفعيل من قاعدة البيانات =====
        conn = sqlite3.connect("bot_data.sqlite", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT activated FROM groups WHERE group_id=?", (group_id,))
        group_row = cursor.fetchone()
        activated = group_row and group_row[0] == 1
        group_activation_state[group_id] = activated
        conn.close()

        print(f"[MAIN] group_id={group_id}, activated={activated}, text='{text_clean}'")

        # ===== جمع جميع الأوامر من القاموس في قائمة واحدة =====
        all_commands = [cmd for cmds in ROLES_COMMANDS.values() for cmd in cmds]

        # ===== إذا غير مفعلة =====
        if not activated:
            if text_clean == "تفعيل":
                print("[MAIN] محاولة تفعيل...")
                handle_activation(update)
            elif text_clean in all_commands:  # فقط إذا كان النص أحد الأوامر
                print("[MAIN] محاولة استخدام أمر قبل التفعيل")
                bot.send_message(
                    chat_id=group_id,
                    text="❌ يجب تفعيل البوت أولاً عبر كتابة 'تفعيل' من قِبل مالك المجموعة."
                )
            else:
                print("[MAIN] تجاهل التحديث لأن البوت غير مفعّل ولم يكن أمراً.")
            continue
        # conn = sqlite3.connect("bot_data.sqlite", timeout=10)
        # cursor = conn.cursor()
        # cursor.execute("SELECT activated FROM groups WHERE group_id=?", (group_id,))
        # group_row = cursor.fetchone()
        # activated = group_row and group_row[0] == 1
        # group_activation_state[group_id] = activated
        # conn.close()

        # print(f"[MAIN] group_id={group_id}, activated={activated}, text='{text_clean}'")

        # # ===== إذا غير مفعلة =====
        # if not activated:
        #     if text_clean == "تفعيل":
        #         print("[MAIN] محاولة تفعيل...")
        #         handle_activation(update)
        #     else:
        #         print("[MAIN] تجاهل التحديث لأن البوت غير مفعّل بعد.")
        #         bot.send_message(chat_id=group_id, text= "❌ يجب تفعيل البوت أولاً عبر كتابة 'تفعيل' من قِبل مالك المجموعة.")
        #     continue

        # ===== بعد التفعيل، تنفيذ جميع الأوامر والدوال =====
        is_bot_message = (user_id == bot.get_bot_user_id())
        state_key = (str(group_id), str(user_id))
        if state_key in user_command_state:
            handle_command_state(state_key, text, group_id, message_id, user_id)
            continue

        # استدعاء بقية الدوال
        save_message(group_id, message_id, from_bot=is_bot_message)
        welcome_new_member(bot, update)
        handle_main_owner_commands(update, text, group_id, message_id, user_id, bot)
        handle_shared_rank_common_owner_commands(update, text, group_id, message_id, user_id)
        handle_Manager_command(update, text, group_id, message_id, user_id)
        handle_distinguished_members(update, text, group_id, message_id, user_id)
        global_replies_handler(text, group_id, message_id, user_id)
        group_replies_handler(text, group_id, message_id, user_id)
        auto_reply_handler(text, group_id, message_id)
        initialize_group_protection_settings(group_id)
        # handle_general_responses(update, text, group_id, message_id)


        if get_protection_status(group_id, "الالعاب") == 1 or is_authorized(user_id_str, chat_id_str, max_priority=7):
            if text_clean == "كت":
                question_cut = random.choice(cut_game_questions)
                bot.send_reply_message(
                    text=question_cut,
                    chat_id=group_id,
                    mid=message_id
                )

            elif text_clean == "خيرني":
                question_would_you_rather = random.choice(would_you_rather_questions)
                bot.send_reply_message(
                    text=question_would_you_rather,
                    chat_id=group_id,
                    mid=message_id
                )
            elif text_clean == "اساله" or text_clean == "اسالة" or text_clean == "صارحني" or text_clean == "صراحة"or text_clean == "صراحه":
                    question_truth = random.choice(truth_questions_data_questions)
                    bot.send_reply_message(
                        text=question_truth,
                        chat_id=group_id,
                        mid=message_id
                    )


        if is_dev(user_id):
            if not handle_common_dev_commands(text, group_id, message_id):
                if is_main_dev(user_id):
                    handle_main_dev_commands(update, text, group_id, message_id, user_id)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 تم إيقاف البوت.")

     