# System Architecture Diagrams

## 1. Complete End-to-End Architecture

```mermaid
graph TB
    A["Raw Transactions"] -->|Data Generation| B["10k Synthetic Data"]
    B -->|EDA Analysis| C["Feature Engineering"]
    C -->|8 Features Engineered| D["Training Dataset"]
    
    D -->|Train/Test Split| E["Random Forest Model"]
    E -->|98.5% Accuracy| F["Baseline Model<br/>baseline_model.joblib"]
    
    subgraph "Real-Time Scoring"
        F -->|Load Model| G["Flask REST API<br/>Port 5000"]
        G -->|POST /predict| H["Single Transaction<br/>Scoring"]
        G -->|POST /batch_predict| I["Batch Prediction<br/>10k txn / 30s"]
        G -->|GET /health| J["Health Check"]
        G -->|GET /stats| K["Statistics"]
    end
    
    H -->|Fraud Probability| L["Decision Engine<br/>Threshold 0.29"]
    I -->|Batch Results| L
    L -->|APPROVE/BLOCK| M["Prediction Output"]
    
    M -->|Log All Predictions| N["Audit Trail<br/>JSON Logging"]
    N -->|Data Stream| O["Monitoring Pipeline"]
    
    subgraph "Drift Detection & Monitoring"
        O -->|Extract Features| P["7 Feature Monitor"]
        P -->|PSI Calculation| Q["Population Stability<br/>Index"]
        P -->|KS Test| R["Statistical Test<br/>p-value > 0.05"]
        Q -->|PSI < 0.1| S{"Drift<br/>Detected?"}
        R -->|p-value > 0.05| S
        S -->|No: Continue| T["Feature Distributions<br/>Stable"]
        S -->|Yes: Alert| U["Drift Alert<br/>>2 Features"]
    end
    
    T -->|Performance Data| V["Metrics Dashboard"]
    U -->|Trigger Alert| W["Alert System"]
    
    subgraph "Monitoring & Alerts"
        V -->|Real-Time Metrics| X["HTML Dashboard<br/>performance_dashboard.html"]
        W -->|Check Thresholds| Y["Block Rate > 5%"]
        W -->|Check Thresholds| Z["Model Age > 30d"]
        Y -->|Alert| AA["Alert JSON Log"]
        Z -->|Alert| AA
    end
    
    AA -->|Log Alerts| AB["Alert Report<br/>alerts.json"]
    
    subgraph "Automated Retraining"
        U -->|Drift in >2 Features| AC["Retraining Trigger"]
        Z -->|Model Too Old| AC
        AC -->|Retrain Model| AD["Data Preparation"]
        AD -->|Feature Engineering| AE["Train New Model"]
        AE -->|If Better| AF["Backup Old Model<br/>model_v1_backup"]
        AF -->|Deploy| AG["Replace with<br/>New Model"]
        AG -->|Update Production| F
    end
    
    X -.->|Visualize| AH["Stakeholder Dashboard"]
    AB -.->|Notify| AI["Alert Notifications"]
    
    style B fill:#e1f5ff
    style D fill:#e1f5ff
    style F fill:#c8e6c9
    style G fill:#fff9c4
    style L fill:#fff9c4
    style M fill:#ffe0b2
    style O fill:#c8e6c9
    style V fill:#c8e6c9
    style X fill:#ffe0b2
    style AA fill:#ffccbc
    style AB fill:#ffccbc
    style AC fill:#c8e6c9
    style AH fill:#ffe0b2
    style AI fill:#ffccbc
```

---

## 2. High-Level Workflow Architecture

```mermaid
graph LR
    subgraph Input["📥 INPUT"]
        A["Transactions<br/>Real-time or Batch"]
    end
    
    subgraph Processing["⚙️ PROCESSING"]
        B["Feature<br/>Engineering<br/>8 Features"]
        C["Random Forest<br/>Model<br/>98.5% Accuracy"]
    end
    
    subgraph Prediction["🎯 PREDICTION"]
        D["Decision Engine<br/>Threshold: 0.29"]
        E["Output<br/>APPROVE/BLOCK"]
    end
    
    subgraph Monitoring["📊 MONITORING"]
        F["Drift Detection<br/>PSI + KS Test"]
        G["Performance<br/>Dashboard"]
        H["Alert System<br/>Threshold Checks"]
    end
    
    subgraph Intelligence["🧠 INTELLIGENCE"]
        I["Auto-Retraining<br/>Drift/Age Triggers"]
        J["Updated Model<br/>Re-deployed"]
    end
    
    subgraph Logging["📝 LOGGING"]
        K["Audit Trail<br/>JSON Logs"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> K
    K --> F
    K --> G
    K --> H
    F -->|Drift Alert| I
    H -->|Alert| I
    I --> J
    J --> C
    
    style A fill:#bbdefb
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#fff9c4
    style E fill:#ffe0b2
    style F fill:#f8bbd0
    style G fill:#b2dfdb
    style H fill:#f8bbd0
    style I fill:#d1c4e9
    style J fill:#c8e6c9
    style K fill:#ede7f6
```

---

## 3. Deployment & Layered Architecture

