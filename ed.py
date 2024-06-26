from edapi import EdAPI
from datetime import datetime, timedelta
import discord


def get_threads(amt: int, course_id: int) -> list:
    ed = EdAPI()
    ed.login()
    threads = ed.list_threads(course_id=course_id, limit=amt)
    ret_threads = []
    for thread in threads:
        if 'is_private' in thread and thread["is_private"]:
            continue
        ret_threads.append(dict(thread))
    return ret_threads


def get_thread(id: int) -> dict:
    ed = EdAPI()
    ed.login()
    thread = ed.get_thread(id)
    if 'is_private' in thread and thread["is_private"]:
        raise Exception("Thread is private")
    return dict(thread)


def get_course_thread(course_id: int, thread_number: int) -> dict:
    ed = EdAPI()
    ed.login()
    thread = ed.get_course_thread(course_id, thread_number)
    if 'is_private' in thread and thread["is_private"]:
        raise Exception("Thread is private")
    return dict(thread)


def get_title(thread: dict) -> str:
    return thread["title"]


def get_document(thread: dict) -> str:
    return thread["document"]


def get_author(thread: dict) -> str | None:
    try:
        author = thread["user"]["name"]
        return author
    except TypeError:
        return None


def get_category(thread: dict) -> str:
    return thread["category"]


def break_string_to_thousands(string: str) -> list[str] | None:
    x = len(string) // 1000
    str_list = []
    for i in range(x + 1):
        if i == x:
            str_list.append(string)
        else:
            str_list.append(string[:1000])
            string = string[1000:]

    if len(str_list[-1]) == 0:
        del str_list[-1]

    return str_list


def get_link(thread: dict) -> str:
    return (
        f'https://edstem.org/us/courses/{thread["course_id"]}/discussion/{thread["id"]}'
    )


def get_reply_link(reply: dict) -> str:
    return f'https://edstem.org/us/courses/{reply["course_id"]}/discussion/{reply["thread_id"]}?comment={get_id(reply)}'


def get_id(thread: dict) -> str:
    return thread["id"]


def get_course_id(thread: dict) -> str:
    return thread["course_id"]


def get_is_anonymous(thread: dict) -> bool:
    return bool(thread["is_anonymous"])


def get_is_pinned(thread: dict) -> bool:
    return bool(thread["is_pinned"])


def get_date(thread: dict) -> datetime:
    datestring = thread["created_at"]
    datestring = datestring[:-3] + datestring[-2:]
    dt = datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt


def get_date_string(thread: dict) -> str:
    datestring = thread["created_at"]
    datestring = datestring[:-3] + datestring[-2:]
    dt = datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%f%z")
    offset_hours = 19
    adjusted_dt = dt.replace(tzinfo=None) - timedelta(hours=offset_hours)
    formatted_datetime = adjusted_dt.strftime("%m/%d/%Y at %-I:%M:%S%p") + " PST"
    return formatted_datetime


def make_embed(thread: dict, color) -> discord.Embed:
    try:
        author = get_author(thread) + ', '
    except KeyError:
        author = 'Anonymous, ' if get_is_anonymous(thread) else ''
    except TypeError:
        author = ''

    title = f"{get_title(thread)}: {author}in {get_category(thread)}"

    document = get_document(thread)
    if len(document) > 4000:
        document = document[:4000] + "..."

    link = get_link(thread)

    embed = discord.Embed(title=title, url=link, description=document, color=color)
    embed.set_footer(
        text=f"{get_date_string(thread)} | A bot by yousef :D | {get_course_id(thread)} | {get_id(thread)}"
    )
    return embed


def filter_threads(threads: list[dict], category: str, pinned_ok: bool) -> list[dict]:
    filtered_threads = []
    for thread in threads:
        if not pinned_ok and thread["is_pinned"]:
            continue
        if bool(thread["is_private"]):
            continue
        if category == 'All' or thread["category"] == category:
            filtered_threads.append(thread)
    return filtered_threads


if __name__ == "__main__":
    thread = get_course_thread(57105, 45)
    for key in thread:
        print(key, thread[key])
