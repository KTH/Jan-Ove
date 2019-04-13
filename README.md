# Jan-Ove

```
常青树 Cháng Qīng Shù ("Evergreen Tree")
```

Jan-Ove is a table tennis bot used at KTH to make sure no loss or win goes forgotten.

# How to use

## Configuration

Configuration is done through environment variables:

* (required) `CONNECTION_STRING` - An ODBC connection string to a sql database
* (required) `SLACK_BOT_TOKEN` - The bot app token retrieved from your Slack installation
* (optional) `TRIGGER_TEXT` - The text for the bot to trigger on. Default is `!pingis`
* (optional) `DEBUG` - Set this to whatever to enable debug logging

## Running locally

1) Install docker and make sure it's running
2) [Create a Slack bot app for your workspace](https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace#-create-a-bot)
3) Create a file named `.env` in the project root with the required environment variables (see above)
4) Run `docker-compose up --build`

# How to use

Invite the bot to a channel or use private messaging. Send `!pingis help` to get a list of commands

# Tests

lol, no
