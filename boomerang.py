import json
import uuid
from datetime import date, timedelta, datetime
from os import environ

import requests

gist = requests.get(environ['GIST_URL']).json()
for link in gist:
    start_split = [int(x) for x in link['date'].split('/')]
    start = date(month=start_split[0], day=start_split[1], year=start_split[2])
    spaces = [7, 14, 28, 56, 112, 224, 364, 364, 364, 364, 364, 364]
    reread_dates = {start + timedelta(days=d) for d in spaces}
    if datetime.today().date() in reread_dates:
        r = requests.post(
            'https://api.todoist.com/rest/v1/tasks',
            data=json.dumps({
                'content': f'Reread [{link["title"]}]({link["url"]})',
            }),
            headers={
                'Content-Type': 'application/json',
                'X-Request-Id': str(uuid.uuid4()),
                'Authorization': f'Bearer {environ["TODOIST_TOKEN"]}'
            })
