# ML Backend Inference

## Overview
The core value of the application is the Fine-Tuned BERT model. The backend is engineered to serve this heavy model efficiently within a containerized environment.

![Inference Result](../images/app2.png)
*(Prediction Output)*

## Model Architecture

### BERT (Bidirectional Encoder Representations from Transformers)
*   **Variant**: `bert-base-uncased` fine-tuned on valid/fake news datasets.
*   **Input**: Tokenized text sequences (max length 512 tokens).
*   **Output**: Binary classification (0: Real, 1: Fake) with Softmax probability.

## Serving Strategy using FastAPI

1.  **Model Loading**:
    *   **Cold Start**: The model is loaded into memory during the container startup phase.
    *   **Optimization**: We use `torch.no_grad()` to reduce memory footprint during inference, as no backpropagation is required.

2.  **Concurrency**:
    *   FastAPI handles asynchronous requests.
    *   Model inference is CPU-bound and runs in a thread pool to avoid blocking the main event loop.

3.  **Resource Management**:
    *   **Requests**: Guaranteed minimal CPU/Memory allocation to prevent OOM kills.
    *   **Limits**: Capped resources to ensure fair scheduling alongside other cluster services.
