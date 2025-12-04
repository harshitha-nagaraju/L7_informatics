from flask import current_app
import smtplib
from email.mime.text import MIMEText




def send_email(subject, body, to_email):
cfg = current_app.config
if not cfg.get('SMTP_SERVER'):
current_app.logger.info('SMTP not configured, skipping email')
return False
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = cfg.get('FROM_EMAIL')
msg['To'] = to_email


s = smtplib.SMTP(cfg.get('SMTP_SERVER'), cfg.get('SMTP_PORT'))
s.starttls()
s.login(cfg.get('SMTP_USER'), cfg.get('SMTP_PASS'))
s.sendmail(cfg.get('FROM_EMAIL'), [to_email], msg.as_string())
s.quit()
return True




def check_and_alert(user, category, spent, budget_amount):
# Notify when exceeding or low on budget (threshold)
cfg = current_app.config
threshold = cfg.get('LOW_BUDGET_THRESHOLD', 0.1)
if budget_amount <= 0:
return
remaining = budget_amount - spent
if remaining < 0:
subject = f'Budget exceeded for {category.name}'
body = f'You have exceeded your budget for {category.name}. Spent: {spent}, Budget: {budget_amount}.'
send_email(subject, body, user.email)
elif remaining <= budget_amount * threshold:
subject = f'Low budget warning for {category.name}'
body = f'Only {remaining:.2f} left in {category.name} budget (Budget {budget_amount}, Spent {spent})'
send_email(subject, body, user.email)
