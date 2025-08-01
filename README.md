# BusArrivalBot

Telegram Bot to get bus arrival timings in Singapore

Try it out at @BusArrivalBot

## Setup instructions

This project manages its dependencies using `uv`

[Install it first](https://docs.astral.sh/uv/getting-started/installation/) before proceeding

### Environment values

Create a file `.env` containing the keys from `.env.example`

You will need a bot token from `@BotFather` to host your own instance of the bot

### Start bot

Run an instance of the bot

The dependencies in `pyproject.toml` will be installed automatically

```shell
uv run bot.py
```

## Building and running

```bash
docker build --rm -f Dockerfile -t bus-arrival-bot:0.1.0 .
docker run --name bus-arrival-bot --rm bus-arrival-bot:0.1.0
```

## Milestones

### Milestone 1 (done)

- [x] Search for busses by location and bus stop code
- [x] Host bot on server

### Milestone 2 (done)

- [x] Rate limiting (done)
- [x] Refresh button (done)

### Milestone 3

- [x] Search for bus stop
- [x] Bus route info

### Milestone 4

- [x] Generalise reply handler
- [x] Scheduler for updating stops and routes

### Milestone 5

- [x] Dockerfile
- [ ] autopep8 and pylint configuration

### Milestone 6

- [ ] State busses not in service
- [ ] Save stops as favourites

### Chores

- [ ] Handle memory leak from cache implementation
- [ ] Handle request timeouts and error codes from LTA Datamall
- [ ] Fix comments
- [ ] Typecheck
- [ ] Optimize Dockerfile (currently 479.68 MB)

## Inconsistency of result displays

Searching for bus stops yields the results in a text message, whereas location search displays it as inline keyboard buttons.

The consideration was that inline buttons are not persistent, so it makes it harder to search.

Can consider both approaches to see which provides a better UX.
