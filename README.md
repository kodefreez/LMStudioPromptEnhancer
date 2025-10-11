# LM Studio Prompt Enhancer for ComfyUI

A custom node for ComfyUI that connects to a local LM Studio instance to generate enriched, detailed prompts for image synthesis.

This node is designed to be a creative partner, helping you discover surprising and complex results with minimal initial direction through features like the Concept Blender, Chaos Slider, and Mood Matrix.

## Features

-   **Concept Blender:** Creatively merge two different themes (`Theme A` and `Theme B`) using several blend modes (e.g., `A vs. B`, `A in the world of B`).
-   **Chaos Slider:** Inject controlled randomness into your prompts to discover surprising and unexpected results.
-   **Mood Matrix:** Guide the prompt's feeling along abstract axes like `Ancient <-> Futuristic` or `Serene <-> Chaotic`.
-   **Subject-Specific Enhancement:** Tailor prompt generation for specific subjects like `People` with dedicated controls.
-   **Model-Aware Output:** Automatically switches between detailed paragraphs and concise, comma-separated tags based on the target model (`SDXL`, `Pony`, etc.).
-   **Direct LM Studio Integration:** Connects directly to your local LM Studio server API.

## Parameters

### Main Creative Controls

-   `theme_a` / `theme_b`: The two core ideas you want to combine.
-   `blend_mode`: Controls how `Theme A` and `Theme B` are combined.
    -   `Simple Mix`: A creative mix of both themes.
    -   `A vs. B`: Pits the themes against each other.
    -   `A in the world of B`: Places Theme A in Theme B's environment.
    -   `A made of B`: Constructs Theme A from the substance of Theme B.
    -   `Style of A, Subject of B`: Applies the aesthetic of Theme A to the subject of Theme B.
-   `style_preset`: Apply a general style to the prompt, such as `Cinematic`, `Photorealistic`, `Anime`, etc.
-   `creativity`: Adjusts the LLM's temperature. Higher values lead to more creative and unpredictable prompts.

### Advanced Controls

-   `subject`: Choose the primary subject type to reveal specialized controls.
    -   `Generic`: A general-purpose prompter for any theme.
    -   `People`: Unlocks the fields below to give you fine-grained control over generating characters.
-   `target_model`: Optimizes the prompt structure for specific models like `Pony`, `Flux`, and `SDXL`.
-   `prompt_tone`: Sets the tone of the generated prompt (`SFW` or `NSFW`).

### Fine-Tuning Sliders

-   `chaos`: (0.0 to 10.0) Injects random keywords to spark creativity. The number of keywords is determined by the chaos level:
    -   **1.0 - 3.9:** 1 wildcard
    -   **4.0 - 6.9:** 2 wildcards
    -   **7.0 - 9.9:** 3 wildcards
    -   **10.0:** 4 wildcards
    The wildcards are pulled from internal lists of creative materials, environments, and art styles.

-   `mood_ancient_futuristic`: (-10.0 to 10.0) Pushes the mood towards `ancient` (negative values < -1.0) or `futuristic` (positive values > 1.0).

-   `mood_serene_chaotic`: (-10.0 to 10.0) Pushes the mood towards `serene` (negative values < -1.0) or `chaotic` (positive values > 1.0).

-   `mood_organic_mechanical`: (-10.0 to 10.0) Pushes the mood towards `organic` (negative values < -1.0) or `mechanical` (positive values > 1.0).

### People Subject Options

These options appear when `subject` is set to `People`. Each dropdown includes a `random` option to let the AI pick a creative choice for you.

-   `action_pose`, `emotion_expression`, `lighting`, `framing`

## Installation

1.  **Clone the repository into your `custom_nodes` folder:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    ```
    (You will need to update the URL once you have a public repository)

2.  **Restart ComfyUI.**
    The required dependencies from `requirements.txt` will be installed automatically on startup.

## How it Works

The node constructs a detailed request for your local language model based on your inputs. The primary instruction is determined by the `blend_mode`, which tells the AI how to combine `Theme A` and `Theme B`. It then layers in details from the Mood Matrix, Chaos slider, and other settings. The final prompt structure (paragraph vs. tags) is determined by the `target_model`.

## Testing

This project uses Python's built-in `unittest` framework. Tests are located in the `tests/` directory.

To run the tests, navigate to the root directory of the node (`LMStudio-Prompt-Enhancer`) and run the following command:

```bash
python -m unittest discover
```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.