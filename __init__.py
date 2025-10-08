import json
import os
from .LMStudioPromptEnhancerNode import LMStudioPromptEnhancerNode

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Path to the package.json file
package_json_path = os.path.join(current_dir, "package.json")

# Read the version from package.json
__version__ = "unknown"
if os.path.exists(package_json_path):
    with open(package_json_path, "r") as f:
        package_info = json.load(f)
        __version__ = package_info.get("version", "unknown")

NODE_CLASS_MAPPINGS = {
    "LMStudioPromptEnhancer": LMStudioPromptEnhancerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LMStudioPromptEnhancer": "LM Studio Prompt Enhancer"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', '__version__']
