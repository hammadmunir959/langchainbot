# Context Engineering & LangChain Groq Reference

This document serves as a comprehensive guide to **Context Engineering** and a detailed reference for the **ChatGroq** implementation in LangChain. 

---

##  ChatGroq Parameter Reference

The `ChatGroq` class provides an interface to Groq's high-speed LLMs. Below are the key parameters used to configure the client and model behavior.

### 1. Completion Parameters
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `model` | `str` | *Required* | The model ID to use (e.g., `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`). |
| `temperature` | `float` | `1.0` | Controls randomness. `0.0` is deterministic; `1.0` is creative. |
| `max_tokens` | `int` | `None` | The maximum number of tokens to generate in the completion. |
| `top_p` | `float` | `1.0` | Nucleus sampling; considers tokens with top_p probability mass. |
| `stop` | `List[str]` | `None` | List of sequences where the API will stop generating further tokens. |
| `streaming` | `bool` | `False` | Whether to stream the response back in chunks. |
| `reasoning_format` | `str` | `'raw'` | Format for reasoning output. Options: `'raw'` (XML tags), `'parsed'`, `'hidden'`. |
| `reasoning_effort` | `str` | `None` | Controls the model's effort on reasoning (for models supporting it). |

### 2. Client & Connectivity Parameters
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `api_key` | `SecretStr` | `Env Var` | Your Groq API key (defaults to `GROQ_API_KEY`). |
| `max_retries` | `int` | `2` | Maximum number of retries for failed requests. |
| `timeout` | `float` | `None` | Timeout in seconds for the API request. |
| `base_url` | `str` | `None` | Custom base URL for API requests (useful for proxies). |
| `model_kwargs` | `dict` | `{}` | Additional parameters to pass directly to the Groq API. |

---

##  What is Context Engineering?

> **"[Context engineering is the] delicate art and science of filling the context window with just the right information for the next step."**  
> — *Andrej Karpathy*

While **Prompt Engineering** focuses on tactical wording (how you ask), **Context Engineering** is a strategic discipline focused on the entire information ecosystem (what the model knows). 

### The OS Analogy
- **LLM**: The CPU (Reasoning engine).
- **Context Window**: The RAM (Working memory).
- **Context Engineering**: The Operating System (Managing what data is loaded into RAM at the right time).

### Core Components
1. **System Instructions**: Defining the persona, guardrails, and behavioral logic.
2. **Retrieved Knowledge (RAG)**: Injecting external, up-to-date data from vector DBs or APIs.
3. **Memory Management**: Balancing short-term chat threads and long-term user profiles.
4. **Tool Definitions**: Defining the capabilities (APIs/functions) the agent can invoke.
5. **Structured Formatting**: Enforcing output standards (e.g., JSON schemas) for reliability.

---

##  The Four Pillars of Context Engineering

To prevent "Context Rot" and ensure efficient token usage, modern agents use four primary strategies:

### 1. Write (Persist Information)
Save context *outside* the window to keep it available but not crowded.
- **Scratchpads**: Temporary "notepads" where agents store intermediate reasoning or plans.
- **Persistent Memory**: Storing user preferences or project summaries in a database for multi-session recall.

### 2. Select (Curate Relevant Information)
Pull in only what is necessary for the current turn.
- **Dynamic Retrieval**: Using RAG to fetch specific snippets rather than dumping entire documents.
- **Just-in-Time Context**: Fetching tools or data descriptors only when the agent specifically requests them.

### 3. Compress (Optimize Token Usage)
Reduce the size of the context without losing meaning.
- **Hierarchical Summarization**: Periodically summarizing old message history to free up tokens.
- **Token Pruning**: Removing redundant tool outputs or "garbage" data once processed.

### 4. Isolate (Structure for Focus)
Separate different types of context to prevent confusion.
- **Multi-Agent Architectures**: Breaking a complex task into sub-agents (e.g., a "Researcher" and a "Writer"), each with its own focused context.
- **Context Segmenting**: Using XML tags (e.g., `<rules>`, `<history>`, `<data>`) to help the model distinguish between different pieces of information.

---

## Common Context Challenges

As context grows, performance can degrade due to several factors:

