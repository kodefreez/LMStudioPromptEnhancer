import requests

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

# Fetch the models when the script is loaded
available_models = get_lmstudio_models()

class LMStudioPromptEnhancerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "theme": ("STRING", {"multiline": False, "default": "A majestic landscape"}),
                "subtheme": ("STRING", {"multiline": False, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": False, "default": ""}),
                "style_preset": (["Cinematic", "Photorealistic", "Anime", "Fantasy Art", "Sci-Fi"], ),
                "creativity": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 2.0, "step": 0.1}),
                "lmstudio_endpoint": ("STRING", {"multiline": False, "default": "http://localhost:1234/v1/chat/completions"}),
                "model_identifier": (available_models, ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "target_model": (["Generic", "Pony", "Flux", "SDXL"],),
                "prompt_tone": (["SFW", "NSFW"],),
                "pony_tags": ("STRING", {"multiline": False, "default": "score_9, score_8_up, score_7_up, source_anime"}),
                "sdxl_style": ("STRING", {"multiline": True, "default": "cinematic photo, 35mm film, professional, 4k, high resolution"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("positive_prompt", "negative_prompt",)
    FUNCTION = "generate_prompt"

    CATEGORY = "LMStudio"

    def generate_prompt(self, theme, subtheme, negative_prompt, style_preset, creativity, lmstudio_endpoint, model_identifier, seed, target_model="Generic", prompt_tone="SFW", pony_tags="", sdxl_style=""):
        system_prompt = f'''You are an expert prompt engineer for a text-to-image AI. Your task is to take a user's theme and transform it into a detailed, rich, and artistic prompt.

Follow these rules:
1.  **Tone:** The generated prompt must be strictly '{prompt_tone}'.
2.  **Structure:** Create a single, cohesive paragraph. Do not use lists or bullet points.
3.  **Clarity and Detail:** Expand on the user's theme with specific, evocative details. Describe the scene, the subject, the lighting, and the atmosphere.
4.  **Style Integration:** Seamlessly weave the chosen style preset into the prompt. For example, for 'Cinematic', use terms like 'dramatic lighting', 'wide-angle shot', 'film grain'. For 'Photorealistic', use camera settings like '4k, dslr, f/2.8'.
5.  **Model-Specific Syntax:** Pay attention to the target model and apply its specific syntax.
    *   **Pony:** Start the prompt with the provided Pony tags.
    *   **SDXL:** Incorporate the detailed SDXL style information.
    *   **Flux:** Focus on natural, descriptive language.
    *   **Generic:** Create a high-quality, general-purpose prompt.
6.  **Avoid Clutter:** Do not include negative prompts, instructions, or any meta-commentary. The output should only be the positive prompt itself.'''

        user_message = f"Theme: '{theme}'"
        if subtheme:
            user_message += f"\nSub-theme: '{subtheme}'"
        user_message += f"\nStyle Preset: '{style_preset}'"
        user_message += f"\nTarget Model: '{target_model}'"
        user_message += f"\nPrompt Tone: '{prompt_tone}'"


        if target_model == "Pony" and pony_tags:
            user_message += f"\nPony Tags: '{pony_tags}'"
        if target_model == "SDXL" and sdxl_style:
            user_message += f"\nSDXL Style: '{sdxl_style}'"


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

            # Prepend tags for Pony model
            if target_model == "Pony" and pony_tags:
                generated_prompt = f"{pony_tags}, {generated_prompt}"

            # Append style for SDXL model
            if target_model == "SDXL" and sdxl_style:
                generated_prompt = f"{generated_prompt}, {sdxl_style}"

            # For now, we just pass the user's negative prompt through
            generated_negative_prompt = negative_prompt

            return (generated_prompt, generated_negative_prompt)

        except requests.exceptions.RequestException as e:
            error_message = f"API Error: Could not connect to LM Studio at {lmstudio_endpoint}. Please ensure it is running and the endpoint is correct. Details: {e}"
            return (error_message, negative_prompt)
        except (KeyError, IndexError) as e:
            error_message = f"API Error: Received an unexpected response format from the API. Details: {e}"
            return (error_message, negative_prompt)

