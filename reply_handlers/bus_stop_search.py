import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot_app_state import get_app_state
from message_formatters.bus_stop_search import bus_stop_search_msg

# search opp heavy
# /search pei
REGEX_SEARCH = r"^\/?search\s*(.*)"
# <STOPS_CHECKSUM>,<PAGE_NUM>,<QUERY>
REGEX_SEARCH_CALLBACK = r"(\w{8})\,(\d{1,3})\,(.{1,50})"

_MAX_QUERY_LENGTH_EXCEEDED = """Unable to process search of more than 50 characters

Please try again with a shorter search query"""

_NO_SEARCH_QUERY = """No search query was given

Use the search command followed by your search query
E.g. `search sentosa`"""

_STALE_SEARCH = """There has been changes to the list of bus stops since you made the search

Please restart the process again by repeating your search query to obtain updated results"""


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    query = update.callback_query

    has_message = message is not None and message.text is not None
    has_query = query is not None and query.data is not None

    app_state = get_app_state(context.application)

    page = 0
    if has_message:
        m = re.match(REGEX_SEARCH, message.text, re.IGNORECASE)
        if m is None:
            return  # unreachable, pacify typechecker
        query_str: str = m.group(1)

        # reject if length > 50
        if len(query_str) > 50:
            await message.reply_text(_MAX_QUERY_LENGTH_EXCEEDED)
            return

        search_query: list[str] = re.split(r"[\s\/\-\,]", query_str)
    elif has_query:
        m = re.match(REGEX_SEARCH_CALLBACK, query.data)
        if m is None:
            return  # unreachable, pacify typechecker

        checksum = m.group(1)
        page = int(m.group(2))
        search_query = re.split(r"\s", m.group(3))

        # end flow if search query is already outdated
        if checksum != app_state.bus_stop_utility.stops_checksum:
            await query.answer()
            await query.edit_message_text(_STALE_SEARCH)
            return

    if len(search_query) == 1 and search_query[0] == "" and has_message:
        await message.reply_text(_NO_SEARCH_QUERY, parse_mode="Markdown")
        return

    possible_stops = app_state.bus_stop_utility.search_possible_stops(search_query)

    # paginate if query result count > 20
    # return inline callback buttons for pagination
    reply_msg = bus_stop_search_msg(possible_stops, page)
    reply_markup: InlineKeyboardMarkup | None = None
    last_page = len(possible_stops) // 20
    if last_page > 0:
        if page == 0:
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Page 2 >",
                            callback_data=f"{app_state.bus_stop_utility.stops_checksum},{page + 1},{' '.join(search_query)}",
                        )
                    ]
                ]
            )
        elif page == last_page:
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"< Page {last_page}",
                            callback_data=f"{app_state.bus_stop_utility.stops_checksum},{page - 1},{' '.join(search_query)}",
                        )
                    ]
                ]
            )
        else:
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"< Page {page}",
                            callback_data=f"{app_state.bus_stop_utility.stops_checksum},{page - 1},{' '.join(search_query)}",
                        ),
                        InlineKeyboardButton(
                            f"Page {page + 2} >",
                            callback_data=f"{app_state.bus_stop_utility.stops_checksum},{page + 1},{' '.join(search_query)}",
                        ),
                    ],
                ]
            )

    if has_message:
        await message.reply_text(text=reply_msg, reply_markup=reply_markup)
    elif has_query:
        await query.answer()
        try:
            await query.edit_message_text(text=reply_msg, reply_markup=reply_markup)
        except BadRequest:
            pass  # ignore errors due to same message being sent
