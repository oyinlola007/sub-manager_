import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import cogs.config as config
import cogs.strings as strings


def send_mail(you):
	me = config.SENDER_MAIL
	me_password =config.SENDER_PASSWORD

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = strings.MESSAGE_SUBJECT
	msg['From'] = strings.MESSAGE_FROM
	msg['To'] = you

	# Create the body of the message (a plain-text and an HTML version).


	# Record the MIME types of both parts - text/plain and text/html.
	part2 = MIMEText(strings.HTML, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part2)
	# Send the message via local SMTP server.
	mail = smtplib.SMTP('smtp.gmail.com', 587)

	mail.ehlo()

	mail.starttls()

	mail.login(me, me_password)
	mail.sendmail(me, you, msg.as_string())
	mail.quit()
