from piazza_api import Piazza
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import html
import discord


load_dotenv()

# Get the email and password from the .env file
email = os.getenv('PIAZZA_EMAIL')
password = os.getenv('PIAZZA_PASSWORD')


# dataclass to store post data
@dataclass
class Post:
    post_id: str
    class_id: str
    subject: str
    content: str
    tags: list[str]
    instructor_response: str | None
    student_response: str | None
    timestamp: str

    @property
    def post_link(self) -> str:
        '''Gets the link to a post'''
        return f'https://piazza.com/class/{self.class_id}?cid={self.post_id}'

    @property
    def embed(self) -> discord.Embed:
        '''Creates an embed for a post'''
        embed = discord.Embed(
            title=self.subject,
            description=self.content,
            color=discord.Color.blue(),
            url=self.post_link
        )
        embed.set_footer(text=f'{self.timestamp} | A bot by yousef :D | {self.class_id} | {self.post_id}')
        if self.instructor_response:
            embed.add_field(
                name='Instructor Response',
                value=self.instructor_response,
                inline=False
            )
        if self.student_response:
            embed.add_field(
                name='Student Response',
                value=self.student_response,
                inline=False
            )
        if not self.student_response and not self.instructor_response:
            embed.add_field(
                name='No Responses Yet',
                value='Be the first to respond!',
                inline=False
            )
        if self.tags:
            embed.add_field(
                name='Tags',
                value=', '.join(self.tags),
                inline=False
            )
        return embed


def get_posts(class_id: str, *, limit: int | None = None) -> list[Post]:
    '''Returns a list of all posts in the class'''
    p = Piazza()
    p.user_login(email=email, password=password)
    class_data = p.network(class_id)
    posts = class_data.iter_all_posts(limit=limit)
    post_list = []
    for post in posts:
        post_id = get_post_id(post)
        content = get_post_content(post)
        subject = get_post_subject(post)
        tags = get_post_tags(post)
        instructor_response = get_instructor_response(post)
        student_response = get_student_response(post)
        timestamp = get_post_ts(post)
        post_list.append(
            Post(
                post_id,
                class_id,
                subject,
                content,
                tags,
                instructor_response,
                student_response,
                timestamp
            )
        )
    return list(reversed(post_list))


def get_post(class_id: str, p_id: int) -> Post | None:
    '''Returns a post with the given id'''
    p = Piazza()
    p.user_login(email=email, password=password)
    class_data = p.network(class_id)
    post = class_data.get_post(p_id)

    if post is None:
        return None

    post_id = get_post_id(post)
    content = get_post_content(post)
    subject = get_post_subject(post)
    tags = get_post_tags(post)
    instructor_response = get_instructor_response(post)
    student_response = get_student_response(post)
    timestamp = get_post_ts(post)
    return Post(
                post_id,
                class_id,
                subject,
                content,
                tags,
                instructor_response,
                student_response,
                timestamp
            )


def get_student_response(post: dict) -> str | None:
    '''Gets the student response from a post'''
    try:
        return html.unescape(post['children'][0]['history'][0]['content'])
    except IndexError:
        return None
    except KeyError:
        return None


def get_instructor_response(post: dict) -> str | None:
    '''Gets the instructor response from a post'''
    try:
        return html.unescape(post['children'][1]['history'][0]['content'])
    except IndexError:
        return None
    except KeyError:
        return None


def get_post_id(post: dict) -> str:
    '''Gets the post id from a post'''
    return post['nr']


def get_post_ts(post: dict) -> str:
    '''Gets the post timestamp from a post in PST'''
    dt = datetime.strptime(post['created'], '%Y-%m-%dT%H:%M:%SZ')
    offset_hours = 7
    adjusted_dt = dt.replace(tzinfo=None) - timedelta(hours=offset_hours)
    formatted_datetime = adjusted_dt.strftime("%m/%d/%Y at %-I:%M:%S%p") + " PST"
    return formatted_datetime


def get_post_tags(post: dict) -> list[str]:
    '''Gets the tags from a post'''
    return post['tags']


def get_post_subject(post: dict) -> str:
    '''Gets the subject of a post'''
    return post['history'][0]['subject']


def get_post_content(post: dict) -> str:
    '''Gets the content of a post'''
    return html.unescape(post['history'][0]['content'])
