import os


class Config:
    # rcr.slackbot's ID and TOKEN as an environment variable
    BOT_ID = os.environ.get("SLACK_BOT_ID")
    BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
    # constants
    AT_BOT = "<@" + BOT_ID + ">"
