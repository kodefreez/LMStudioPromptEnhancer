import json
import os

from PIL import Image


def extract_prompt_from_metadata(metadata):
    """
    Extracts the prompt from ComfyUI's metadata.
    It checks for 'prompt' and 'workflow' keys.
    """
    if "prompt" in metadata:
        try:
            prompt_data = json.loads(metadata["prompt"])
            if "prompt" in prompt_data:
                return prompt_data["prompt"]
        except (json.JSONDecodeError, TypeError):
            pass  # Not a JSON string, or not a dict

    if "workflow" in metadata:
        try:
            workflow_data = json.loads(metadata["workflow"])
            # This is a more complex extraction, assuming the prompt is in a node
            # For simplicity, we'll look for a node with a 'prompt' widget
            for node in workflow_data.get("nodes", []):
                if "widgets_values" in node:
                    for value in node["widgets_values"]:
                        if (
                            isinstance(value, str) and len(value) > 100
                        ):  # Heuristic for a prompt
                            return value
        except (json.JSONDecodeError, TypeError):
            pass

    return None


def batch_fix_metadata(input_folder: str, output_folder: str):
    """
    Processes all PNG images in a folder, extracts the prompt, and saves
    a new version with clean metadata to the output folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                with Image.open(image_path) as img:
                    # Extract the prompt from the existing metadata
                    prompt_text = extract_prompt_from_metadata(img.info)

                    if prompt_text:
                        # Create new, clean metadata using PngInfo
                        from PIL.PngImagePlugin import PngInfo

                        pnginfo = PngInfo()
                        pnginfo.add_text("prompt", json.dumps({"prompt": prompt_text}))

                        # Save the image with the new metadata
                        img.save(output_path, "PNG", pnginfo=pnginfo)
                        print(f"Processed '{filename}' and saved to '{output_folder}'")
                    else:
                        print(f"Could not find a prompt for '{filename}'. Skipping.")

            except Exception as e:
                print(f"An error occurred while processing '{filename}': {e}")


# --- How to use this script ---

# 1. Make sure you have Pillow installed: pip install Pillow
# 2. Set the 'input_directory' to the folder with your ComfyUI-generated images.
# 3. Set the 'output_directory' to where you want to save the fixed images.
# 4. Run the script.

# Example usage:
# input_directory = "path/to/your/comfyui/output"
# output_directory = "path/to/your/fixed_images"

# batch_fix_metadata(input_directory, output_directory)
