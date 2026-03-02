import requests
import sys

def send(text, task_type):
    resp = requests.post('http://localhost:8000/api/nlp/process', json={
        'text': text,
        'task_type': task_type
    })
    print(resp.status_code, resp.text)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python send_task.py "some text" sentiment_analysis')
    else:
        send(sys.argv[1], sys.argv[2])
