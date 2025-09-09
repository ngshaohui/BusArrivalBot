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

## Testing

```bash
uv run pytest
```

## Building and running with Docker

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
- [x] formatter and linter configuration

### Milestone 6

- [x] Save stops as favourites
- [x] Handle memory leak from cache implementation
- [x] Integrate pytest framework

### Milestone 7

### Work

- [ ] [Chore] Update help command
- [ ] [Chore] Explore loading data from local files, no need to call API repeatedly when doing development
- [ ] [Chore] Explore command to launch app in staging development mode
- [ ] [Chore] Handle request timeouts and error codes from LTA Datamall
- [ ] [Chore] Fix comments
- [ ] [Chore] Reduce repeated code for bus route directions
- [ ] [Feature] DB migration scripts
- [ ] [Feature] Paginate search query
- [ ] [Feature] Additional bus information such as double decker, bus load
- [ ] [Feature] Compare common stops
- [ ] [Optimization] Reduce size of Dockerfile (currently 299.24 MB)

## Inconsistency of result displays

Searching for bus stops yields the results in a text message, whereas location search displays it as inline keyboard buttons.

The consideration was that inline buttons are not persistent, so it makes it harder to search.

Can consider both approaches to see which provides a better UX.
