# Product Requirement Document (PRD)
## AI Fake News Detector

| Field | Value |
|-------|-------|
| **Project Name** | AI Fake News Detector |
| **Status** | In-Development |
| **Target Audience** | General public, journalists, and researchers |

---

## 1. Project Overview

**Core Value Proposition:** Leverage state-of-the-art NLP (Transformers) to provide real-time credibility scoring for news text, reducing the spread of misinformation.

---

## 2. User Personas

| Persona | Description |
|---------|-------------|
| **The Casual Reader** | Wants a quick "True/False" or "Confidence Score" for a viral headline |
| **The Researcher** | Needs deeper analysis and historical logs of checked articles |
| **The Developer** | Wants to interact with the detection engine via a clean API |

---

## 3. Functional Requirements

### 3.1 Core Features

| Feature ID | Feature Name | Description |
|------------|--------------|-------------|
| FR-01 | Text Analysis | Users can paste text into a text area to get a "Fake" vs "Real" prediction |
| FR-02 | Confidence Scoring | System returns a percentage (e.g., 89% probability of being False) |
| FR-03 | History Logs | Log past searches in MongoDB Atlas for user retrieval |
| FR-04 | Feedback Loop | Users can "Upvote/Downvote" the AI's accuracy to improve future datasets |
| FR-05 | Explanation (SHAP/LIME) | *(Optional)* Highlight words that contributed most to the "Fake" classification |

### 3.2 Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Performance** | API response time for text analysis < 2 seconds |
| **Scalability** | FastAPI must handle asynchronous requests to prevent blocking during model inference |
| **Security** | Sanitize all input text to prevent NoSQL injection in MongoDB |

---

## 4. Technical Stack

| Layer | Technology |
|-------|------------|
| **AI Model** | BERT (Hugging Face, PyTorch) |
| **Training** | Google Colab (GPU) |
| **Backend** | FastAPI (Python 3.10) |
| **Database** | MongoDB Atlas |
| **Frontend** | React 18 + Tailwind CSS |
| **API Client** | Axios |
| **Container** | Docker |
| **Deployment** | Render / AWS |
| **CI/CD** | GitHub Actions |

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React 17)                        │
│              Captures user input → Sends JSON to API            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│  1. Receives text                                               │
│  2. Pre-processes text (Tokenization)                           │
│  3. Runs inference using loaded .pt model                       │
│  4. Saves result in MongoDB Atlas                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATABASE (MongoDB Atlas)                      │
│  Schema: {text_id, content, prediction, confidence, timestamp}  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. UI Requirements

| Component | Description |
|-----------|-------------|
| **Landing Page** | Clean, minimalist search bar style interface |
| **Dashboard** | Results card with "Truth Meter" (Red = Fake, Green = Real) |
| **History Sidebar** | List of recent checks with timestamps |

---

## 7. Roadmap & Milestones

### Phase 1: Data & Model (Weeks 1-2)
- [ ] Clean Kaggle/LIAR datasets
- [ ] Fine-tune BERT model using PyTorch
- [ ] Export model weights

### Phase 2: Backend Development (Week 3)
- [ ] Setup FastAPI environment
- [ ] Integrate Hugging Face transformers pipeline
- [ ] Connect MongoDB Atlas via Motor (async driver)

### Phase 3: Frontend Development (Week 4)
- [ ] Build React 17 UI components
- [ ] Implement Axios for API calls
- [ ] Handle loading states and error boundaries

### Phase 4: Deployment & Testing (Week 5)
- [ ] Containerize with Docker
- [ ] Deploy to cloud
- [ ] Perform bias testing

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| **Model Accuracy** | > 90% on test dataset |
| **User Retention** | Users returning to check multiple sources |
| **Inference Speed** | Time from "Click Analyze" to "Result Displayed" |

---

## 9. Appendix: Technical Considerations

> [!IMPORTANT]
> Review the implementation roadmap for detailed guidance on:
> - Serving BERT without blocking FastAPI's event loop
> - MongoDB schema optimization for high-speed retrieval
> - React 17 state management patterns
