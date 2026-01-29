# 🧠 How to Update Your ML Model

Since your model loads dynamically from S3, updating it is easy and requires **no code changes**.

## 1. The Concept
1.  **Storage:** Your model lives in AWS S3 (`fake-news-models-...`).
2.  **Startup:** When the Backend starts, it checks if the model is locally available.
3.  **Download:** If not found (which is always true on a restart), it downloads the latest files from S3.

## 2. Update Procedure

### Step 1: Upload New Model to S3 ☁️
You have your trained model files (`pytorch_model.bin`, `config.json`, `tokenizer.json`) on your **Local Computer**.
We need to put them into the AWS cloud.

**Instructions:**
1.  **Login to AWS Console:** [https://s3.console.aws.amazon.com/s3/home](https://s3.console.aws.amazon.com/s3/home)
2.  **Find your Bucket:** Click on the bucket named **`fake-news-models-20260129062333399100000001`**.
3.  **Go to Folder:** Open the `models/bert-v1/` folder.
4.  **Upload:**
    *   Click the orange **Upload** button.
    *   Drag & Drop your **Local Files** into the window.
    *   Click **Upload** at the bottom.
    *   *(It's okay to overwrite the existing files).*

### Step 2: Restart the Backend 🔄
Once the files are in S3, tell Kubernetes to restart the backend. This wipes the old model and downloads the new one.

**Run this command from your terminal:**
```bash
# SSH into your server
ssh -i "infra/terraform/ai-fake-news-detector-key.pem" ubuntu@3.110.86.85

# Restart the backend deployment
kubectl rollout restart deployment backend -n fake-news-app
```

### Step 3: Verify 🧪
Watch the logs to see the download happen:
```bash
# (Still inside SSH)
kubectl logs -l app=backend -n fake-news-app -f
```
*You should see logs saying "Downloading from S3..." then "Model loaded successfully".*

## 3. Advanced: Changing Model Version/Folder
If you want to keep the old model and upload the new one to a *new folder* (e.g., `models/bert-v2`), you need to tell the App where to look.

1.  **Edit ConfigMap:**
    ```bash
    kubectl edit configmap backend-config -n fake-news-app
    ```
2.  **Change `S3_MODEL_KEY`:**
    Update the value to your new folder name (e.g., `models/bert-v2`).
3.  **Restart Backend:**
    ```bash
    kubectl rollout restart deployment backend -n fake-news-app
    ```
