from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

#import functions from other python files
import send_email as mail

############# NOTE: ###############
# If originally created gmail api access on another computer,
# need to add the argument --noauth_local_webserver to the python file
# after setting credentials.invalid equal

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser])#parse_args() <-- I changed this...change back if things are getting weird
    subparsers = flags.add_subparsers(help='prewritten emails to send')
    email_parser = subparsers.add_parser("email")
    email_parser.add_argument('-v', '--version', dest='email_version', required=True,
                        help='Parse the email version')
    email_parser.add_argument('-b', '--body', dest='message_body', required=False,
                        help='argument to pass in message body')

    #### Start args for send_alarm_notification() ####
    email_parser.add_argument('-e', '--email_address', dest='recipient_email_address', required=False,
                        help='argument to pass in email address of recipient')
    email_parser.add_argument('-n', '--name', dest='first_name', required=False,
                        help='argument to pass in name of email recipient')
    email_parser.add_argument('-u', '--url', dest='url', required=False,
                        help='argument to pass in played url')
    email_parser.add_argument('-t', '--time', dest='wake_up_time', required=False,
                        help='argument to pass in name wake_up_time')
    email_parser.add_argument('-f', '--favorited', dest='was_favorited', required=False,
                        help='boolean argument to pass whether the video was favorited')
    email_parser.add_argument('-F', '--failed', dest='did_fail', required=False,
                        help='boolean argument to pass whether the video failed')
    email_parser.add_argument('-a', '--additional_feedback', dest='additional_feedback', required=False,
                        help='string entered by user in response to the video')
    #### End args for send_alarm_notification() ####

    args = vars(flags.parse_args())
    email_version = args['email_version']
    message_body = args['message_body']

    #### Start arg vars for send_alarm_notification() ####
    recipient_email_address = args['recipient_email_address']
    first_name = args['first_name']
    url = args['url']
    wake_up_time = args['wake_up_time']
    was_favorited = args['was_favorited']
    did_fail = args['did_fail']
    additional_feedback = args['additional_feedback']
    #### End args for send_alarm_notification() ####
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret_alarm_control.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    #Uncomment the following if you want to change permissions
    credentials.invalid = True
    #End my addition
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def send_git_pull_request():
    """Sends an email

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)


    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "GitRequest"
    message_text = "Pull"

    message = mail.CreateMessage(sender, to, subject, message_text)
    mail.SendMessage(service, "me", message)

def send_warning_message(): #A warning message corresponds to errors that don't cause the entire program to fail and exit
    """Sends an email

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "warning..."
    message_text = "Received Error Message:\n\n" + message_body

    message = mail.CreateMessage(sender, to, subject, message_text)
    mail.SendMessage(service, "me", message)

def send_error_message(): #An error message corresponds to something that causes the entire program to fail and exit
    """Sends an email

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "Failure!"
    message_text = "Received Error Message:\n\n" + message_body

    message = mail.CreateMessage(sender, to, subject, message_text)
    mail.SendMessage(service, "me", message)

def send_success_message():
    """Sends an email

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)


    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "Success!"
    message_text = ""

    message = mail.CreateMessage(sender, to, subject, message_text)
    mail.SendMessage(service, "me", message)

def send_alarm_notification():
    """Sends an email to the specified email address, addressed to specified person

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    sender = "snoozinforabruisin@gmail.com"
    to = recipient_email_address

    if did_fail == "False":
        subject = "Nick woke up to one of your alarms today!"
        addressing_part = "Dear " + first_name + ",\n\n"
        url_part = "Nick woke up to the following video:\n" + url + "\n"
        wake_up_time_part = "It woke him up in " + wake_up_time + "\n"
        if was_favorited == "True":
            favorited_part = "And Nick favorited your video!"
        else:
            favorited_part = ""
        additional_feedback_part = "\nNick's reaction to the video: " + additional_feedback + "\n"
        end_part = "\n\nRegards,\nSnoozinforabruisin"
        message_text = addressing_part + url_part + wake_up_time_part + favorited_part + additional_feedback_part + end_part

    elif did_fail == "True":
        subject = "Oops...one of your alarms didn't wake Nick up"
        addressing_part = "Dear " + first_name + ",\n\n"
        url_part = "One of your videos was selected this morning:\n" + url + "\n\n" + "...but Nick didn't wake up to it...he might still be snoozin!"
        end_part = "\n\nRegards,\nSnoozinforabruisin"
        message_text = addressing_part + url_part + end_part
    else:
        print("Hmmmm")

    message = mail.CreateMessage(sender, to, subject, message_text)
    mail.SendMessage(service, "me", message)

def send_custom():
    """Sends an email with an attachment

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)


    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "Custom Subject"
    message_text = "custom text"
    filedir = ""
    filename = ""

    if filedir == "":
        message = mail.CreateMessage(sender, to, subject, message_text)
    else:
        message = mail.CreateMessageWithAttachment(sender, to, subject, message_text, filedir, filename)
    mail.SendMessage(service, "me", message)

def main():
    if email_version == "GitPullRequest":
        send_git_pull_request()
    elif email_version == "SendWarningMessage":
        send_warning_message()
    elif email_version == "SendErrorMessage":
        send_error_message()
    elif email_version == "SendSuccessMessage":
        send_success_message()
    elif email_version == "SendAlarmNotification":
        send_alarm_notification()
    elif email_version == "Custom": #For this one user must go into this file and change the variables in send_custom()
        send_custom()
    else:
        print("\nUnrecognized email version...\n")
        input()
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        str_error = str(error)
        print("In send email an error was found:\n" + str_error + "\n")
