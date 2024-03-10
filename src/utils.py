import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

from src.config import db_path, account, password, receiver, email_host, email_port


def sql_select_all(sql):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        values = cursor.fetchall()
        return values
    except Exception as e:
        print(f"异常: {e}")
    finally:
        cursor.close()
        conn.close()


def sql_execute(sql, param_list=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, param_list)
        conn.commit()
    except Exception as e:
        print(f"异常: {e}")
    finally:
        cursor.close()
        conn.close()


def send_email(subject, data):
    message = MIMEMultipart()
    message['From'] = account
    message['Subject'] = subject

    html_table = pd.DataFrame(data).to_html(index=False)
    body = MIMEText(html_table, 'html')
    message.attach(body)

    try:
        s = smtplib.SMTP_SSL(email_host, email_port)
        s.login(account, password)
        s.sendmail(account, receiver, message.as_string())
        s.quit()
    except smtplib.SMTPException as e:
        print(e)
