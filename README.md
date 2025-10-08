# LM Studio Prompt Enhancer for ComfyUI

A custom node for ComfyUI that connects to a local LM Studio instance to generate enriched, detailed prompts for image synthesis.

## Features

-   **Theme-based Generation:** Start with a broad theme and let a local LLM expand it into a detailed prompt.
-   **Style Presets:** Quickly apply a specific style (e.g., Cinematic, Photorealistic, Anime) to your prompt.
-   **Creativity Control:** Use a slider to adjust the LLM's temperature, balancing between predictable and highly creative outputs.
-   **Direct LM Studio Integration:** Designed to work with the API endpoint of your local LM Studio server.

## Installation

1.  **Clone the repository into your `custom_nodes` folder:**
    ```bash
    git clone https://github.com/conradstrydom/ComfyUI-LM-Studio-Prompt-Enhancer.git
    ```
    (Note: You may need to navigate to your `ComfyUI/custom_nodes` directory first)

2.  **Restart ComfyUI.**
    The required dependencies from `requirements.txt` will be installed automatically on startup.

## Usage

1.  Run your desired model in LM Studio and start the server.
2.  In ComfyUI, add the **LM Studio Prompt Enhancer** node (found in the `LMStudio` category).
3.  Set your theme, style, and other options on the node.
4.  Connect the `positive_prompt` output to your image generation node (e.g., KSampler).
5.  Queue your prompt.
