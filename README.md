# Jan-Ove :chart_with_upwards_trend:

```
常青树 Cháng Qīng Shù ("Evergreen Tree")
```

Jan-Ove is a table tennis bot used at KTH to make sure no loss or win goes forgotten.

# How to run

## Requirements

* An MSSQL database (we use an Azure SQL Server at KTH)
* A host with docker installed

## Configuration

Configuration is done through environment variables:

* _required_ `CONNECTION_STRING` - An MSSQL ODBC connection string to a sql database. The bundled `Dockerfile` installs the msodbcsql17 driver, but can easily be modified to install a driver suitable for your need.
* _required_ `SLACK_BOT_TOKEN` - The bot app token retrieved from your Slack installation
* `TRIGGER_TEXT` - The text for the bot to trigger on. Default is `!pingis`
* `DEBUG` - Set this to whatever to enable debug logging

## Running locally

1) Install docker and make sure it's running
2) [Create a Slack bot app for your workspace](https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace#-create-a-bot)
3) Create a file named `.env` in the project root with the required environment variables (see above)
4) Run `docker-compose up --build`

# How to use

First time usage: run the `!pingis initialize-database` command to create all neccessary tables.

Then invite the bot to a channel or use private messaging and send `!pingis help` to get a list of commands.

# TL;DR

1) `!pingis register-player @your-slack-handle`
2) `!pingis register-player @your-arch-nemesis`
3) `!pingis new-season "The new cool season"`
4) (Play an actual game of table tennis)
5) `!pingis register-result @your-slack-handle @your-arch-nemesis 15 0`
6) `!pingis leaderboard`
7) Much win. Such feelings. Great time.

# Tests

Very limited. To run the few that exist:

1) `pipenv install --dev`
2) `./run_unit_tests.sh`
