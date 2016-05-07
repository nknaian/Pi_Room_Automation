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
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
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

def main():
    """Sends an email with an attachment

    Creates a Gmail API service object and then creates an email and sends that email
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

   
    sender = "snoozinforabruisin@gmail.com"
    to = "snoozinforabruisin@gmail.com"
    subject = "GitRequest"
    message_text = "Pull"
    filedir = ""
    filename = ""

    if filedir == "":
        message = mail.CreateMessage(sender, to, subject, message_text)
    else:
        message = mail.CreateMessageWithAttachment(sender, to, subject, message_text, filedir, filename)
    mail.SendMessage(service, "me", message)
    
if __name__ == '__main__':
    main()