```mermaid
graph TB
    subgraph Client["🖥️ CLIENT LAYER"]
        A["Web Browser<br/>Dashboard"]
        B["Mobile App<br/>Transaction"]
        C["Batch System<br/>10k txn"]
    end
    
    subgraph API["🌐 API LAYER"]
        D["Flask REST API<br/>Port 5000"]
        E["/predict<br/>Single Txn"]
        F["/batch_predict<br/>Multiple Txn"]
        G["/health<br/>Status Check"]
        H["/stats<br/>Statistics"]
    end
    
    subgraph Model["🤖 MODEL LAYER"]
        I["Loaded Random Forest<br/>98.5% Accuracy"]
        J["Feature Preprocessor<br/>StandardScaler"]
        K["Label Encoder<br/>Categorical"]
    end
    
    subgraph Decision["⚖️ DECISION LAYER"]
        L["Threshold: 0.29<br/>Cost-Optimized"]
        M["APPROVE<br/>Low Risk"]
        N["BLOCK<br/>High Risk"]
    end
    
    subgraph Monitoring["📈 MONITORING LAYER"]
        O["Audit Trail Logger<br/>JSON Format"]
        P["Drift Detector<br/>PSI + KS Test"]
        Q["Performance Tracker<br/>Metrics DB"]
        R["Alert Generator<br/>Threshold Logic"]
    end
    
    subgraph Intelligence["♻️ LEARNING LAYER"]
        S["Drift Check<br/>Statistical Tests"]
        T["Retraining Engine<br/>Auto-Retrain"]
        U["Model Versioning<br/>Git + Backup"]
    end
    
    subgraph Storage["💾 STORAGE LAYER"]
        V["Models/<br/>baseline_model.joblib"]
        W["Reports/<br/>Metrics & Logs"]
        Z["Git History<br/>Version Control"]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
    E --> J
    E --> K
    F --> J
    F --> K
    J --> I
    K --> I
    I --> L
    L --> M
    L --> N
    M --> O
    N --> O
    O --> P
    O --> Q
    O --> R
    P --> S
    R --> S
    S --> T
    T --> U
    U --> V
    Q --> W
    R --> W
    U --> Z
    
    style D fill:#ffeb3b
    style I fill:#8bc34a
    style L fill:#ff6b6b
    style O fill:#03a9f4
    style V fill:#9c27b0
    style T fill:#ff9800
```

---

## 4. Data Flow Diagram

```
Transaction Input
    ↓
[Preprocess: Scale & Encode Features]
    ↓
[Load Model: Random Forest]
    ↓
[Predict: Fraud Probability]
    ↓
[Decision: Compare with Threshold 0.29]
    ↓
[Output: APPROVE or BLOCK]
    ↓
[Log: Audit Trail + Metrics]
    ↓
[Monitor: Check for Drift & Alerts]
    ↓
[Retrain: If Drift Detected OR Model Too Old]
    ↓
[Update: Deploy New Model]
```

---

## Component Mapping

| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| Data Generation | `scripts/generate_data.py` | Create 10k synthetic transactions | ✅ |
| Feature Engineering | `src/feature_engineering.py` | Transform raw data → 8 features | ✅ |
| Model Training | `scripts/train.py` | Train Random Forest (98.5% accuracy) | ✅ |
| Cost Analysis | `scripts/cost_analysis.py` | Find optimal threshold (0.29) | ✅ |
| Real-Time API | `scripts/scoring_api.py` | Flask API for predictions | ✅ |
| Batch Predictions | `scripts/batch_predict.py` | Score 10k transactions in 30s | ✅ |
| Drift Detection | `scripts/drift_detection.py` | Monitor 7 features for changes | ✅ |
| Performance Dashboard | `scripts/performance_dashboard.py` | HTML dashboard for monitoring | ✅ |
| Alert System | `scripts/alert_system.py` | Generate threshold-based alerts | ✅ |
| Auto-Retraining | `scripts/retrain_model.py` | Retrain on drift/age triggers | ✅ |

---

## System Characteristics

### Input Processing
- **Real-time**: Single transactions via REST API
- **Batch**: 10k transactions in ~30 seconds
- **Features**: 8 engineered numerical/categorical features

### Model Inference
- **Algorithm**: Random Forest Classifier
- **Accuracy**: 98.5% (5-fold cross-validated)
- **ROC-AUC**: 0.621
- **Decision Threshold**: 0.29 (cost-optimized)
- **Latency**: <100ms per prediction

### Monitoring
- **Drift Detection**: PSI (Threshold: 0.1) + KS-Test (p-value > 0.05)
- **Features Monitored**: 7 numerical features
- **Alert Triggers**: Block Rate > 5%, Model Age > 30 days, Drift > 2 features
- **Dashboard**: Real-time HTML with metrics

### Intelligence
- **Retraining Triggers**: Data drift (>2 features) OR Model age (>30 days)
- **Model Versioning**: Git + timestamped backups
- **Deployment**: Automatic with old model backup

---

## Deployment Stack

```
┌─────────────────────────────────┐
│   Client Applications           │
├─────────────────────────────────┤
│   Flask REST API (Port 5000)    │
├─────────────────────────────────┤
│   Random Forest Model           │
├─────────────────────────────────┤
│   Decision Engine (Threshold)   │
├─────────────────────────────────┤
│   Monitoring & Alerting         │
├─────────────────────────────────┤
│   Auto-Retraining Engine        │
├─────────────────────────────────┤
│   Local Storage (Models/Logs)   │
├─────────────────────────────────┤
│   Git Version Control           │
└─────────────────────────────────┘
```

---

## Notes

- All diagrams use Mermaid syntax (supported by GitHub)
- Diagrams are automatically rendered when viewing this file in GitHub
- For local viewing, use any Mermaid renderer or VS Code Mermaid extension
- Color coding: Blue=Data, Green=Processing, Yellow=Output, Red=Alerts, Purple=Storage

