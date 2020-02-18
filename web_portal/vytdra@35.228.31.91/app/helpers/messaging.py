from flask import json

def raise_notification(result, message):
    return json.dumps({'success': result, 'message': message}, ensure_ascii=False, encoding='utf8')