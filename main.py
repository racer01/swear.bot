import time
from slackclient import SlackClient

import urllib
import string
import re

from command import Command
from commands import Commands
from config import Config
from db import DB

# instantiate Slack client
slack_client = SlackClient(Config.BOT_TOKEN)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and "text" in output and "user" in output and output["user"] != Config.BOT_ID:
                return output["channel"].strip(), output["user"].strip(), output["text"].strip()
    return None, None, None


def parse_command(commands, text):
    for command in commands:
        if re.fullmatch(command.regex_name, text):
            return command.command
    if text.startswith(Config.AT_BOT):
        return str("Commands.error(keywords)")
    else:
        return None, None


def count_swear(swear_db, message):
    text = "".join([letter for letter in message.lower() if letter in (string.ascii_letters + "ÁÉÍÓÖŐÚÜŰáéíóöőúüű")])
    swear_counter = 0
    for swear in swear_db.data:
        if swear in text:
            swear_counter += text.count(swear) * swear_db.data[swear]
    return swear_counter


def print_message(channel, response, attachment_image_url="", attachment_text=""):
    if response is not None:
        slack_client.api_call("chat.postMessage", channel=channel, text=response,
                              attachments=[{"fallback": attachment_text,
                                            "image_url": attachment_image_url}],
                              as_user=(False if not response else True))


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.5  # 0.5 second delay between reading from firehose
    swr_db = DB("swear_db.txt")
    usr_db = DB("user_db.txt")
    commands = [Command("add", "Commands.add(text, user, usernames[user], swr_db)",
                        'Add a word to the swear database. Usage: `@bot add "wordtoadd" [0..3]`',
                        '{0} add ".{{1,64}}" -?\d{{1,}}|{0} add ".{{1,64}}"'.format(Config.AT_BOT)),
                Command("highscore", "Commands.highscore(usernames, usr_db)", "List users' profanity."),
                Command("swears", "Commands.swears(swr_db)", "List all monitored swearwords."),
                Command("help", "Commands.help(keywords)", "Show this help message."),
                Command("", "'', 'Deal with it!', 'http://i.imgur.com/9PO2N1V.jpg'", "", ":deal_robi:")]
    keywords = {command.name: command.description for command in commands if command.name}
    usernames = {}

    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users
        users = api_call.get('members')
        usernames = {user["id"]: user["real_name"] for user in users if "real_name" in user}
    else:
        raise ConnectionError()
    if slack_client.rtm_connect():
        print("swear.bot connected and running!")
        while True:
            try:
                rtm_read = slack_client.rtm_read()
            except TimeoutError:
                print("Caught a timeout")
                continue
            except ConnectionError:
                print("Caught a connection error")
                continue
            channel, user, text = parse_slack_output(rtm_read)
            response_text, response_image = "", ""
            if user and text:
                print(user, text)
                swear_val = count_swear(swr_db, text)
                if swear_val:
                    if user in usr_db.data:
                        usr_db.data[user] += swear_val
                    else:
                        usr_db.data[user] = swear_val
                    usr_db.write()
                    print_message(channel, Commands.warning(user, usernames[user], usr_db))
                exec("response_text, response_image = {}".format(parse_command(commands, text)))
                print_message(channel, response_text, response_image)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
