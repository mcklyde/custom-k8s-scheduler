
from pod_scheduler import schedule_pods, scheduler_name, default_namespace
from kubernetes import client, config, utils
import yaml
import os
import random
import time

def populate_pods(api_client, n=3, randomize_priority=False):
    test_dir = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "data", "example_pod.yaml")

    with open(file_path, "r") as f:
        manifest = yaml.safe_load(f)

    manifest["spec"]["schedulerName"] = scheduler_name
    pods_created = []

    for i in range(n):
        pod_name = f"test-pod-{i}"
        priority = random.randint(1, 100)
        

        pods_created.append((pod_name, priority))
        manifest["metadata"]["name"] = pod_name
        if randomize_priority:
            manifest["metadata"]["annotations"]["priority"] = str(priority)
        utils.create_from_dict(api_client, manifest)

    return list(sorted(pods_created, key=lambda x: x[1], reverse=True))


def delete_all_pods(pods, v1):
    for pod, _ in pods:
        v1.delete_namespaced_pod(name=pod, namespace=default_namespace)


def wait_for_pod_ready(name, v1, namespace=default_namespace, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        pod = v1.read_namespaced_pod(name=name, namespace=namespace)
        if pod.status.phase == "Running":
            return True
        time.sleep(2)
    return False

def test_pod_was_scheduled_with_priority():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    api_client = client.ApiClient()

    namespace = default_namespace

    pods = populate_pods(api_client, randomize_priority=True)
    
    schedule_pods()

    assert wait_for_pod_ready(pods[0][0], v1, namespace=namespace) # Check the first highest priority pod

    delete_all_pods(pods, v1)



