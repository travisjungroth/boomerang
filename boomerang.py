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

# Refresh habits
r = requests.get(
    'https://api.todoist.com/rest/v1/tasks',
    params={
        'filter': 'overdue & #habits & !@noskip',
    },
    headers=headers())
tasks = r.json()
for task in tasks:
    requests.post(
        f"https://api.todoist.com/rest/v1/tasks/{task['id']}",
        data=json.dumps({
            'due_string': f"{task['due']['string']} starting today"
        }),
        headers=headers())

# Daily sort

api = TodoistAPI(environ["TODOIST_TOKEN"])
api.sync()
today = str(date.today())
task_ids_today = [task['id'] for task in api['items'] if task['due'] is not None and task['due']['date'] == today]
morning = [
    3571827834,  # Take breakfast vitamins
    3603880549,  # Plan day
]
afternoon = [
    3575657684,  # Shutdown ritual
    3564394650,  # Record in my voice journal
    3632277292,  # Say three things I’m grateful for
    3564393963,  # Meditate for 20 minutes
    3564404683,  # Work out
    3997794211,  # Half hour of Spanish Pimsleur
    3922955288,  # Take melatonin
    3646525046,  # Put phone away
]


def key(id_: int):
    if id_ in morning:
        return morning.index(id_) - len(morning)
    elif id_ in afternoon:
        return afternoon.index(id_) + 1
    else:
        return 0


task_ids_today.sort(key=key)
ids_to_orders = {id_: i for i, id_ in enumerate(task_ids_today)}
api.items.update_day_orders(ids_to_orders)
api.commit()
