# Custom Kubernetes Scheduler (Python)

A custom scheduler written in Python that extends Kubernetes scheduling capabilities

---

## Requirements

- Python 3.9+
- [Poetry](https://python-poetry.org/)
- Access to a Kubernetes cluster (e.g. Minikube or KIND)

---

## Getting Started

### 1. Clone the repository
### 2. Make sure to configure your kubeconfig on ~/.kube/config
### 3. In `src/pod_scheduler/config.py` adjust parameters according to your liking.
### 4. Run the script

```bash
poetry install
poetry run scheduler
```


## Tests
```bash
poetry run pytest
```

## Wishlist
- Dockerfile
- Implement ENV files, rather than config.py (though you can have both)
- PyTest fixtures & finalizers
- Implement logging, metrics (Perhaps in prometheus)
- Github Actions/Pipelines - Automated test deployments
- Dealing with node affinities, taints, better eviction strategies, backoffs, and retries
- RBAC for the application
- Add more tests
    - Basic pod scheduling
    - Job/Gang scheduling
    - Pre emption tests
    - Node assignment (Making sure that the nodes are actually assigned uniquely)
    - Annotation testing