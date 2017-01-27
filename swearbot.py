import os
import time
from slackclient import SlackClient

import urllib
import string
import re

# rcr.slackbot's ID as an environment variable
BOT_ID = os.environ.get("SLACK_BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def command_regexify(commands):
    if isinstance(commands, dict):
        dict_keys = list(commands.keys())
        for key in dict_keys:
            commands[AT_BOT + ' ' + key] = commands.pop(key)
    elif isinstance(commands, str):
        return AT_BOT + ' ' + commands


def read_db(filename):
    db = dict()
    with open(filename) as input_db:
        for line in input_db:
            key = line.split(',')[0].strip()
            value = int(line.split(',')[1].strip())
            if key not in db:
                db[key] = value
    return db


def write_db(filename, db):
    with open(filename, 'w') as db_file:
        for key in db:
            db_file.write("{},{}\n".format(key, db[key]))


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and "text" in output and "user" in output and output["user"] != BOT_ID:
                return output["channel"].strip(), output["user"].strip(), output["text"].strip()
    return None, None, None


def parse_command(text, users, swear_db, user_db, channel):
    commands = {"add": "pass",
                "highscore": "print_highscore(users, user_db, channel)",
                "swears": "print_swears(swear_db, channel)",
                "help": "print_help(keywords, channel)"}
    keywords = list(commands.keys())
    keywords.sort()
    command_regexify(commands)
    fixed_add = AT_BOT + ' ' + "add" + ' "\w{1,64}" \d{1,}' + '|' + AT_BOT + ' ' + "add" + ' "\w{1,64}"'
    commands[fixed_add] = commands.pop(command_regexify("add"))
    print(commands)
    for command in commands:
        if re.fullmatch(command, text):
            exec(commands[command])
            return
    print("error")


def count_swear(swear_db, message):
    text = "".join([letter for letter in message.lower() if letter in (string.ascii_letters + "ÁÉÍÓÖŐÚÜŰáéíóöőúüű")])
    swear_counter = 0
    for swear in swear_db:
        if swear in text:
            swear_counter += text.count(swear) * swear_db[swear]
    return swear_counter


def print_help(keywords, channel):
    response = "Avaliable commands are *" + "*, *".join(keywords) + "*"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def print_highscore(users, user_db, channel):
    ordered_keys = sorted(user_db, key=user_db.get, reverse=True)
    response = "Swear highscore:\n"
    for key in ordered_keys:
        for user in users:
            if user["id"] == key:
                response += "*{}*: {}\n".format(user["real_name"], user_db[key])
                break
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def print_swears(swear_db, channel):
    ordered_keys = sorted(swear_db)
    response = "Registered *swears* are:\n>>> "
    response += ", ".join(["*{}* ({})".format(key, swear_db[key]) for key in ordered_keys])
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def print_warning(user, users, user_db, channel):
    first_name = ([u["real_name"] for u in users if u["id"] == user][0]).split(' ')[0]
    response = ":bangbang: Hey *{}*! (<@{}>) :bangbang:\n".format(first_name, user)
    response += "You sweared :zipper_mouth_face: and you should feel bad :point_up:. "
    response += "You have *{}* point(s).".format(user_db[user])
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.5  # 0.5 second delay between reading from firehose
    swr_db = read_db("swear_db.txt")
    usr_db = read_db("user_db.txt")

    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users
        users = api_call.get('members')
    if slack_client.rtm_connect():
        print("rcr.slackbot connected and running!")
        while True:
            try:
                rtm_read = slack_client.rtm_read()
            except TimeoutError:
                print("Caught a timeout")
            channel, user, text = parse_slack_output(rtm_read)
            if user and text:
                print(user, text)
                if text == ":deal_robi:":
                    slack_client.api_call("chat.postMessage", channel=channel,
                                          attachments=[{"fallback": "Deal with it!",
                                                        "image_url": "http://i.imgur.com/9PO2N1V.jpg"}])
                elif text.startswith(AT_BOT):
                    parse_command(text, users, swr_db, usr_db, channel)
                swear_val = count_swear(swr_db, text)
                if swear_val:
                    if user in usr_db:
                        usr_db[user] += swear_val
                    else:
                        usr_db[user] = swear_val
                    write_db("user_db.txt", usr_db)
                    print_warning(user, users, usr_db, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
