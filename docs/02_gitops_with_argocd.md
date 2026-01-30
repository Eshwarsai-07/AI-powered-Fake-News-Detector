# GitOps with ArgoCD

## Overview
We utilize a pure GitOps deployment model. The state of the Kubernetes cluster is declarative and strictly mirrored from the Git repository. ArgoCD acts as the reconciliation agent, ensuring the live cluster always matches the desired state defined in code.

![ArgoCD Workflow](../images/ArgoCD.png)

## Reconciliation Architecture

### The App-of-Apps Pattern
*   **Parent Application**: A root application creates the namespace and manages child applications.
*   **Child Applications**: Independent configurations for `backend`, `frontend`, `ingress`, and `monitoring`.

### Sync Policy
*   **Automated Sync**: Changes in the `k8s/` directory trigger an immediate cluster update.
*   **Self-Healing**: Manual changes to the cluster (drift) are automatically detected and reverted by ArgoCD to match the Git source.

## Deployment Strategy
1.  **CI Completion**: GitHub Actions pushes a new image tag to GHCR.
2.  **Manifest Update**: (Future State) An image updater service or manual PR updates the deployment manifest with the new tag.
3.  **ArgoCD Detects Change**: The controller notices the divergence in `deployment.yaml`.
4.  **Rolling Update**: ArgoCD accepts the change and performs a zero-downtime rolling update of the pods.
