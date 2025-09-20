# reply_manager.py
import json
import os

class ReplyManager:
    def __init__(self, file_path="replies.json"):
        self.file_path = file_path
        self.replies = self._load_replies()
        print(f"[TRACE] تم تحميل الردود من الملف: {self.replies}")

    def _load_replies(self):
        """تحميل الردود المحفوظة من الملف"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    print(f"[TRACE] بيانات الردود المُحمّلة من {self.file_path}: {data}")
                    return data
            except json.JSONDecodeError as e:
                print(f"[ERROR] خطأ في تحميل JSON من الملف {self.file_path}: {e}")
                return {}
            except Exception as e:
                print(f"[ERROR] خطأ غير متوقع عند فتح الملف {self.file_path}: {e}")
                return {}
        else:
            print(f"[TRACE] ملف الردود {self.file_path} غير موجود، سيتم إنشاؤه عند الحفظ.")
        return {}

    def _save_replies(self):
        """حفظ الردود إلى الملف"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(self.replies, file, ensure_ascii=False, indent=4)
            print(f"[TRACE] تم حفظ الردود في الملف {self.file_path}: {self.replies}")
        except Exception as e:
            print(f"[ERROR] فشل حفظ الردود في الملف {self.file_path}: {e}")

    def add_reply(self, chat_id, keyword, response):
        """إضافة رد جديد أو تحديث رد قديم مع التحقق من القيم الفارغة"""
        keyword = keyword.strip()
        response = response.strip()

        if not keyword:
            print("[WARNING] لم يتم إدخال كلمة مفتاحية. لا يمكن الحفظ.")
            return False
        if not response:
            print("[WARNING] لم يتم إدخال نص الرد. لا يمكن الحفظ.")
            return False

        chat_id = str(chat_id)
        if chat_id not in self.replies:
            self.replies[chat_id] = {}
            print(f"[TRACE] تم إنشاء مجموعة جديدة في الردود: {chat_id}")

        self.replies[chat_id][keyword] = response
        print(f"[DEBUG] إضافة/تحديث رد للمجموعة {chat_id}: {keyword} -> {response}")
        self._save_replies()
        return True

    def get_reply(self, chat_id, keyword):
        """جلب رد معين في مجموعة"""
        chat_id = str(chat_id)
        reply = self.replies.get(chat_id, {}).get(keyword)
        if reply:
            print(f"[TRACE] تم العثور على الرد للمجموعة {chat_id}, الكلمة '{keyword}': {reply}")
        else:
            print(f"[TRACE] لا يوجد رد للمجموعة {chat_id} للكلمة '{keyword}'")
        return reply

    def get_all_replies(self, chat_id):
        """جلب جميع الردود لمجموعة"""
        chat_id = str(chat_id)
        all_replies = self.replies.get(chat_id, {})
        print(f"[TRACE] جميع الردود للمجموعة {chat_id}: {all_replies}")
        return all_replies

    def delete_reply(self, chat_id, keyword):
        """حذف رد معين"""
        chat_id = str(chat_id)
        if chat_id in self.replies and keyword in self.replies[chat_id]:
            print(f"[DEBUG] حذف الرد '{keyword}' من المجموعة {chat_id}")
            del self.replies[chat_id][keyword]
            self._save_replies()
            return True
        print(f"[WARNING] لا يوجد رد '{keyword}' لحذفه في المجموعة {chat_id}")
        return False
    def delete_all_replies(self, chat_id):
        """حذف جميع الردود الخاصة بمجموعة معينة"""
        chat_id = str(chat_id)
        if chat_id in self.replies and self.replies[chat_id]:
            print(f"[DEBUG] حذف جميع الردود من المجموعة {chat_id}")
            self.replies[chat_id] = {}
            self._save_replies()
            return True
        print(f"[WARNING] لا توجد ردود لحذفها في المجموعة {chat_id}")
        return False
