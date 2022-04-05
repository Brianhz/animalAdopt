from email import message
import smtplib
from smtplib import SMTPHeloError, SMTPAuthenticationError, SMTPNotSupportedError, SMTPException
import os
from email.message import EmailMessage

#email send#
# Email_ADDRESS = os.environ.get('EMAIL_USER')
# Email_PASSWORD = os.environ.get('EMAIL_PASS')
Email_ADDRESS = "brian.test10000@gmail.com"
Email_PASSWORD = "brian.10000"


msg = EmailMessage()
msg['Subject'] = 'Test5'
msg['From'] = Email_ADDRESS
msg['To'] = 'brian.test10000@gmail.com'
msg.set_content('Test6')

# with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    errorFound = False
    try:
        smtp.login(Email_ADDRESS, Email_PASSWORD)
    except SMTPHeloError:
        print("SMTPHeloError")
        errorFound = True
    except SMTPAuthenticationError:
        print("SMTPAuthenticationError")
        errorFound = True
    except SMTPNotSupportedError:
        print("SMTPNotSupportedError")
        errorFound = True
    except SMTPException:
        print("SMTPException")
        errorFound = True
    except:
        print('smtp_login found error')
        errorFound = True

    if errorFound:
        print('No action since login smtp server failed')
    else:
        subject = 'test for brian'
        body = 'test for brian on 2022-04-05'
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(Email_ADDRESS, 'anthony.1120.h@gmail.com', msg)
