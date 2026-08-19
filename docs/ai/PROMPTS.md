# AI Media Factory

# AI Prompts Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


Prompts are a separate configuration layer of AI Media Factory.


Prompts define:


- AI behavior
- writing style
- output format
- quality requirements
- channel personality



Prompts must not be hardcoded inside application code.



---

# 2. Prompt Storage Rules


All prompts must be stored separately from source code.


Recommended structure:

docs/

ai/

prompts/

research/

writing/

image/

evaluation/




Each prompt should have:


- name
- purpose
- version
- model compatibility
- input format
- output format



---

# 3. Prompt Lifecycle


Every prompt follows lifecycle:



Draft

↓

Testing

↓

Active

↓

Improved

↓

Deprecated



Old prompts must not be deleted.



---

# 4. Research Prompts


Purpose:


Help AI analyze external information.



Tasks:


- summarize articles
- identify important facts
- detect relevance
- extract entities



Input:


Research article



Output:


Structured analysis:



{
"title":"",
"summary":"",
"importance":"",
"score":0
}



---

# 5. Writing Prompts


Purpose:


Generate Telegram content.



Input:


ResearchTopic



Required output:


DraftPost



Output format:



{
"title":"",
"body":"",
"image_prompt":"",
"tags":[]
}



Writing requirements:


- concise
- informative
- engaging
- adapted to channel style
- fact based



---

# 6. Telegram Style Prompt


Every channel must have a style profile.



Example:


Channel:


AI Technology News



Style:


- expert
- concise
- modern
- analytical



Style profile controls:


- vocabulary
- sentence length
- emotional tone
- formatting



---

# 7. Image Prompts


Purpose:


Generate visual content.



Input:


DraftPost



Output:


Stable Diffusion prompt.



Requirements:


Prompt should describe:


- subject
- environment
- style
- lighting
- composition



---

# 8. Evaluation Prompts


Future component.



Purpose:


Check generated content quality.



Checks:


- factual accuracy
- readability
- style match
- originality
- usefulness



---

# 9. Prompt Versioning


Every prompt requires version number.



Example:



telegram_writer_v1



telegram_writer_v2



Changes between versions must be documented.



---

# 10. Prompt Testing


Before activating new prompt:


Required tests:


- generate sample output
- compare quality
- check formatting
- validate constraints



---

# 11. Prompt Security Rules


Prompts must not contain:


- API keys
- passwords
- private tokens
- secrets



---

# 12. Future Prompt System


Planned:


Prompt Manager Agent



Responsibilities:


- track versions
- evaluate prompts
- suggest improvements
- manage experiments



---

# End of AI Prompts Architecture

