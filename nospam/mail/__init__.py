import email
import re
import itertools
from typing import List


class Mail(object):
    def __init__(self, subject: str, sender: str, receiver: str, content: str):
        '''
        :param subject: Subject of the email.
        :param sender: Sender of the email.
        :param receiver: Receiver of the email.
        :param content: Content of the email.
        :returns: Mail object.
        '''
        self.subject = subject
        self.sender = sender
        self.receiver = receiver
        self.content = content

        # Cache preventing duplicate calculation
        self.tokens = []

    def tokenify(self) -> List[str]:
        '''
        Tokenify our email.
        :returns: List of tokens
        '''
        if len(self.tokens) == 0:
            subject_tokens = ['*subject*' +
                              word.lower() for word in re.findall(r'[A-Za-z]+', self.subject)]
            content_tokens = [word.lower() for word in re.findall(
                r'[A-Za-z]+', self.content)]
            sender_tokens = ['*sender*' + self.sender.lower()]
            self.tokens = list(itertools.chain(
                subject_tokens, content_tokens, sender_tokens))
        return self.tokens


def from_file(filename: str) -> Mail:
    '''
    :param filename: Path to the email file.
    :returns: Mail object.
    '''
    with open(filename, encoding='latin-1') as f:
        mail = email.message_from_file(f)
        content = ''
        for part in mail.walk():
            # Only process email parts in plain text and html
            if part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
                content += str(part.get_payload())
        subject = mail.get('subject')
        sender = re.findall(r'<.*>', mail.get('from'))[0][1:-1]
        receiver = mail.get('to')
        return Mail(subject, sender, receiver, content)


def from_string(raw_mail: str) -> Mail:
    '''
    :param filename: Path to the email file.
    :returns: Mail object.
    '''
    mail = email.message_from_string(raw_mail)
    content = ''
    for part in mail.walk():
        # Only process email parts in plain text and html
        if part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
            content += str(part.get_payload())
    subject = mail.get('subject')
    sender = re.findall(r'<.*>', mail.get('from'))[0][1:-1]
    receiver = mail.get('to')
    subject = str(subject)
    return Mail(subject, sender, receiver, content)
