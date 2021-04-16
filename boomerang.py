import json
import uuid
from datetime import datetime, timedelta, date
from os import environ

import requests
from todoist import TodoistAPI


def headers():
    return {
        'Content-Type': 'application/json',
        'X-Request-Id': str(uuid.uuid4()),
        'Authorization': f'Bearer {environ["TODOIST_TOKEN"]}'
    }


# Re-add online articles
gist = requests.get(environ['GIST_URL']).json()
for link in gist:
    start = datetime.strptime(link['date'], '%m/%d/%Y').date()
    spaces = [7, 14, 28, 56, 112, 224, 364, 364, 364, 364, 364, 364]
    reread_dates = {start + timedelta(days=d) for d in spaces}
    if datetime.today().date() in reread_dates:
        r = requests.post(
            'https://api.todoist.com/rest/v1/tasks',
            data=json.dumps({
                'content': f'Reread [{link["title"]}]({link["url"]})',
            }),
            headers=headers())
