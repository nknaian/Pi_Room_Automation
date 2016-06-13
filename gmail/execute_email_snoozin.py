from __future__ import print_function
import httplib2
import os
import base64
from bs4 import BeautifulSoup
import subprocess
import time
import shlex

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

#import functions from other python files
import read_email as mail

############# NOTE: ###############
# If originally created gmail api access on another computer,
# need to add the argument --noauth_local_webserver to the python file
# after setting credentials.invalid equal



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser])#parse_args() <-- I changed this...change back if things are getting weird
    subparsers = flags.add_subparsers(help='types poll_mode')
    poll_parser = subparsers.add_parser("poll")
    poll_parser.add_argument('-m', '--mode', dest='poll_mode', required=True,
                        help='Parse the polling mode')
    args = vars(flags.parse_args())
    poll_mode = args['poll_mode']
except ImportError:
    flags = None

# Set up subparser for polling type


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

def FilterMessageBody(messageBody, videoList):
    tempVideo = ""
    for char in messageBody:
        if (char == "\r") or (char == '\t') or (char == '\n'):
            if (tempVideo[:7] == "http://") or (tempVideo[:8] == "https://"):
                videoList.append(tempVideo)
            tempVideo = ""

        else:
            tempVideo += char


def poll_for_urls():
    """Checks inbox for message with certain subject line, prints a snippet of the message

    Creates a Gmail API service object and then querys for the latest of a specific email, gets
    that email, then prints the list of urls found (only urls are detected)
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    # Search inbox for message we're looking for and create MimeMessage of object
    query = 'subject:AddUrls AND is:unread AND in:inbox'
    messages_that_match = mail.ListMessagesMatchingQuery(service, "me", query)
    if not messages_that_match:
        exit(0) # No new messages...exiting with 0
    our_message = messages_that_match[0] #We're only interested in the latest message
    message = mail.GetMimeMessage(service, "me", our_message['id'])

    # Mark message as read
    msgLabel = { 'removeLabelIds': ['UNREAD'] }
    service.users().messages().modify(userId="me", id=our_message['id'], body= msgLabel).execute()
    
    # Go through message and capture text of message body
    for part in message.walk():
        message.get_payload()
        if part.get_content_type() == 'text/plain':
            messageBody = part.get_payload()

    # Filter message body into a list of the youtube videos (right now will put any http link in the list)
    videos = []
    FilterMessageBody(messageBody, videos)#, garbage) remove garbage after test

    # Check if file is empty (for later use)
    empty = False
    if os.stat("/home/pi/Desktop/Random_urls").st_size == 0:
        empty = True

    # append urls onto file where urls are contained, putting each one on a new line
    with open("/home/pi/Desktop/Random_urls", "a") as myFile:
        iterator = 0
        for link in videos:
            if empty == True and iterator == 0:
                pass
            else:
                myFile.write("\n")
            myFile.write(link)
            iterator += 1
    
    print("\nNew videos addded:\n")
    print(videos)
    print("\n")
    

def poll_for_heater_requests():
    """Checks inbox for message with certain subject line, prints a snippet of the message

    Creates a Gmail API service object and then querys for the latest of a specific email, gets
    that email, then prints the list of urls found (only urls are detected)
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # Search inbox for message we're looking for and create MimeMessage of object
    query = 'subject:Heater AND is:unread AND in:inbox'
    messages_that_match = mail.ListMessagesMatchingQuery(service, "me", query)
    if not messages_that_match:
        exit(0) # No new messages...exiting with 0
    our_message = messages_that_match[0] #We're only interested in the latest message
    message = mail.GetMimeMessage(service, "me", our_message['id'])

    # Mark message as read
    msgLabel = { 'removeLabelIds': ['UNREAD'] }
    service.users().messages().modify(userId="me", id=our_message['id'], body= msgLabel).execute()
    
    # Go through message and capture text of message body
    for part in message.walk():
        message.get_payload()
        if part.get_content_type() == 'text/plain':
            messageBody = part.get_payload()


    # Check if file is empty (for later use)
    empty = False
    if os.stat("/home/pi/Desktop/Random_urls").st_size == 0:
        empty = True

    # overwrite whatever was in the buffer before with new heater state request
    with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/heater_state_buffer", "w") as myFile: #Note: buffer must be in same folder as this file
      myFile.write(messageBody)

def poll_for_alarm_requests():
    """Checks inbox for message with certain subject line, prints a snippet of the message

    Creates a Gmail API service object and then querys for the latest of a specific email, gets
    that email, then prints the list of urls found (only urls are detected)
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # Search inbox for message we're looking for and create MimeMessage of object
    query = 'subject:Alarm AND is:unread AND in:inbox'
    messages_that_match = mail.ListMessagesMatchingQuery(service, "me", query)
    if not messages_that_match:
        exit(0) # No new messages...exiting with 0
    our_message = messages_that_match[0] #We're only interested in the latest message
    message = mail.GetMimeMessage(service, "me", our_message['id'])

    # Mark message as read
    msgLabel = { 'removeLabelIds': ['UNREAD'] }
    service.users().messages().modify(userId="me", id=our_message['id'], body= msgLabel).execute()
    
    # Go through message and capture text of message body
    for part in message.walk():
        message.get_payload()
        if part.get_content_type() == 'text/plain':
            messageBody = part.get_payload()


    # overwrite whatever was in the buffer before with new heater state request
    with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/alarm_state_buffer", "w") as myFile: #Note: buffer must be in same folder as this file
      myFile.write(messageBody)

def poll_for_git_requests():
    """Checks inbox for message with certain subject line, prints a snippet of the message

    Creates a Gmail API service object and then querys for the latest of a specific email, gets
    that email, then prints the list of urls found (only urls are detected)
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # Search inbox for message we're looking for and create MimeMessage of object
    query = 'subject:GitRequest AND is:unread AND in:inbox'
    messages_that_match = mail.ListMessagesMatchingQuery(service, "me", query)
    if not messages_that_match:
        exit(0) # No new messages...exiting with 0
    our_message = messages_that_match[0] #We're only interested in the latest message
    message = mail.GetMimeMessage(service, "me", our_message['id'])

    # Mark message as read
    msgLabel = { 'removeLabelIds': ['UNREAD'] }
    service.users().messages().modify(userId="me", id=our_message['id'], body= msgLabel).execute()
    
    # Go through message and capture text of message body
    for part in message.walk():
        message.get_payload()
        if part.get_content_type() == 'text/plain':
            messageBody = part.get_payload()

    # Decide action based on what kind of git request it is
    if messageBody == "Pull":
        git_pull_command = "git pull origin master"
        #git_pull_out = subprocess.check_output(shlex.split(git_pull_command), cwd="/home/pi/Desktop/Git_repo/Pi_Room_Automation" ) #temporarily commenting out so we don't overwrite current work
        
      
    else:
        print("\nUnrecognized GitRequest...\n")
        input()
      
def main():

    if poll_mode == "AddUrls":
        poll_for_urls()
    elif poll_mode == "HeaterRequest":
        poll_for_heater_requests()
    elif poll_mode == "AlarmRequest":
        poll_for_alarm_requests()
    elif poll_mode == "GitPullRequest":
        poll_for_git_requests()
    else:
        print("\nUnrecognized polling mode...\n")
        input()


if __name__ == '__main__':
    main()

