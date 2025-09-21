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

### Development mode

When developing locally

1. Run the scripts to save the datasets on the disk as `bus_routes.json` and `bus_stops.json`

```bash
# commands to be run from the project root
uv run python -m scripts.fetch_stops
uv run python -m scripts.fetch_routes
```

2. Set `DEVELOPMENT_MODE=True` in the `.env` file.

This loads the bus_routes and bus_stops from the disk, so that the API fetch for all the stops and routes does not happen each time the application is restarted

An empty database will be created in memory which is discarded once the bot is stopped

## Linting and formatting

```bash
uv run ruff check
uv run ruff format
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

- [ ] Refactor into modules by functional responsbility

### Milestone 8

- [ ] [Precommit hooks](https://docs.astral.sh/uv/guides/integration/pre-commit/)
- [ ] CI/CD tests

### Work

- [Chore] Handle request timeouts and error codes from LTA Datamall
- [Chore] Fix comments
- [Chore] Reduce repeated code for bus route directions
- [Feature] DB migration scripts
- [Feature] DB backup mechanism
- [Feature] Paginate search query
- [Feature] Additional bus information such as double decker, bus load
- [Feature] Compare common stops
- [Optimization] Reduce size of Dockerfile (currently 299.53 MB)

## Inconsistency of result displays

Searching for bus stops yields the results in a text message, whereas location search displays it as inline keyboard buttons.

The consideration was that inline buttons are not persistent, so it makes it harder to search.

Can consider both approaches to see which provides a better UX.

## Bot commands

List of commands registered with `@BotFather`

```
help - View usage instructions
list - List saved stops
settings - View user configuration settings
```
