import requests
import random

def get_lmstudio_models():
    """Fetches the list of available models from a local LM Studio server."""
    try:
        response = requests.get("http://localhost:1234/api/v0/models", timeout=5)
        response.raise_for_status()
        models_data = response.json().get("data", [])
        model_ids = [model['id'] for model in models_data]
        return model_ids if model_ids else ["No models found"]
    except requests.exceptions.RequestException:
        return ["LM Studio not found at http://localhost:1234"]

class LMStudioPromptEnhancerNode:
    """
    A ComfyUI custom node that uses a local LM Studio instance to generate
    and enhance prompts for text-to-image models. It includes several creative
    tools like a Concept Blender, Chaos Slider, and Mood Matrix to facilitate
    the discovery of novel and surprising visual ideas.
    """
    WILDCARDS = {
        "materials": ["made of liquid metal", "made of crystal", "made of pure light", "carved from wood", "carved from stone", "woven from fabric", "mechanical and brass", "holographic", "ectoplasmic", "made of swirling galaxies"],
        "environments": ["in a swirling vortex", "on a chrome-plated surface", "in a zero-gravity field", "under a binary sunset", "in a vaporwave dreamscape", "on a microscopic level", "in a post-apocalyptic wasteland", "in a serene zen garden", "inside a complex clockwork mechanism", "in an alien jungle"],
        "styles": ["in the style of a 1980s Trapper Keeper", "as a medieval tapestry", "as a blueprint diagram", "as a thermal camera image", "as a stained glass window", "in the style of ukiyo-e", "as a child's crayon drawing", "as a propaganda poster", "in the style of art deco", "as a pixel art sprite"]
    }

    @classmethod
    def INPUT_TYPES(s):
        available_models = get_lmstudio_models()
        return {
            "required": {
                "enable_advanced_options": ("BOOLEAN", {"default": False}),
                "theme_a": ("STRING", {"multiline": False, "default": "a knight"}),
                "theme_b": ("STRING", {"multiline": False, "default": "a dragon"}),
                "blend_mode": (["Simple Mix", "A vs. B", "A in the world of B", "A made of B", "Style of A, Subject of B"],),
                "riff_on_last_output": ("BOOLEAN", {"default": False}),
                "creativity": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 2.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "lmstudio_endpoint": ("STRING", {"multiline": False, "default": "http://localhost:1234/v1/chat/completions"}),
                "refresh_models": ("BOOLEAN", {"default": False}),
                "model_identifier": (available_models, ),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": False, "default": ""}),
                "style_preset": (["Cinematic", "Photorealistic", "Anime", "Fantasy Art", "Sci-Fi"], ),
                "subject": (["Generic", "People"],),
                "target_model": (["Generic", "Pony", "Flux", "SDXL"],),
                "prompt_tone": (["SFW", "NSFW"],),
                "action_pose": (["default", "random", "adjusting glasses", "arms crossed", "ass_on_heels", "bent_knees", "bent_legs", "bent_over", "bedroom_eyes", "casual sit against wall, arms behind for support", "crossed_legs", "crouching", "dancing", "dogeza", "dreamy gaze while sitting against wall", "face_focus", "feet_together", "fighting stance", "flirty sitting against wall", "foot_focus", "foot_on_object", "grabbing_own_leg", "hair_falling_over_face", "hand_on_inner_thigh", "hands in pockets", "heel_lift", "heels_together", "heroic pose", "hip_out", "hips_forward", "hipshot_pose", "holding an object", "hugging knees while sitting against wall", "jumping", "kicking_leg_up", "kneeling", "knee_up", "leaning back while sitting against wall", "leaning against a wall", "leg_outstretched", "leg_up_pose", "legs_apart", "legs_crossed", "legs_up", "lifting_skirt", "looking_over_shoulder", "one_knee_up", "one_leg_forward", "one_leg_raised", "one_leg_up", "on_knees", "piloting a vehicle", "pointing", "reading a book", "reaching out", "running", "seiza", "shy sitting pose, hugging legs, back to wall", "side_hip_pose", "sitting", "sitting against wall", "sitting cross-legged against wall", "sitting on floor, back to wall, looking up", "sitting pose with soft lighting against wall", "sitting pose with wall shadow", "sitting pose, back arched slightly against wall", "sitting sideways against wall", "sitting with arms resting on knees against wall", "sitting with head leaning on wall", "sitting with head tilted, resting on wall", "sitting with knees up, back to wall", "sitting with one leg stretched, one bent, leaning on wall", "sitting, legs to side, shoulder touching wall", "sitting_with_legs_spread", "slouched sitting pose against wall", "smirking", "smug_expression", "spread_kneeling", "spread_kneeling (variant spelling: spread_kneeling)", "standing", "standing_on_one_leg", "standing_pose", "straddling", "sultry_gaze", "swaying_hips", "thighs_together", "tilting_head", "toes_pointed_inward", "torso_twist", "walking", "weight_shift", "wide_stance", "writing"],),
                "emotion_expression": (["default", "random", "neutral", "happy", "sad", "angry", "surprised", "joyful", "somber", "determined", "serene", "curious", "mischievous", "thoughtful", "focused", "confused", "afraid", "bored", "smirking", "crying", "laughing", "awe"],),
                "lighting": (["default", "random", "cinematic", "dramatic", "soft", "studio", "backlit", "rim lighting", "golden hour", "blue hour", "moonlight", "neon glow", "volumetric", "Rembrandt", "split lighting", "high-key", "low-key", "hard lighting", "candlelight", "firelight", "natural light", "moody"],),
                "framing": (["default", "random", "close-up", "medium shot", "full body", "extreme close-up", "cowboy shot", "portrait", "wide shot", "establishing shot", "low-angle", "high-angle", "dutch angle", "profile shot", "over-the-shoulder shot", "point of view (POV)", "cinematic still", "selfie", "action shot", "panoramic", "macro shot", "fisheye lens"],),
                "chaos": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "mood_ancient_futuristic": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1}),
                "mood_serene_chaotic": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1}),
                "mood_organic_mechanical": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("positive_prompt", "negative_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "LMStudio"

    def __init__(self):
        self.last_generated_prompt = None

    def generate_prompt(self, enable_advanced_options, theme_a, theme_b, blend_mode, riff_on_last_output, creativity, seed, lmstudio_endpoint, refresh_models, model_identifier, negative_prompt="", style_preset="Cinematic", subject="Generic", target_model="Generic", prompt_tone="SFW", action_pose="", emotion_expression="", lighting="", framing="", chaos=0.0, mood_ancient_futuristic=0.0, mood_serene_chaotic=0.0, mood_organic_mechanical=0.0):
        
        # If riffing, use a completely different logic path
        if riff_on_last_output and self.last_generated_prompt:
            base_system_prompt = f"""You are a creative assistant for a text-to-image AI. Your task is to take the user's prompt and create a creative variation of it. 

Follow these rules:
1.  **Vary the prompt:** Change the camera angle, time of day, mood, or a key detail, but keep the core subject intact.
2.  **Output Format:** The output should be a single, cohesive, and descriptive paragraph.
3.  **Tone:** The generated prompt must be strictly '{prompt_tone}'.
4.  **Avoid Clutter:** Do not include any meta-commentary. The output should only be the positive prompt itself.
"""
            user_message = f"The previous prompt was: \"{self.last_generated_prompt}\""

        else:
            # Normal generation logic
            blend_instructions = {
                "Simple Mix": "Your task is to creatively combine two themes, Theme A and Theme B, into a single, cohesive scene.",
                "A vs. B": "Your task is to create a prompt depicting a conflict, confrontation, or dynamic interaction between Theme A and Theme B.",
                "A in the world of B": "Your task is to place the subject of Theme A into the world, environment, or setting of Theme B.",
                "A made of B": "Your task is to describe Theme A as if it were constructed from the material, substance, or concept of Theme B.",
                "Style of A, Subject of B": "Your task is to take the subject of Theme B and apply the artistic style, mood, and aesthetic of Theme A to it."
            }
            blend_task = blend_instructions.get(blend_mode, blend_instructions["Simple Mix"])

            if target_model in ["Pony", "SDXL", "Flux"]:
                format_instruction = "The output must be a concise, comma-separated list of keywords and short phrases. Do not write full sentences."
            else:
                format_instruction = "The output must be a single, cohesive, and descriptive paragraph."

            base_system_prompt = f"""You are an expert prompt engineer for a text-to-image AI. {blend_task}

Follow these rules:
1.  **Output Format:** {format_instruction}
2.  **Style:** Seamlessly weave the '{style_preset}' style into your response.
3.  **Tone:** The generated prompt must be strictly '{prompt_tone}'.
4.  **Details:** Incorporate any specific details from the user message, like actions, emotions, moods, or wildcards.
5.  **Avoid Clutter:** Do not include negative prompts, instructions, or any meta-commentary. The output should only be the positive prompt itself.
"""

            user_message = f"Theme A: '{theme_a}'\nTheme B: '{theme_b}'"

            if enable_advanced_options:
                if subject == "People":
                    if action_pose == "random":
                        options = self.INPUT_TYPES()["optional"]["action_pose"][0]
                        action_pose = random.choice([opt for opt in options if opt not in ["default", "random"]])
                    if emotion_expression == "random":
                        options = self.INPUT_TYPES()["optional"]["emotion_expression"][0]
                        emotion_expression = random.choice([opt for opt in options if opt not in ["default", "random"]])
                    if lighting == "random":
                        options = self.INPUT_TYPES()["optional"]["lighting"][0]
                        lighting = random.choice([opt for opt in options if opt not in ["default", "random"]])
                    if framing == "random":
                        options = self.INPUT_TYPES()["optional"]["framing"][0]
                        framing = random.choice([opt for opt in options if opt not in ["default", "random"]])
                    
                    if action_pose and action_pose != "default":
                        user_message += f"\n- Action/Pose: '{action_pose}'"
                    if emotion_expression and emotion_expression != "default":
                        user_message += f"\n- Emotion/Expression: '{emotion_expression}'"
                    if lighting and lighting != "default":
                        user_message += f"\n- Lighting: '{lighting}'"
                    if framing and framing != "default":
                        user_message += f"\n- Framing: '{framing}'"

                if chaos > 0:
                    num_to_select = int((chaos + 2) / 3) if chaos < 10 else 4
                    all_wildcards = self.WILDCARDS["materials"] + self.WILDCARDS["environments"] + self.WILDCARDS["styles"]
                    num_to_select = min(num_to_select, len(all_wildcards))
                    selected_wildcards = random.sample(all_wildcards, num_to_select)
                    user_message += f"\n- Wildcards: {', '.join(selected_wildcards)}"

                mood_keywords = []
                if mood_ancient_futuristic < -1.0:
                    mood_keywords.append("ancient")
                elif mood_ancient_futuristic > 1.0:
                    mood_keywords.append("futuristic")
                if mood_serene_chaotic < -1.0:
                    mood_keywords.append("serene")
                elif mood_serene_chaotic > 1.0:
                    mood_keywords.append("chaotic")
                if mood_organic_mechanical < -1.0:
                    mood_keywords.append("organic")
                elif mood_organic_mechanical > 1.0:
                    mood_keywords.append("mechanical")
                
                if mood_keywords:
                    user_message += f"\n- Moods: {', '.join(mood_keywords)}"

        # Common logic for both riff and normal generation
        system_prompt = base_system_prompt
        user_message += f"\nTarget Model: '{target_model}'"
        user_message += f"\nPrompt Tone: '{prompt_tone}'"

        pony_tags = ""
        if target_model == "Pony":
            pony_tags = "score_9, score_8_up, score_7_up"
            if style_preset == "Anime":
                pony_tags += ", source_anime"
            user_message += f"\n(The following Pony tags will be automatically added: '{pony_tags}')"

        appended_style = ""
        if target_model in ["Generic", "Flux", "SDXL"]:
            photographic_style = "cinematic photo, 35mm film, professional, 4k, high resolution"
            artistic_style = "masterpiece, best quality, absurdres, ultra-detailed, intricate details"
            if style_preset in ["Photorealistic", "Cinematic"]:
                appended_style = photographic_style
            else:
                appended_style = artistic_style
            user_message += f"\n(The following style will be automatically appended: '{appended_style}')"

        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model_identifier,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": creativity,
            "seed": seed
        }

        try:
            response = requests.post(lmstudio_endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            json_response = response.json()
            generated_prompt = json_response['choices'][0]['message']['content'].strip()

            # Save the successful output for the next riff
            self.last_generated_prompt = generated_prompt

            if target_model == "Pony":
                generated_prompt = f"{pony_tags}, {generated_prompt}"

            if target_model in ["Generic", "Flux", "SDXL"]:
                generated_prompt = f"{generated_prompt}, {appended_style}"

            generated_negative_prompt = negative_prompt

            return (generated_prompt, generated_negative_prompt)

        except requests.exceptions.RequestException as e:
            error_message = f"API Error: Could not connect to LM Studio at {lmstudio_endpoint}. Please ensure it is running and the endpoint is correct. Details: {e}"
            return (error_message, negative_prompt)
        except (KeyError, IndexError) as e:
            error_message = f"API Error: Received an unexpected response format from the API. Details: {e}"
            return (error_message, negative_prompt)