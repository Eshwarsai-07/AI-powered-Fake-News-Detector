# 🚀 Quickstart Guide (Non-Technical)

Welcome! This guide will help you launch your **AI Fake News Detector** from scratch. Even if you aren't a developer, you can follow these steps to get the system running on your own AWS cloud account.

---

## 📋 Phase 1: Accounts You Need
Before we start, make sure you have these three accounts ready:
1. **AWS Account**: This is where your app will live (the cloud).
2. **GitHub Account**: This stores your code and manages the "brains" of the setup.
3. **Docker Hub**: A storage place for your app "images" (like blueprints).

---

## 🛠️ Phase 2: Manual Prep (Do this first)
You need to set up a few things in your **AWS Console**:
1. **Generate Access Keys**: Go to IAM in AWS and create "Access Keys". Save these safely; you'll need them for Phase 3.
2. **Train the AI Model (Google Colab)**: 
   - Use our provided notebook or your own flow in **Google Colab** to train the model.
   - Download the resulting model files to your computer and place them in `model_training/saved_model/fake-news-bert/`.
   - *Note: We include a `train.py` script as a reference, but you don't need to run it if you used Colab.*

---

## 🚀 Phase 3: Launching the System
You will run four main steps to build your system:

### 1. Build the "House" (Infrastructure)
Go to the `infra/terraform` folder and run:
`terraform init` then `terraform apply`
*This tells AWS to create the servers, networks, **and your S3 Model Storage** automatically.* 
**Note down the `model_bucket_name` from the output!**

### 2. Upload the Model (One-Time)
Now that your S3 bucket exists, upload your trained model:
`python model_training/upload_s3.py --model-dir model_training/saved_model/fake-news-bert/ --bucket [YOUR_BUCKET_NAME] --version bert-v1`

### 3. Install the "Tools" (Bootstrap)
Go to the `infra/ansible` folder and run:
`ansible-playbook -i inventory.ini playbook.yml`
*This installs Docker and Kubernetes on your new server.*

### 4. Start the "Brain" (GitOps)
Finally, tell the system to start managing itself:
`kubectl apply -f k8s/argocd/applications.yaml`
*This connects your code to the server so it can deploy automatically.*

---

## 📈 Phase 4: Seeing it in Action
Once launched, you can access your system through these links:
- **The Website**: Enter the address of your server (found in your AWS console) into your browser.
- **The Monitoring Dashboard**: Access the "Grafana" link to see live charts of how the AI is performing.
- **The AI Model**: The backend will automatically pull the newest AI model from your S3 bucket every time it starts up.

---

## 🆘 Troubleshooting for Beginners
- **"Access Denied"**: Check if your AWS Keys are correct.
- **"Model not found"**: Ensure your S3 bucket name matches exactly what you wrote in the configuration files.
- **"Site not loading"**: Wait 5 minutes. Sometimes the "Cloud" takes a moment to warm up!

**Congratulations! You've just deployed a production-grade AI system.** 🛡️
