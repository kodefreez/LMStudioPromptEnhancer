from PIL import Image
import json

def clear_and_set_prompt(image_path: str, prompt_text: str, output_path: str):
    """
    Opens an image, removes all existing metadata, and saves it with only a 'prompt' metadata field.

    Args:
        image_path (str): The path to the input image.
        prompt_text (str): The prompt text to embed in the image.
        output_path (str): The path to save the modified image.
    """
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Build prompt JSON
            prompt_data = {"prompt": prompt_text}
            prompt_json = json.dumps(prompt_data)

            # Use PngInfo to write textual metadata into PNG images
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("prompt", prompt_json)

            # Save the image with the new metadata
            img.save(output_path, "PNG", pnginfo=pnginfo)

        print(f"Successfully processed '{image_path}' and saved it to '{output_path}'")

    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- How to use this script ---

# 1. Make sure you have Pillow installed: pip install Pillow
# 2. Replace the placeholder values below with your actual image path, prompt, and desired output path.
# 3. Uncomment the last three lines and run the script.

# Example usage:
# input_image = "path/to/your/image.png"
# generated_prompt = "a beautiful landscape, digital art, 4k, high resolution"
# output_image = "path/to/your/fixed_image.png"

# clear_and_set_prompt(input_image, generated_prompt, output_image)
