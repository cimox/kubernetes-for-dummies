import os
from uuid import uuid4

from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException

NAMESPACE = os.getenv('NAMESPACE', 'jobs')
JOB_NAME = os.getenv('JOB_NAME', str(uuid4()))
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'job-app')
CONTAINER_IMAGE = os.getenv('CONTAINER_IMAGE', 'cimox/job-app:0.0.6')

JOB_TYPE = os.getenv('JOB_TYPE', 'stateful')
FIB_N = int(os.getenv('FIB_N', 35))


def create_job_object():
    # Configurate env variables
    envs = [
        client.V1EnvVar(name='JOB_TYPE', value=JOB_TYPE),
        client.V1EnvVar(name='FIB_N', value='35')
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
    volume = client.V1Volume(
        name='storage',
        host_path={
            'path': '/c/minikube-pv'
        }
    )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "pi"}),
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
        metadata=client.V1ObjectMeta(name=JOB_NAME),
        spec=spec
    )

    return job


def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="jobs"
    )
    print("Job created. status='%s'" % str(api_response.status))


if __name__ == '__main__':
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    # Create a job object with client-python API. The job we
    # created is same as the `pi-job.yaml` in the /examples folder.
    job = create_job_object()

    create_job(batch_v1, job)
