import os
from flask import Flask

app = Flask(__name__)

EDGE_APP_HOST = os.getenv('EDGE_APP_HOST', '127.0.0.1')
EDGE_APP_PORT = os.getenv('EDGE_APP_PORT', 5000)

JOB_STATEFUL = 'stateful'
JOB_STATELESS = 'stateless'


@app.route('/ready')
def ready():
    return '', 200


@app.route('/job/<job_type>')
def job(job_type):
    if job_type not in [JOB_STATEFUL, JOB_STATELESS]:
        return f'Unknown job type {job_type}', 404

    if job_type == JOB_STATEFUL:
        return 'Starting stateful job'
    elif job_type == JOB_STATELESS:
        return 'Starting stateless job'

    # TODO: start the jobs in k8s


if __name__ == "__main__":
    print(f'Started flask Cloud APP')

    app.run(host=EDGE_APP_HOST, port=EDGE_APP_PORT)
