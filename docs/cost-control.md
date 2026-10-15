# LLM Usage Tracking & Cost Control

This document details the cost-control guardrails implemented to prevent financial abuse of the Groq API key while maintaining high-quality multi-agent travel planning.

---

## 1. Multi-Layer Cost Protection Architecture

```text
[Incoming User Request]
         │
         ▼
1. Authentication Check (Must be authenticated user)
         │
         ▼
2. Rate Limiting Check (Max 5 auth/min, 20 req/min)
         │
         ▼
3. User Daily Limit Check (Max 10 travel plans/day per account)
         │
         ▼
4. Application Budget Check (Total daily USD cost < $2.00)
         │
         ▼
5. Concurrency Semaphore (Max 3 concurrent active LangGraph workflows)
         │
         ▼
6. Deterministic Optimization (Budget arithmetic, maps, & ranking use pure Python)
         │
         ▼
7. Output Token Capping (Brief: 500, Standard: 1200, Detailed: 2500)
         │
         ▼
[Execution & Usage Accounting] -> Persisted to llm_usage_records
```

---

## 2. Groq Pricing & Token Economics

- Groq provides ultra-fast inference with transparent pricing (typically $0.10 to $0.59 per million tokens depending on model).
- A complete travel plan executes through 14 agents. Because of context builders, each agent receives only minimal state slice:
  - Average prompt tokens per plan: ~1,800 tokens
  - Average completion tokens per plan: ~2,200 tokens
  - Total tokens per plan: ~4,000 tokens
  - Estimated cost per plan: **~$0.002 USD (0.2 cents)**

---

## 3. Configurable Limits

```env
# Maximum plans an individual account can generate per day
TRAVEL_PLANS_PER_USER_PER_DAY=10

# Maximum concurrent plans across all users
MAX_CONCURRENT_PLANS_TOTAL=3

# Hard budget caps enforced by backend before invoking LLM
DAILY_LLM_BUDGET_USD=2.00
MONTHLY_LLM_BUDGET_USD=20.00

# Output token caps per mode
OUTPUT_TOKENS_BRIEF=500
OUTPUT_TOKENS_STANDARD=1200
OUTPUT_TOKENS_DETAILED=2500
```

> [!NOTE]
> Application-side budget checks prevent new workflows from starting once the calculated spending ceiling is reached. For complete hardware-level caps, configure credit limits directly in your [Groq Billing Console](https://console.groq.com/settings/billing).
