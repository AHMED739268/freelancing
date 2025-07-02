# classrooms/email_log.py
from collections import deque

email_messages = deque(maxlen=50)

def add_email_message(msg):
    email_messages.appendleft(msg)

def get_all_messages():
    return list(email_messages)
