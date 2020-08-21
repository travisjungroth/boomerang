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
    due_string = task['due']['string']
    due_string = due_string if due_string.endswith(' starting today') else f'{due_string} starting today'
    requests.post(
        f"https://api.todoist.com/rest/v1/tasks/{task['id']}",
        data=json.dumps({
            'due_string': due_string
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
    3632277292,  # Say three things I’m grateful for
    # 3564394650,  # Record in my voice journal
]
afternoon = [
    3564393963,  # Meditate for 10 minutes
    3564404683,  # Bodyweight workout
    3575657684,  # Shutdown ritual
    # 3997794211,  # Roll and Spanish
    3922955288,  # Take night vitamins
    4103403945,  # Make sure phone VPN is on
    4013318231,  # Log habits
    3646525046,  # Put phone away
    4088458451,  # Put in braces
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
