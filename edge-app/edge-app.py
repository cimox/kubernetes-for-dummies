import os

from flask import Flask
from kubernetes import client, config

app = Flask(__name__)

EDGE_APP_HOST = os.getenv('EDGE_APP_HOST', '127.0.0.1')
EDGE_APP_PORT = os.getenv('EDGE_APP_PORT', 5000)
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'job-app')
CONTAINER_IMAGE = os.getenv('CONTAINER_IMAGE', 'cimox/job-app:0.0.6')

JOB_STATEFUL = 'stateful'
JOB_STATELESS = 'stateless'
JOB_NAME = os.getenv('JOB_NAME', 'job-app-')

# config.load_kube_config()
config.load_incluster_config()
batch_v1 = client.BatchV1Api()


def create_job_object(job_type, fib_n):
    # Configurate env variables
    envs = [
        client.V1EnvVar(name='JOB_TYPE', value=job_type),
        client.V1EnvVar(name='FIB_N', value=fib_n)
    ]

    # Configurate VolumeMounts
    volume_mount = client.V1VolumeMount(
        mount_path='/mnt/storage', name='storage'
    )

    # Configurate resource requests and limits
    resources = client.V1ResourceRequirements(
        requests={
            'memory': '64Mi', 'cpu': '250m'
        },
        limits={
            'memory': '128Mi', 'cpu': '500m'
        }
    )

    # Configurate Pod template container
    container = client.V1Container(
        name=CONTAINER_NAME,
        image=CONTAINER_IMAGE,
        env=envs,
        volume_mounts=[volume_mount],
        resources=resources
    )

    # Configure Volume template
    if job_type == JOB_STATEFUL:
        volume = client.V1Volume(
            name='storage',
            host_path={
                'path': '/c/minikube-pv'
            }
        )
    else:
        volume = client.V1Volume(
            name='storage',
            empty_dir={}
        )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "job-app"}),
        spec=client.V1PodSpec(
            restart_policy="Never",
            containers=[container],
            volumes=[volume]
        )
    )

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=1
    )

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(generate_name=JOB_NAME),
        spec=spec
    )

    return job


def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="jobs"
    )
    print("Job created. status='%s'" % str(api_response.status))

    return api_response.status


@app.route('/ready')
def ready():
    return '', 200


@app.route('/job/<job_type>/fib_n/<fib_n>')
def job(job_type, fib_n):
    if job_type not in [JOB_STATEFUL, JOB_STATELESS]:
        return f'Unknown job type {job_type}', 404

    job = create_job_object(job_type, fib_n)

    if job_type == JOB_STATEFUL:
        create_job(batch_v1, job)
        return 'Starting stateful job'
    elif job_type == JOB_STATELESS:
        create_job(batch_v1, job)
        return 'Starting stateless job'


if __name__ == "__main__":
    print(f'Started flask Cloud APP')

    app.run(host=EDGE_APP_HOST, port=EDGE_APP_PORT)
