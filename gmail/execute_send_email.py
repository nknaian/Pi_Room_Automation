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
    args = vars(flags.parse_args())
    email_version = args['email_version']
    message_body = args['message_body']
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
    #credentials.invalid = True
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

def send_error_message():
    """Sends an email

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

   
    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "Running master_regulator failed after changes!"
    message_text = "Attempted running returned the following error message:\n\n" + message_body
    
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
    elif email_version == "SendErrorMessage":
        send_error_message()
    elif email_version == "Custom": #For this one user must go into this file and change the variables in send_custom()
        send_custom()
    else:
        print("\nUnrecognized email version...\n")
        input()
if __name__ == '__main__':
    main()
