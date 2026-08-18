# AI Media Factory

# AI Models Configuration

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory supports multiple AI models.


Models can run:


- locally through Ollama
- through cloud APIs
- through specialized generation systems



Model selection depends on task requirements.



---

# 2. Model Selection Rules


Before using a model, AI must consider:


1. Task type

2. Required quality

3. Hardware limitations

4. Cost

5. Latency



Priority order:


1. Local models

2. Cloud models when quality is insufficient

3. Specialized models for specific tasks



---

# 3. Local AI Infrastructure


Primary local runtime:


Ollama



Current endpoint:


http://localhost:11434



Local models are preferred for:


- development
- testing
- private data processing



---

# 4. Research Model


Model:


qwen2.5-coder:3b



Runtime:


Ollama



Purpose:


- research analysis
- text processing
- topic evaluation
- structured extraction



Input:


Research articles



Output:


ResearchTopic analysis



Parameters:


temperature: 0.7


top_p: 0.9


max_tokens: 2048



---

# 5. Development Assistant Model


Model:


qwen2.5-coder:7b



Runtime:


Ollama



Purpose:


- code generation
- architecture assistance
- debugging
- documentation creation



Usage:


Development only.



---

# 6. General Language Model


Model:


llama3.1:8b



Runtime:


Ollama



Purpose:


- general reasoning
- planning
- text analysis
- agent communication



---

# 7. Cloud Writing Model


Provider:


DashScope



Model:


qwen-coder-plus



Purpose:


High quality content generation.



Used for:


- Telegram posts
- long-form content
- style adaptation



API key:


Stored only in environment variables.



Never commit keys to Git.



---

# 8. Image Generation Model


Model:


Stable Diffusion



Runtime:


Local



Purpose:


Generate:


- Telegram images
- illustrations
- channel branding assets



Input:


Image prompt



Output:


MediaAsset



---

# 9. Model Parameters


Default parameters:


temperature:


0.7



top_p:


0.9



max_tokens:


2048



repeat_penalty:


1.1



Specific engines may override defaults.



---

# 10. Prompt Rules


Every model call must have:


- system prompt
- task prompt
- structured input
- expected output format



Prompts must be stored separately:



docs/ai/PROMPTS.md



---

# 11. Model Failure Handling


If model fails:


1. Log error

2. Retry if possible

3. Use fallback model

4. Save failure information



---

# 12. Hardware Limitations


Current development machine:


Laptop GPU:

NVIDIA RTX 3050 Ti


VRAM:


4GB



Implications:


Large models may require:


- reduced context
- CPU inference
- quantized versions



---

# 13. Future Models


Possible additions:


- LLM Evaluator
- Fact Checker
- Embedding Model
- Vision Model
- Speech Model



---

# 14. Security Rules


API keys:


- stored in .env
- never committed
- never written in documentation



Model configuration:


must be managed through environment settings.



---

# End of AI Models Configuration

