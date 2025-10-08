import requests

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
                "model_identifier": ("STRING", {"multiline": False, "default": "local-model"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("positive_prompt", "negative_prompt",)
    FUNCTION = "generate_prompt"

    CATEGORY = "LMStudio"

    def generate_prompt(self, theme, subtheme, negative_prompt, style_preset, creativity, lmstudio_endpoint, model_identifier, seed):
        system_prompt = """You are an expert prompt engineer for a text-to-image AI. Your task is to take a user's theme and transform it into a detailed, rich, and artistic prompt.

Follow these rules:
1.  **Structure:** Create a single, cohesive paragraph. Do not use lists or bullet points.
2.  **Clarity and Detail:** Expand on the user's theme with specific, evocative details. Describe the scene, the subject, the lighting, and the atmosphere.
3.  **Style Integration:** Seamlessly weave the chosen style preset into the prompt. For example, for 'Cinematic', use terms like 'dramatic lighting', 'wide-angle shot', 'film grain'. For 'Photorealistic', use camera settings like '4k, dslr, f/2.8'.
4.  **Avoid Clutter:** Do not include negative prompts, instructions, or any meta-commentary. The output should only be the positive prompt itself."""

        user_message = f"Theme: '{theme}'"
        if subtheme:
            user_message += f"\nSub-theme: '{subtheme}'"
        user_message += f"\nStyle Preset: '{style_preset}'"

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
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            json_response = response.json()
            generated_prompt = json_response['choices'][0]['message']['content'].strip()

            # For now, we just pass the user's negative prompt through
            generated_negative_prompt = negative_prompt
            
            return (generated_prompt, generated_negative_prompt)

        except requests.exceptions.RequestException as e:
            error_message = f"API Error: Could not connect to LM Studio at {lmstudio_endpoint}. Please ensure it is running and the endpoint is correct. Details: {e}"
            return (error_message, negative_prompt)
        except (KeyError, IndexError) as e:
            error_message = f"API Error: Received an unexpected response format from the API. Details: {e}"
            return (error_message, negative_prompt)