*   **Context Poisoning**: When a hallucination enters the history and sabotages future reasoning.
*   **Context Distraction**: Irrelevant data overwhelming the model’s focus on instructions.
*   **Context Confusion**: Overlapping information (e.g., two contradicting tools) making the model hesitant.
*   **Context Clash**: When different parts of the provided context disagree with each other.

---

## Implementation with LangGraph

LangGraph is specifically designed to support advanced context engineering through:

1.  **Checkpointing**: Automated short-term memory that persists state across agent steps.
2.  **State Management**: Defining custom schemas to isolate internal "thought" fields from the public message list.
3.  **Long-Term Memory**: Built-in abstractions (`LangMem`) to save and retrieve user-specific context across sessions.
4.  **Nodes & Edges**: Providing "surgical" control over exactly what information is passed to the LLM at each node in the graph.

---

## � Context Engineering Checklist for a 3B LLM

### 1. **Define Identity & Role**

* [ ] Decide the AI’s persona (expert, assistant, tutor, etc.)
* [ ] Write a **concise role statement** (1–2 sentences)
* [ ] Ensure tone aligns with task (formal, casual, concise, friendly)
* [ ] Limit details to high-signal info (avoid unnecessary backstory)

---

### 2. **Clarify Task / Objective**

* [ ] Specify **exact task(s)** the model should perform
* [ ] Include **expected output format** (list, paragraph, code, table)
* [ ] Ensure instructions are **direct and unambiguous**
* [ ] Prioritize critical tasks first; optional tasks later

---

### 3. **Set Rules & Constraints**

* [ ] Ethical or safety constraints (avoid sensitive or unsafe outputs)
* [ ] Style constraints (concise, detailed, step-by-step, numbered)
* [ ] Resource limits (e.g., token limits, no external data lookup)
* [ ] Include **“what not to do”** rules for clarity

---

### 4. **Decide What Memory / History to Include**

* [ ] Include only **recent, relevant interactions** (2–3 messages)
* [ ] Summarize prior info instead of copying full text if long
* [ ] Avoid overloading model; 3B models have limited context window
* [ ] Keep memory structured (bullet points or labeled lines)

---

### 5. **Include Critical Knowledge Snippets**

* [ ] Embed **tiny relevant definitions or formulas** if needed
* [ ] Include **short tables or examples** (1–2 concise examples)
* [ ] Avoid long external text; use only what is **essential for task**
* [ ] Verify knowledge is **accurate and up-to-date**

---

### 6. **Organize Context Structure**

* [ ] Follow a consistent template:

```
[Identity]
[Task]
[Rules/Constraints]
[Memory/History]
[Knowledge Snippets / Examples]
[User Input]
```

* [ ] Keep **most critical info at the top**
* [ ] Optional info goes at the bottom

---

### 7. **Optimize for Token Efficiency**

* [ ] Remove unnecessary words, adjectives, or examples
* [ ] Use abbreviations only if model understands them
* [ ] Test context length vs model performance
* [ ] Keep total tokens below **2K–4K** (for most 3B models)

---

### 8. **Test & Iterate**

* [ ] Run small test prompts first
* [ ] Observe model output for correctness, relevance, hallucination
* [ ] Trim or restructure context based on errors
* [ ] Incrementally add info to see impact on performance

---

### 9. **Prepare Reusable Snippets**

* [ ] Save identity/role snippets for reuse
* [ ] Save rules/templates for repeated tasks
* [ ] Create modular context blocks (can be combined as needed)
* [ ] Maintain versioning for updates

---

### 10. **Optional Enhancements**

* [ ] Include “step-by-step reasoning” instruction if task is complex
* [ ] Add **checks or verification prompts** to self-correct outputs
* [ ] Consider small embedded examples of **ideal outputs**
* [ ] Use “user intent clarifications” to reduce ambiguity

---
## 🔗 Resources & Further Reading

- [LangChain Blog: Context Engineering for Agents](https://blog.langchain.com/context-engineering-for-agents/)
- [Redis: Context Engineering Best Practices](https://redis.io/blog/context-engineering-best-practices-for-an-emerging-discipline/)
- [Phil Schmid: Practical Context Engineering](https://www.philschmid.de/context-engineering)
- [Groq Documentation](https://console.groq.com/docs/models)