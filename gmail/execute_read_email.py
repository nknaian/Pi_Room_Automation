from __future__ import print_function
import httplib2
import os
import base64
from bs4 import BeautifulSoup

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

#import functions from other python files
import read_email as mail

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
    our_message = messages_that_match[0] #We're only interested in the latest message
    message = mail.GetMimeMessage(service, "me", our_message['id'])
   
    # Go through message and create beautuful soup object containing the 'soup' of the message body html
    messageIsOneLine = True
    for part in message.walk():
        message.get_payload()
        if part.get_content_type() == 'text/plain':
            singleLink = part.get_payload()
            print("Plain text part: \n")
            print(singleLink)
            
        elif part.get_content_type() == 'text/html':
            soup = BeautifulSoup(part.get_payload(), "html.parser")
            messageIsOneLine = False
            print("html part: \n")
            print(part.get_payload())
            

    # Parse html into a list of the urls contained within the message body (can include filter of urls here)
    videos = []
    if messageIsOneLine == True:
        videos.append(singleLink)
        #print(videos)
    else:
        for link in soup.find_all('a'):
            videos.append(link.get('href'))
        #print(videos)

    # Check if file is empty (for later use)
    empty = False
    if os.stat("textUrls.txt").st_size == 0:
        empty = True

    # append urls onto file where urls are contained, putting each one on a new line
    with open("textUrls.txt", "a") as myFile:
        iterator = 0
        for link in videos:
            if empty == True and iterator == 0:
                pass
            else:
                myFile.write("\n")
            myFile.write(link)
            iterator += 1
    
if __name__ == '__main__':
    main()
