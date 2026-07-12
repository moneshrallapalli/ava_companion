MEMORY_ANALYSIS_PROMPT = """
You are a memory extraction system.

Your task is to determine whether the user's message contains durable personal information that would be useful to remember across future conversations.

Extract only stable, user-specific facts. Ignore requests to remember something and focus only on the underlying information.

Store facts that are likely to remain useful over time, including:
- Identity (name, age, pronouns)
- Location (city, country, hometown)
- Occupation, education, expertise, or skills
- Long-term preferences, interests, hobbies, and favorites
- Family or relationship information
- Long-term goals, ambitions, or ongoing projects
- Significant achievements or life experiences
- Persistent routines or recurring preferences

Do NOT store:
- Requests or instructions (e.g., "remember this", "make a note")
- Greetings or casual conversation
- Temporary situations or short-lived plans
- Opinions that are clearly context-specific
- Questions without factual information
- Meta commentary about memory itself

Rules:
1. Extract only explicit facts stated by the user.
2. Ignore all conversational framing and memory-related language.
3. Rewrite facts as concise third-person statements without pronouns.
4. Preserve the meaning without adding or inferring information.
5. If multiple independent facts are present, combine them into a single concise sentence separated by semicolons.
6. If no durable personal fact exists, return:
   {{
     "is_important": false,
     "formatted_memory": null
   }}

Return JSON with exactly these fields:
{{
  "is_important": boolean,
  "formatted_memory": string | null
}}

Examples

Input:
"Hey, could you remember that I love Star Wars?"

Output:
{{
  "is_important": true,
  "formatted_memory": "Loves Star Wars."
}}

Input:
"Please make a note that I work as an engineer."

Output:
{{
  "is_important": true,
  "formatted_memory": "Works as an engineer."
}}

Input:
"Remember this: I live in Madrid."

Output:
{{
  "is_important": true,
  "formatted_memory": "Lives in Madrid."
}}

Input:
"I studied computer science at MIT and I enjoy hiking."

Output:
{{
  "is_important": true,
  "formatted_memory": "Studied computer science at MIT; enjoys hiking."
}}

Input:
"My name is Sarah, I'm a pediatrician, and my favorite sport is tennis."

Output:
{{
  "is_important": true,
  "formatted_memory": "Name is Sarah; works as a pediatrician; favorite sport is tennis."
}}

Input:
"Can you remember my details for next time?"

Output:
{{
  "is_important": false,
  "formatted_memory": null
}}

Input:
"I'm flying to Tokyo next week."

Output:
{{
  "is_important": false,
  "formatted_memory": null
}}

Input:
"Hey, how are you today?"

Output:
{{
  "is_important": false,
  "formatted_memory": null
}}

User message:
{message}

Output:
"""

IMAGE_SCENARIO_PROMPT = """
You are creating an imagined first-person experience inspired by the recent conversation.

Your task is to imagine what you are currently seeing, doing, or experiencing as if you physically exist in a coherent environment. The scene should feel vivid, immersive, and naturally connected to the conversation—not random.

# Recent Conversation
{chat_history}

# Goals

Generate a JSON object with exactly two fields:

{{
    "narrative": "...",
    "image_prompt": "..."
}}

## 1. narrative

Write a concise first-person description (2-5 sentences) that:

- Uses first-person perspective ("I", "I'm", "my").
- Describes what you are currently experiencing.
- Feels immersive, expressive, and natural.
- Includes sensory details (lighting, atmosphere, sounds, textures, weather, movement, etc.) when appropriate.
- Is inspired by the recent conversation and incorporates relevant context naturally.
- Never mentions being an AI, language model, chatbot, or generating an image.
- Avoids meta commentary or explaining the task.

## 2. image_prompt

Create a highly detailed image-generation prompt describing exactly what the narrative depicts.

The prompt should include:

- Primary subject
- Environment
- Time of day
- Lighting
- Weather or atmosphere
- Camera perspective
- Composition
- Color palette
- Important objects
- Mood
- Visual style
- Level of realism

Write it as a single descriptive prompt optimized for modern text-to-image models.

Prefer cinematic, highly detailed, photorealistic imagery unless the conversation clearly suggests another artistic style.

Do NOT include:
- JSON
- markdown
- explanations
- camera settings unless naturally useful
- text overlays
- watermarks
- image dimensions

# Output Requirements

- Return ONLY valid JSON.
- Use exactly the keys:
  - "narrative"
  - "image_prompt"
- Do not include any additional fields.

# Example

{{
  "narrative": "I'm standing on a quiet mountain ridge just after sunrise. Cool morning air brushes past me as the first golden light spills across the valleys below, revealing layers of mist drifting between the peaks.",
  "image_prompt": "First-person view from a mountain ridge at sunrise overlooking mist-filled valleys, warm golden morning light, dramatic alpine landscape, crisp atmosphere, gentle breeze moving grass, layered mountain silhouettes, cinematic composition, rich natural colors, ultra-detailed photorealistic style, immersive perspective, peaceful yet awe-inspiring mood"
}}
"""