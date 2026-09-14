import re

from telegram import Update
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from message_formatters.bus_stop_search import bus_stop_search_msg

# search opp heavy
# /search pei
REGEX_SEARCH = r"\/?search\s*(.*)"

_NO_SEARCH_QUERY = """No search query was given

Use the search command followed by your search query
E.g. `search sentosa`"""


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message

    if message is None or message.text is None:
        return

    m = re.match(REGEX_SEARCH, message.text, re.IGNORECASE)
    if m is None:
        return  # unreachable, pacify typechecker
    query_str: str = m.group(1)
    query: list[str] = re.split(r"[\s\/\-]", query_str)

    if len(query) == 1 and query[0] == "":
        await message.reply_text(_NO_SEARCH_QUERY, parse_mode="Markdown")
        return

    app_state = get_app_state(context.application)
    possible_stops = app_state.bus_service.search_possible_stops(query)
    reply_msg = bus_stop_search_msg(possible_stops)

    await message.reply_text(text=reply_msg)
