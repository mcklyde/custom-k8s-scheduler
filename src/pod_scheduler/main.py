import time
import random
import json


from collections import Counter
from .config import scheduler_name, default_namespace

from kubernetes import client, config, watch

config.load_kube_config()
v1 = client.CoreV1Api()


def nodes_available():
    ready_nodes = []
    for n in v1.list_node().items:
        for status in n.status.conditions:
            if status.status == "True" and status.type == "Ready":
                ready_nodes.append(n.metadata.name)

    return ready_nodes


def list_all_pods():
    pods = []
    jobs = []
    for pod in v1.list_pod_for_all_namespaces().items:
        if pod.spec.scheduler_name == scheduler_name:

            name = pod.metadata.name
            node_name = pod.spec.node_name
            priority = pod.metadata.annotations.get(
                "priority", 0) if pod.metadata.annotations else 100
            job_name = pod.metadata.labels.get(
                "batch.kubernetes.io/job-name", None) if pod.metadata.labels else None

            pods.append((name, node_name, int(priority), job_name))
    return pods


def schedule(name, node, namespace=default_namespace):
    metadata = (client.V1ObjectMeta(name=name))
    target = client.V1ObjectReference(kind="Node", api_version="v1", name=node)

    binding = client.V1Binding(metadata=metadata, target=target)

    # https://github.com/kubernetes-client/python/issues/547
    # _preload_content set to False due to an unfixed bug in python
    v1.create_namespaced_binding(
        namespace=namespace, body=binding, _preload_content=False)

    return


def main():
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, default_namespace):
        if event['object'].status.phase == "Pending" and event['object'].spec.scheduler_name == scheduler_name:
            print("Found something that meets the condition")
            try:
                schedule_pods()
            except client.rest.ApiException as e:
                print(json.loads(e.body)['message'])


def podsToSchedule(pod):
    (_, node, _, _) = pod
    if node == None:
        return True

    return False


def available_unique_nodes(nodes, pods):
    nodes = set(nodes)
    nodes_taken = []
    for pod in pods:
        if pod[1]:
            nodes_taken.append(pod[1])

    return list(nodes.difference(set(nodes_taken)))


def evict_pods(pressure_ratio, availableNodes):
    pods = list_all_pods()
    pods = filter(lambda x: x[1], pods)
    pods = sorted(pods, key=lambda x: x[2])  # Sort it by least priority

    pending_pods = list(filter(podsToSchedule, list_all_pods()))
    
    # Since available nodes are in scarcity we must evict pods
    # pressure ratio is here so we can set the sensitivity of how pods get evicted.
    if len(pending_pods)/(len(availableNodes)+1) > pressure_ratio:
        print(pods[0][0], "will be evicted")
        eviction = client.V1Eviction(
            metadata=client.V1ObjectMeta(
                name=pods[0][0],
                namespace=default_namespace
            ),
            delete_options=client.V1DeleteOptions()
        )
        try:
            v1.create_namespaced_pod_eviction(
                name=pods[0][0],
                namespace=default_namespace,
                body=eviction
            )
        except client.exceptions.ApiException as e:
            print(f"Eviction failed for {pods[0][0]}: {e}")


def schedule_pods():
    pods = list_all_pods()
    availableNodes = available_unique_nodes(nodes_available(), pods)

    pods = filter(podsToSchedule, pods)
    pods = sorted(pods, key=lambda x: x[2], reverse=True)

    for pod in filter(podsToSchedule, pods):
        if pod[3]:  # Has a job
            job = pod[3]
            job_pods = list(filter(lambda x: x[3] == job, pods))

            if len(availableNodes) >= len(job_pods):
                for pod in job_pods:
                    pods.remove(pod)
                    node = node.pop()
                    schedule(pod[0], node, namespace="default")
            else:
                print(
                    f"${job} cannot be fullfilled there are only {len(availableNodes)} nodes, job requires {len(job_pods)}")
        else:
            if len(availableNodes) > 0:
                node = availableNodes.pop()
            else:
                print("We've ran out of nodes")
                break

            schedule(pod[0], node, namespace="default")

    evict_pods(5, availableNodes)


if __name__ == '__main__':
    main()
