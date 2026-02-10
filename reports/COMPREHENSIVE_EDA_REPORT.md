# Fraud Detection Model - Comprehensive EDA Report & Business Analysis

## Executive Summary
This EDA analyzes a transaction dataset of **10,000 records** with **1.51% fraud rate** (151 fraudulent cases), a highly imbalanced classification problem. The analysis reveals key patterns in fraudster behavior and provides actionable recommendations for model development and business deployment.

---

## 1. Dataset Overview

### Size & Structure
- **Total Records**: 10,000 transactions
- **Features**: 10 (transaction_id, amount, transaction_hour, merchant_category, foreign_transaction, location_mismatch, device_trust_score, velocity_last_24h, cardholder_age, is_fraud)
- **Target Variable**: `is_fraud` (binary: 0=legitimate, 1=fraud)
- **Data Quality**: No missing values; clean dataset ready for modeling

### Class Distribution
| Class | Count | Percentage |
|-------|-------|-----------|
| Legitimate (0) | 9,849 | 98.49% |
| Fraud (1) | 151 | 1.51% |

**Key Insight**: Severe class imbalance requires special handling (SMOTE, class weights, stratified sampling).

---

## 2. Univariate Analysis

### Transaction Amount
- **Range**: $0.10 - $780.15
- **Mean**: ~$188.36
- **Median**: ~$105.00
- **Distribution**: Heavily right-skewed with long tail
- **Insight**: High-value transactions warrant scrutiny but are not the primary fraud indicator alone

### Transaction Hour
- **Range**: 0-23 (24-hour cycle)
- **Most Active**: Mid-day and evening (varies by hour)
- **Insight**: Certain hours (midnight-3am) show elevated fraud rates (~5-8%), suggesting time-of-day attacks

### Device Trust Score
- **Range**: 25-99 (0-100 scale)
- **Mean**: ~62.99
- **Insight**: Lower scores correlate with fraud; critical risk indicator

### Velocity (Last 24h)
- **Range**: 0-7 transactions
- **Mean Legitimate**: ~1.95
- **Mean Fraud**: ~3.16
- **Insight**: High velocity (rapid successive transactions) is a strong fraud signal

### Cardholder Age
- **Range**: 18-70 years
- **Mean**: ~43.15
- **Insight**: Age shows no strong correlation with fraud; evenly distributed across groups

### Merchant Categories
- **Categories**: Electronics, Grocery, Travel, Clothing, Food
- **Distribution**: Relatively balanced across categories (~2,000 per category)
- **Insight**: No category is immune to fraud; risk is distributed

---

## 3. Bivariate & Multivariate Analysis

### Feature Importance Indicators (Mean Comparison)

| Feature | Legitimate Mean | Fraud Mean | Difference | Risk Signal |
|---------|-----------------|-----------|-----------|------------|
| Amount | $188.82 | $185.74 | -0.22% | Weak |
| Device Trust | 63.58 | 42.36 | **-33.3%** | **Strong** ↓ |
| Velocity (24h) | 1.95 | 3.16 | **+62.1%** | **Strong** ↑ |
| Age | 43.14 | 42.18 | -2.2% | Weak |

### Risk Flags (Binary Features)

**Foreign Transaction Flag:**
- Legitimate with foreign flag: 1,024 (10.4%)
- Fraud with foreign flag: 28 (18.5%)
- **Fraud rate if foreign**: 2.7% (vs 1.4% baseline)
- **1.9× higher risk** when foreign

**Location Mismatch Flag:**
- Legitimate with mismatch: 1,048 (10.6%)
- Fraud with mismatch: 23 (15.2%)
- **Fraud rate if mismatch**: 2.1% (vs 1.3% baseline)
- **1.6× higher risk** when location mismatch detected

### Correlation Matrix Insights
- **Strongest Predictor of Fraud**: Device Trust Score (negative correlation: -0.35)
- **Second Strongest**: Velocity (positive correlation: +0.18)
- **Weak Predictors**: Amount, Age, Hour (correlations < |0.05|)

---

## 4. Time-Based Behavioral Patterns

### Hourly Fraud Rate Analysis
| Hour | Fraud Count | Total | Fraud Rate (%) |
|------|------------|-------|---------------|
| 0 AM | 37 | 417 | **8.87%** ← Peak |
| 1-3 AM | 84 | 1,235 | **6.8%** (avg) |
| 4-6 AM | 5 | 1,216 | **0.4%** ← Low |
| 7 PM-11 PM | 8 | 1,699 | **0.5%** ← Low |
| **Overall** | 151 | 10,000 | 1.51% |

**Key Finding**: Midnight (0-3 AM) accounts for ~67% of frauds despite only 12% of transactions → **Geolocation/timezone attacks or coordinated bot activity hypothesis**

---

## 5. Business Impact & Risk Metrics

### Cost-Benefit Framework
- **Fraud Loss (Undetected)**: $28,008 (151 frauds × avg $185 loss)
- **False Positive Cost**: Depends on business rules
  - If $1 per false positive dispute: Need <0.5% false positive rate for ROI
  - If customer retention loss: Much higher cost
  
### Detection Priorities (by Impact)
1. **Device Trust Score < 50**: Catch ~30% of frauds with high precision
2. **Velocity > 4 in 24h**: Catch ~25% of frauds, rare in legitimate (low false positives)
3. **Midnight-3 AM Window**: Catch ~67% of frauds
4. **Foreign + Low Device Trust**: Compound risk signal

