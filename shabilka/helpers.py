# coding=utf-8
import json

import itertools
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def return_dict_combinations(d):
    assert isinstance(d, dict), "You should pass dictionary to init this object"
    allNames = sorted(d)
    combinations = itertools.product(*(d[name] for name in allNames))
    res = []
    for comb in combinations:
        res.append(zip(allNames, comb))
    return res


def read_init(cls):
    def read(filepath):
        class_ = cls

        with open(filepath, 'r') as f:
            records_json = json.load(f)

        res = []
        for record in records_json:
            try:
                res.append(class_(**record))
            except Exception as e:
                pass

        return res

    return read


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def sendemail_via_gmail(gmail_user, gmail_password, to, subject, body):
    assert isinstance(to, list), "to must be list of emails"
    import smtplib

    msg = MIMEMultipart()  # create a message
    sent_from = gmail_user
    msg['From'] = sent_from
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg=msg, from_addr=sent_from, to_addrs=[to])
        server.close()

        print('Email sent!')
    except Exception:
        print('Something went wrong during email notification sending')
