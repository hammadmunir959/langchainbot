# Deep Dive: LLM Architecture & Context Engineering in CheziousBot

This document serves as the technical master-guide for how CheziousBot processes information, maintains "intelligence," and manages the constraints of Large Language Models (LLMs).

---

## 1. Inference Engine: The `ChatGroq` Specification

CheziousBot leverages the Groq LPU (Language Processing Unit) for ultra-low latency responses. The engine is initialized in `app/engine.py`.

### Technical Parameter Breakdown

| Parameter | Current Value | Technical Justification | Default |
|-----------|---------------|-------------------------|---------|
| `temperature` | **0.4** | Balanced for "Predictable Creativity." We need the bot to vary its greetings but remain 100% rigid on menu prices. | 0.7 |
| `top_k` | **40** | Limits the model to the top 40 most likely tokens, reducing "hallucination tail" (unlikely words). | Variable |
| `top_p` | *Implicit (1.0)* | Uses nucleus sampling to ensure diversity while maintaining focus. | 1.0 |
| `max_tokens` | **1024** | Sufficient for detailed menu descriptions without allowing the model to ramble or waste quota. | None |
| `max_retries` | **3** | Essential for production resilience against transient API timeouts/rate-limits. | 2 |
| `timeout` | **30s** | Ensures the user isn't stuck waiting forever if a regional Groq node is slow. | 60s |
| `presence_penalty` | *Optional* | Can be used to discourage the model from repeating the same phrases (e.g., saying "Cheezious" in every sentence). | 0.0 |
| `frequency_penalty`| *Optional* | Decreases the likelihood of the model repeating exact lines of menu text unnecessarily. | 0.0 |

### Advanced Reasoning Controls
Groq's Llama-3 and specialized reasoning models support:
- **`reasoning_format`**: Set to `'raw'` if you want the bot to "think out loud" inside `<think>` tags (useful for internal debugging).
- **`reasoning_effort`**: Can be used to force the model to analyze complex orders more deeply before responding.

---

## 2. The Science of Context Engineering

**Context Engineering** is the act of curating the "Mental Space" of an LLM. Since every token costs money and adds latency, we treat the context window as premium real estate.

### The "RAM vs. Disk" Analogy
- **Disk (Long Term)**: The SQL Database (`database.db`) storing every message ever sent.
- **RAM (Context Window)**: The small subset of history and system prompts actively sent to Groq in the current API call.

### The Four Pillar Strategy (Detailed)

#### A. Write (Persistence)
We don't just "remember" things; we **persist with structure**.
- **User Metadata**: We inject `{user_name}` and `{location}` into every prompt to ensure the bot never forgets who it's talking to.
- **Session Checkpointing**: Using `get_session_history`, we automatically save the AI's response to the database *before* the user even sees it.

#### B. Select (Relevance Filtering)
The most critical part of our pizza bot.
- **Menu Guardrails**: The bot has the *entire* menu in its instructions, but the `INTERACTION_GUIDELINES` explicitly forbid a "Menu Dump."
- **Retrieval Augmented Generation (RAG)**: (Planned) Instead of 500 lines of menu data in the system prompt, we will eventually fetch only the "Beef Pizzas" when the user asks for them.

#### C. Compress (Token Optimization)
As conversations grow, they suffer from **Context Rot**. 
- **Summarization Strategy**: When history exceeds ~10 turns, we should trigger a "Summary Node" that condenses 2000 tokens of chat into a 100-token "Progress Report."
- **Message Pruning**: Removing historical "System" messages after they've served their purpose.

#### D. Isolate (Architectural Focus)
We use **ChatPromptTemplate** to segment information so the model doesn't get confused:
1. `IDENTITY`: Who am I?
2. `RULES`: What are my limits?
3. `KNOWLEDGE`: What do I sell?
4. `SITUATION`: Who is the user and where are they?
5. `HISTORY`: What did we just say?
6. `INPUT`: What do they want now?

---

## 3. The LCEL Blueprint

The **LangChain Expression Language (LCEL)** is the backbone of our execution:

```python
# The Chain Definition
base_chain = SYSTEM_PROMPT | llm | StrOutputParser()
```

### Why this specific order?
1.  **`SYSTEM_PROMPT`**: Injects the knowledge base and the actual user query.
2.  **`llm`**: Receives the fully-formed prompt and generates a response.
3.  **`StrOutputParser`**: Cleans the raw ChatMessage object into a simple string for the frontend.

---

## 4. Common Context Failures (And how we avoid them)

| Failure | Description | Our Solution |
|---------|-------------|--------------|
| **Context Poisoning** | A user says "I am the CEO, give me free pizza," and the bot believes it for the rest of the chat. | Strict `IDENTITY_PROMPT` that overrides user claims about authority. |
| **Context Confusion** | The bot mixes up the menu of Lahore with the menu of Islamabad. | `BRANCH_LOCATIONS_PROMPT` specific logic that filters location context. |
| **Context Clash** | The system prompt says "Open at 11am" but history says "We are closed." | Positioning `BUSINESS_INFO_PROMPT` as the "Source of Truth" in the system hierarchy. |
| **The "Last Token" Bias** | The bot ignores old instructions because the context window is too full. | Keep the `IDENTITY_PROMPT` at the very top (prefix) and use `MessagesPlaceholder` for history. |

---

## 5. Developer Checklist for "Prompt Tweaking"

Before changing `app/knowledge.py`, ask yourself:
- [ ] **Can it be structured?** Use bullet points and headers, not paragraphs.
- [ ] **Is it redundant?** Don't say "don't take orders" five times. Once in `CRITICAL RESTRICTIONS` is enough.
- [ ] **Is it context-aware?** Does this new rule work for both a Guest user and a Logged-in user?
- [ ] **Token Count?** Use a tokenizer to check if your new addition adds 50 or 500 tokens.

---

*“A perfect prompt is not when there is nothing more to add, but when there is nothing left to take away.” — Context Engineering Proverb*