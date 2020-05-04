import random
import re
import time
import datetime
import calendar
import schedule

import gmail.api.creds as creds
import gmail.api.read_email as read_email
import gmail.api.send_email as send_email


### Gmail interface ###

class GmailInterface:
    def __init__(self):
        self.service = creds.get_gmail_service()

    def get_matches(self, subject, days_old):
        """Returns a list of unread emails in the inbox that have a matching
        subject, and are newer than days_old"""
        query = 'subject:{} AND is:unread AND in:inbox AND newer_than:{}d'.format(subject, days_old)
        return read_email.ListMessagesMatchingQuery(self.service, "me", query)

    def get_sender(self, match):
        # Get message
        message = read_email.GetMimeMessage(self.service, "me", match['id'])

        # Get email address of sender
        sender_full = message["From"]
        sender_address = re.search('<(.*)>', sender_full).group(1)
        print("sender address = ", sender_address)
        return sender_address

    def read_message(self, match, end_str):
        """Gets the body of a message that comes before the 'end' identifier,
        and marks the message as 'read'"""
        # Get message
        message = read_email.GetMimeMessage(self.service, "me", match['id'])

        print("message:\n", message)

        # Mark message as read
        msgLabel = { 'removeLabelIds': ['UNREAD'] }
        self.service.users().messages().modify(userId="me", id=match['id'], body= msgLabel).execute()

        # Go through message and capture text of message body
        message_body = ""
        for part in message.walk():
            message.get_payload()
            if part.get_content_type() == 'text/plain':
                message_body = part.get_payload()

        # Only get part of message before 'end' identifier
        message_body = message_body.split(end_str, 1)
        if len(message_body) != 2:
            print("Error: bad formatting. End identifier '{}' not found".format(end_str))
            return None
        else:
            return message_body[0]

    def send(self, to, subject, message_text):
        print("to = ", to)
        sender = "snoozinforabruisin@gmail.com"
        message = send_email.CreateMessage(sender, to, subject, message_text)
        send_email.SendMessage(self.service, "me", message)


### Album Recommendations ###

class AlbumRecs:
    def __init__(self, gmail_iface):
        self.gmail_iface = gmail_iface
        self.album_recs = {}
        random.seed(time.time())

    def get_shuffled_participants(self):
        participants = []
        for participant in self.album_recs.keys():
            participants.append(participant)
        random.shuffle(participants)
        return participants

    def get_shuffled_album_recs(self):
        recs = []
        for rec in self.album_recs.values():
            recs.append(rec)
        random.shuffle(recs)
        return recs

    def send(self):
        to = ""
        for participant in self.get_shuffled_participants():
            to += "{}; ".format(participant)
        subject = "Album recs for week of {}".format(datetime.date.today())
        message_text = ""
        for i, rec in enumerate(self.get_shuffled_album_recs()):
            message_text += "Album Rec {}:\n{}\n".format(i+1, rec)

        self.gmail_iface.send(to, subject, message_text)

    def add(self):
        # Find matching albumrec emails within the last 7 days
        matches = self.gmail_iface.get_matches("albumrec", 7)

        # Add the newest album rec from each sender
        for match in matches:
            sender = self.gmail_iface.get_sender(match)
            if sender not in self.album_recs:
                rec = self.gmail_iface.read_message(match, "Enjoy |--|")
                if rec:
                    self.album_recs[sender] = rec


### Serving Function ###

def serve_album_recs():
    # Create gmail interface
    gmail_iface = GmailInterface()

    # Create album recs
    album_recs = AlbumRecs(gmail_iface) 

    # Add album recs that have been recieved
    album_recs.add()
    
    # Send the message
    album_recs.send()
            

### Main ###

def main():
    serve_album_recs()
    # schedule.every().monday.at("14:49").do(serve_album_recs)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

if __name__ == '__main__':
    main()

# while True:
#     album_rec = poll_for_albums()