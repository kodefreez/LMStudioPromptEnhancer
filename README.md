# LM Studio Prompt Enhancer for ComfyUI

A custom node for ComfyUI that connects to a local LM Studio instance to generate enriched, detailed prompts for image synthesis.

## Features

-   **Theme-based Generation:** Start with a broad theme and let a local LLM expand it into a detailed prompt.
-   **Style Presets:** Quickly apply a specific style (e.g., Cinematic, Photorealistic, Anime) to your prompt.
-   **Creativity Control:** Use a slider to adjust the LLM's temperature, balancing between predictable and highly creative outputs.
-   **Direct LM Studio Integration:** Designed to work with the API endpoint of your local LM Studio server.
-   **Model Selection:** Specify which model LM Studio should use via the `model_identifier` field.

### Advanced Options

-   **Target Model Selection:** Tailor the prompt generation for specific models like `Pony`, `Flux`, and `SDXL`. The node will automatically apply the correct syntax and prompting style for the selected model.
-   **Pony-Specific Tags:** When using the `Pony` target model, you can provide custom `score_` and `source_` tags to guide the generation process.
-   **SDXL-Specific Styles:** For the `SDXL` target model, you can add detailed photographic and artistic style information to achieve more precise results.

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
4.  (Optional) Select a `Target Model` from the advanced options and fill in any model-specific details.
5.  Connect the `positive_prompt` output to your image generation node (e.g., KSampler).
6.  Queue your prompt.

## Testing

This project uses Python's built-in `unittest` framework. Tests are located in the `tests/` directory.

To run the tests, navigate to the root directory of the node (`LMStudio-Prompt-Enhancer`) and run the following command:

```bash
python -m unittest discover
```