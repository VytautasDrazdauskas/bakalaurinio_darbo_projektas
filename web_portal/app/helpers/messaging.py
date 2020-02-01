from flask import json

def RaiseNotification(result, message):
    return json.dumps({'success': result, 'message': message}, ensure_ascii=False, encoding='utf8')