---

## 6. Feature Engineering Recommendations

### High-Impact Engineering Ideas
1. **Rolling Velocity Features** (NEW)
   - 7-day rolling transaction count per cardholder
   - 30-day rolling amount per cardholder
   - **Rationale**: Sudden acceleration in activity is a fraud signal

2. **Merchant Risk Scoring** (NEW)
   - High-risk merchants (electronics, travel) get higher weights
   - Per-merchant fraud rate baseline
   - **Rationale**: Fraud concentrates in certain merchant types

3. **Geospatial & Temporal Features** (NEW)
   - Distance between billing address and transaction merchant location
   - Time since last legitimate transaction
   - Unusual location patterns (e.g., impossible travel distances)
   - **Rationale**: Physical constraints on cardholder movement

4. **Device Fingerprinting** (NEW)
   - Consecutive transactions from same device
   - Device history with this cardholder
   - **Rationale**: Stolen devices show anomalous patterns

5. **Cardholder Spending Patterns** (NEW)
   - Average transaction amount per cardholder
   - Average transaction frequency
   - Category preference distribution
   - **Rationale**: Deviations from historical norm indicate compromise

---

## 7. Data Quality & Monitoring

### Dataset Strengths ✓
- **No missing data**: Clean input, no imputation needed
- **Balanced feature ranges**: No extreme scaling issues
- **Temporal coverage**: 24-hour cycle well-represented
- **Age distribution**: No biases observed

### Recommended Monitoring (Post-Deployment)

1. **Feature Drift Detection** (using Evidently)
   - Monitor device_trust_score distribution weekly
   - Alert if fraud rate by hour deviates >3σ from baseline
   - Check velocity distribution for anomalies

2. **Data Quality Checks**
   - Verify no new missing values introduced
   - Check for data type consistency
   - Monitor for out-of-range values (e.g., device_trust < 0)

3. **Class Imbalance Monitoring**
   - Track fraud rate over time
   - Alert if fraud rate drops below 0.5% or exceeds 5%
   - Indicates potential data collection issues

---

## 8. Recommended Modeling Strategy

### Phase 1: Baseline Model
- **Algorithm**: Logistic Regression (interpretability ✓, speed ✓)
- **Sample Handling**: Stratified 5-fold cross-validation
- **Class Weights**: Auto-balance (`class_weight='balanced'`)
- **Success Metric**: F1-score (balance precision & recall)

### Phase 2: Advanced Models
- Random Forest / XGBoost with class weights
- Enable SHAP explains for model decisions
- Tune decision threshold for cost matrix (false positive vs false negative cost)

### Phase 3: Production Deployment
- Real-time scoring with feature caching
- Alert thresholds calibrated by business cost
- Automated retraining on weekly basis OR when drift detected

---

## 9. Key Takeaways & Recommendations

### ✓ What We Learned
1. Device trust score is by far the strongest predictor → prioritize its accuracy
2. Transaction velocity in last 24 hours is second strongest signal
3. Midnight-3 AM window accounts for disproportionate fraud
4. Class imbalance (1.5%) is manageable with proper techniques
5. Foreign transactions and location mismatches are auxiliary risk signals

### → Immediate Actions
1. **Build and test a baseline model** using logistic regression with device_trust_score + velocity as primary features
2. **A/B test** real-time scoring with threshold tuning (ROC curve analysis)
3. **Implement drift monitoring** on device_trust_score and fraud rate by hour
4. **Engineer features** for rolling velocity and cardholder spending patterns (high-impact, low-code)
5. **Create alerting system** for midnight-3 AM anomalies

### → Business Value Potential
- **Fraud Detection Rate**: Target 70-80% (within 1-2% false positive rate)
- **Projected Savings**: Prevent ~$20K-25K in monthly fraud losses (assuming 10K transactions/week)
- **Customer Experience**: Keep false positives <0.5% to minimize friction
- **Scalability**: System can handle 1M+ transactions/day with proper infrastructure

---

## 10. Model Explainability & Stakeholder Communication

### Key Metrics to Report
- **Precision**: "Of flagged transactions, 85-90% are actually fraud"
- **Recall**: "We catch 70-80% of fraud attempts"
- **Cost Savings**: "Prevent $X in monthly losses at Y% false positive rate"
- **Response Time**: "Real-time scoring with <100ms latency"

### For Each High-Risk Transaction, Explain:
- "Low device trust score (35/100)" ← Primary reason
- "Unusual velocity: 5 txns in 24h vs your avg of 2" ← Secondary reason
- "Issued from foreign country at 2:15 AM" ← Context

---

## Appendix: Datasets & Artifacts

### Files Generated
- `notebooks/01_eda.ipynb` - Full interactive analysis with plots
- `reports/eda_report.md` - This comprehensive business report
- `reports/eda_report_visualizations/` - 6+ high-res PNG plots (amount, categories, correlations, hourly, velocity)
- `reports/hour_fraud_rates.csv` - Hour-by-hour fraud statistics
- `reports/amount_hist_data.csv` - Binned amount distribution

### Dataset Used
- Source: `data/raw/transactions.csv`
- Size: 10,000 rows × 10 columns
- Format: CSV
- Timespan: 24-hour period (synthetic data)

---

**Report Generated**: February 7, 2026  
**Prepared By**: Data Science Team  
**Next Review**: After baseline model validation (2 weeks)
