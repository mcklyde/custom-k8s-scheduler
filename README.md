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
### 2.
Make sure to configure your kubeconfig on ~/.kube/config
### 3. Run the script

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
- Github Actions/Pipelines - Automated test deployments
- Add more tests
    - Basic pod scheduling
    - Job/Gang scheduling
    - Pre emption tests
    - Node assignment (Making sure that the nodes are actually assigned uniquely)
    - Annotation testing
-