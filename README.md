# BusArrivalBot

Telegram Bot to get bus arrival timings in Singapore

Try it out at @BusArrivalBot

## Setup instructions

This project manages its dependencies using `pipenv`

[Install it first](https://pipenv.pypa.io/en/latest/index.html#install-pipenv-today) before proceeding

### Environment values

Create a file `.env` containing the keys from `.env.example`

You will need a bot token from `@BotFather` to host your own instance of the bot

### Install dependencies

Install the dependencies from `Pipefile` and `Pipfile.lock`

```shell
python -m pipenv install
```

### Start virtual environment

Start the virtual environment with the `pipenv shell`

```shell
python -m pipenv shell
```

Use `python -m` instead of just `pipenv shell` allows command history to be retained in the shell

### Start bot

Run an instance of the bot

Ensure that the virtual environment has been activated before running the command

```shell
python -m bot
```

## Milestones

### Milestone 1 (done)

- Search for busses by location and bus stop code (done)
- Host bot on server (done)

### Milestone 2 (done)

- Rate limiting (done)
- Refresh button (done)

### Milestone 3

- Search for bus stop
- Bus route info

### Milestone 4

- Save stops as favourites
