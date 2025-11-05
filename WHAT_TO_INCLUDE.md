# What to Include in Your Paper: P-Values and Confidence Intervals

## Should You Include P-Values?

### ✅ **YES, but frame them correctly:**

**Include them because:**
- Shows you did proper statistical testing
- Demonstrates transparency (acknowledging limitations)
- Reviewers expect some statistical tests

**But frame them like this:**

> "We report p-values for completeness, though they are weak due to sparse trading (only 3% of days have trades). This is expected for selective strategies that trade only when signals are strong. Economic metrics (Sharpe ratios, annualized returns) are more relevant for evaluating trading strategies."

### 📊 **What to Report:**

**Main Results Table:**
```
Sector          | Annual Return | 95% CI          | Sharpe | p-value
Technology      | 7.7%          | [0.5%, 14.9%]   | 1.11   | 0.035
Financials      | 0.6%          | [-0.1%, 1.3%]   | 0.67   | 0.108
```

**In Text:**
- Lead with Sharpe ratios and returns (these are your main findings)
- Mention p-values in a footnote or secondary paragraph
- Explain why they're weak (sparse trading)

---

## What Are Confidence Intervals?

### **Simple Explanation:**

A **95% confidence interval** says: "We're 95% confident the true return is between these two numbers."

**Example for Technology:**
- Annual Return: **7.7%**
- 95% CI: **[0.5%, 14.9%]**

This means:
- We estimate the true annual return is 7.7%
- But we're 95% confident it's somewhere between 0.5% and 14.9%
- The interval is wide because we have sparse data (only 21 trades)

### **Why Confidence Intervals Are Better Than P-Values:**

1. **More informative**: Shows both the estimate AND uncertainty
2. **Easier to interpret**: "Between 0.5% and 14.9%" is clearer than "p = 0.035"
3. **Accounts for uncertainty**: Wide intervals show you have limited data
4. **No arbitrary thresholds**: No "p < 0.05" cutoff

### **How to Read Your Confidence Intervals:**

**Technology:**
- Return: 7.7% (95% CI: 0.5% to 14.9%)
- ✅ **CI doesn't include zero** → statistically significant
- ✅ **Lower bound is positive** → even worst case is profitable

**Financials:**
- Return: 0.6% (95% CI: -0.1% to 1.3%)
- ⚠️ **CI includes zero** → not statistically significant
- ⚠️ **Lower bound is negative** → could lose money in worst case

**Consumer Discretionary:**
- Return: 0.6% (95% CI: -4.5% to 5.6%)
- ❌ **CI includes zero** → not statistically significant
- ❌ **Very wide interval** → high uncertainty

---

## Recommended Paper Structure

### **1. Main Results Section:**

**Lead with economic metrics:**
> "Technology shows the strongest performance with a Sharpe ratio of 1.11 and annualized return of 7.7% (95% CI: 0.5% to 14.9%). Financials follows with Sharpe 0.67 and return 0.6% (95% CI: -0.1% to 1.3%)."

### **2. Statistical Testing Section (Secondary):**

> "We performed one-sample t-tests to assess statistical significance. Technology shows p = 0.035 (raw), though this does not survive FDR correction for multiple comparisons. The weak p-values are expected given sparse trading (only 3% of days have trades), which is characteristic of selective strategies that trade only when signals are strong. Economic metrics (Sharpe ratios, confidence intervals) are more relevant for evaluating trading strategies."

### **3. Table Format:**

| Sector | Annual Return | 95% CI | Sharpe | p-value* |
|--------|---------------|--------|--------|----------|
| Technology | 7.7% | [0.5%, 14.9%] | 1.11 | 0.035 |
| Financials | 0.6% | [-0.1%, 1.3%] | 0.67 | 0.108 |
| Industrials | 0.5% | [-0.8%, 1.7%] | 0.70 | 0.454 |

*Note: p-values are weak due to sparse trading (only 3% of days have trades). This is expected for selective strategies.

---

## Key Takeaways

### ✅ **DO:**
- Report Sharpe ratios prominently
- Report annualized returns with confidence intervals
- Include p-values but frame them appropriately
- Explain why p-values are weak (sparse trading)

### ❌ **DON'T:**
- Lead with p-values
- Hide weak p-values
- Claim statistical significance without FDR correction
- Ignore confidence intervals

### 💡 **Remember:**
- **P-values** = "Is the signal real?" (statistical)
- **Sharpe ratios** = "Can you make money?" (economic)
- **Confidence intervals** = "How certain are we?" (uncertainty)

For trading strategies, economic significance (Sharpe, returns) is more important than statistical significance (p-values).

