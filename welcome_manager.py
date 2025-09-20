import json
import os

class WelcomeManager:
    def __init__(self, file_path="welcome_messages.json"):
        self.file_path = file_path
        self.welcome_messages = self._load_welcomes()
        print(f"[TRACE] تم تحميل الترحيبات من الملف: {self.welcome_messages}")

    def _load_welcomes(self):
        """تحميل الترحيبات المحفوظة من الملف"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    print(f"[TRACE] بيانات الترحيب المُحمّلة من {self.file_path}: {data}")
                    return data
                except json.JSONDecodeError as e:
                    print(f"[ERROR] خطأ في تحميل JSON: {e}")
                    return {}
        print(f"[TRACE] ملف الترحيب {self.file_path} غير موجود، سيتم إنشاء ملف جديد عند الحفظ.")
        return {}

    def _save_welcomes(self):
        """حفظ الترحيبات إلى الملف"""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.welcome_messages, file, ensure_ascii=False, indent=4)
        print(f"[TRACE] تم حفظ الترحيبات في الملف {self.file_path}: {self.welcome_messages}")

    def add_welcome(self, chat_id, message):
        """إضافة أو تحديث ترحيب لمجموعة"""
        self.welcome_messages[str(chat_id)] = message
        print(f"[DEBUG] إضافة/تحديث الترحيب للمجموعة {chat_id}: {message}")
        self._save_welcomes()
        return True

    def get_welcome(self, chat_id):
        """جلب ترحيب مجموعة"""
        welcome = self.welcome_messages.get(str(chat_id))
        print(f"[TRACE] جلب الترحيب للمجموعة {chat_id}: {welcome}")
        return welcome

    def delete_welcome(self, chat_id):
        """حذف ترحيب مجموعة"""
        if str(chat_id) in self.welcome_messages:
            print(f"[DEBUG] حذف الترحيب الحالي للمجموعة {chat_id}")
            del self.welcome_messages[str(chat_id)]
            self._save_welcomes()
            return True
        print(f"[TRACE] لا يوجد ترحيب محفوظ لحذف المجموعة {chat_id}")
        return False
