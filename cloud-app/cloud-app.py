import os
from time import sleep

import requests
from flask import Flask

app = Flask(__name__)

CLOUD_APP_HOST = os.getenv('CLOUD_APP_HOST', '127.0.0.1')
CLOUD_APP_PORT = os.getenv('CLOUD_APP_PORT', 5000)
EDGE_API_URL = os.getenv('EDGE_API_URL', 'http://cluster-dns.edge.edge-app')


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/ready')
def ready():
    sleep(5)  # Sleep for 5s
    return '', 200


@app.route('/edge/<job_type>')
def edge(job_type):
    print(f'Starting {job_type} on the edge')

    try:
        response = requests.get(EDGE_API_URL + '/' + job_type)

        if response.status_code == 200:
            return response.text, 200

        return response.text, 503
    except Exception:
        print('EDGE App exception')

    return 'Edge APP error', 503


if __name__ == "__main__":
    print(f'Started flask Cloud APP')

    app.run(host=CLOUD_APP_HOST, port=CLOUD_APP_PORT)
