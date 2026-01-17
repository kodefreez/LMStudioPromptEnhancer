import os
import random
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the system path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from LMStudioPromptEnhancerNode import LMStudioPromptEnhancerNode, get_lmstudio_models


class TestLMStudioPromptEnhancerNode(unittest.TestCase):

    def setUp(self):
        """Set up a node instance and base parameters before each test."""
        self.node = LMStudioPromptEnhancerNode()
        # Parameters that are now optional
        self.optional_params = {
            "negative_prompt": "",
            "style_preset": "Cinematic",
            "subject": "Generic",
            "target_model": "Generic",
            "prompt_tone": "SFW",
            "action_pose": "default",
            "emotion_expression": "default",
            "lighting": "default",
            "framing": "default",
            "chaos": 0.0,
            "mood_ancient_futuristic": 0.0,
            "mood_serene_chaotic": 0.0,
            "mood_organic_mechanical": 0.0,
        }

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_simple_mode_ignores_advanced_features(self, mock_post, mock_get_models):
        """Test that advanced features are ignored when enable_advanced_options is False."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "prompt"}}]
        }
        mock_post.return_value = mock_response

        params = self.optional_params.copy()
        params["chaos"] = 5.0  # Set an advanced parameter

        self.node.generate_prompt(
            enable_advanced_options=False,  # Simple Mode is ON
            theme_a="a",
            theme_b="b",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.7,
            seed=123,
            lmstudio_endpoint="http://f",
            refresh_models=False,
            model_identifier="f-m",
            **params,
        )

        user_message = mock_post.call_args[1]["json"]["messages"][1]["content"]
        self.assertNotIn("Wildcards", user_message)
        self.assertNotIn("Moods", user_message)

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("random.sample")
    @patch("requests.post")
    def test_advanced_mode_uses_features(
        self, mock_post, mock_random_sample, mock_get_models
    ):
        """Test that advanced features are used when enable_advanced_options is True."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "prompt"}}]
        }
        mock_post.return_value = mock_response
        mock_random_sample.return_value = ["holographic"]

        params = self.optional_params.copy()
        params["chaos"] = 5.0
        params["mood_ancient_futuristic"] = 10.0

        self.node.generate_prompt(
            enable_advanced_options=True,  # Advanced Mode is ON
            theme_a="a",
            theme_b="b",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.7,
            seed=123,
            lmstudio_endpoint="http://f",
            refresh_models=False,
            model_identifier="f-m",
            **params,
        )

        user_message = mock_post.call_args[1]["json"]["messages"][1]["content"]
        self.assertIn("Wildcards: holographic", user_message)
        self.assertIn("Moods: futuristic", user_message)

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_api_connection_error(self, mock_post, mock_get_models):
        """Test the handling of a connection error."""
        mock_get_models.return_value = ["fake-model"]
        from requests.exceptions import RequestException

        mock_post.side_effect = RequestException("Test connection error")

        positive_prompt, _, warnings = self.node.generate_prompt(
            enable_advanced_options=False,
            theme_a="test",
            theme_b="",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.5,
            seed=0,
            lmstudio_endpoint="http://fake-url",
            refresh_models=False,
            model_identifier="",
            **self.optional_params,
        )
        self.assertIn("API Error: Could not connect to LM Studio", positive_prompt)
        self.assertIn("API Error: Could not connect to LM Studio", warnings)

    def test_input_types_default_models(self):
        """Ensure INPUT_TYPES does not perform network IO at import and returns a safe placeholder."""
        types = LMStudioPromptEnhancerNode.INPUT_TYPES()
        model_options = types["required"]["model_identifier"][0]
        self.assertIsInstance(model_options, list)
        self.assertIn("No models found", model_options)

    def test_fix_metadata_roundtrip(self):
        """Test that clear_and_set_prompt writes JSON prompt metadata into a PNG."""
        import json
        import tempfile

        from PIL import Image

        from fix_metadata import clear_and_set_prompt

        tmp_in = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        img.save(tmp_in.name)
        tmp_out = tmp_in.name + ".out.png"

        clear_and_set_prompt(tmp_in.name, "hello world", tmp_out)

        with Image.open(tmp_out) as im:
            self.assertIn("prompt", im.info)
            data = json.loads(im.info["prompt"])
            self.assertEqual(data["prompt"], "hello world")

    def test_batch_fix_metadata(self):
        """Test that batch_fix_metadata extracts and rewrites prompts."""
        import json
        import os
        import tempfile

        from PIL import Image
        from PIL.PngImagePlugin import PngInfo

        from batch_fix_metadata import batch_fix_metadata

        tmpdir = tempfile.mkdtemp()
        in_file = os.path.join(tmpdir, "test.png")
        img = Image.new("RGBA", (10, 10), (0, 255, 0, 255))
        pnginfo = PngInfo()
        pnginfo.add_text("prompt", json.dumps({"prompt": "batch prompt"}))
        img.save(in_file, pnginfo=pnginfo)

        outdir = os.path.join(tmpdir, "out")
        batch_fix_metadata(tmpdir, outdir)

        out_file = os.path.join(outdir, "test.png")
        self.assertTrue(os.path.exists(out_file))
        with Image.open(out_file) as im:
            self.assertIn("prompt", im.info)
            data = json.loads(im.info["prompt"])
            self.assertEqual(data["prompt"], "batch prompt")

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_discover_models_and_refresh(self, mock_post, mock_get_models):
        """Ensure discover_models() is used when refresh_models=True and model_identifier is empty."""
        mock_get_models.return_value = ["discovered-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "prompt"}}]
        }
        mock_post.return_value = mock_response

        positive, negative, warnings = self.node.generate_prompt(
            enable_advanced_options=False,
            theme_a="a",
            theme_b="b",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.7,
            seed=0,
            lmstudio_endpoint="http://f",
            refresh_models=True,
            model_identifier="",
            **self.optional_params,
        )
        self.assertEqual(warnings, "")

        sent_model = mock_post.call_args[1]["json"]["model"]
        self.assertEqual(sent_model, "discovered-model")

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_malformed_api_response(self, mock_post, mock_get_models):
        """Test that unexpected response shapes result in an API error message."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # missing choices
        mock_post.return_value = mock_response

        positive_prompt, _, warnings = self.node.generate_prompt(
            enable_advanced_options=False,
            theme_a="test",
            theme_b="",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.5,
            seed=0,
            lmstudio_endpoint="http://fake-url",
            refresh_models=False,
            model_identifier="fake-model",
            **self.optional_params,
        )
        self.assertIn(
            "API Error: Received an unexpected response format", positive_prompt
        )
        self.assertIn("API Error: Received an unexpected response format", warnings)

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_response_json_raises_value_error(self, mock_post, mock_get_models):
        """Test that JSON decoding errors are handled gracefully."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("No JSON")
        mock_post.return_value = mock_response

        positive_prompt, _, warnings = self.node.generate_prompt(
            enable_advanced_options=False,
            theme_a="test",
            theme_b="",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.5,
            seed=0,
            lmstudio_endpoint="http://fake-url",
            refresh_models=False,
            model_identifier="fake-model",
            **self.optional_params,
        )
        self.assertIn(
            "API Error: Received an unexpected response format", positive_prompt
        )
        self.assertIn("API Error: Received an unexpected response format", warnings)

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_riff_ignores_when_no_last(self, mock_post, mock_get_models):
        """When riff_on_last_output is True but no last prompt exists, normal generation should occur."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "prompt"}}]
        }
        mock_post.return_value = mock_response

        self.node.last_generated_prompt = None

        self.node.generate_prompt(
            enable_advanced_options=False,
            theme_a="a",
            theme_b="b",
            blend_mode="Simple Mix",
            riff_on_last_output=True,
            creativity=0.7,
            seed=0,
            lmstudio_endpoint="http://f",
            refresh_models=False,
            model_identifier="fake-model",
            **self.optional_params,
        )

        user_message = mock_post.call_args[1]["json"]["messages"][1]["content"]
        self.assertNotIn("The previous prompt was:", user_message)

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_sfw_blocks_explicit_pose(self, mock_post, mock_get_models):
        """Explicit sexual poses are ignored when prompt_tone is SFW."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "prompt"}}]
        }
        mock_post.return_value = mock_response

        params = self.optional_params.copy()
        params["subject"] = "People"
        params["action_pose"] = "ass_on_heels"
        params["prompt_tone"] = "SFW"

        positive, negative, warnings = self.node.generate_prompt(
            enable_advanced_options=True,
            theme_a="a",
            theme_b="b",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.7,
            seed=0,
            lmstudio_endpoint="http://f",
            refresh_models=False,
            model_identifier="fake-model",
            **params,
        )

        user_message = mock_post.call_args[1]["json"]["messages"][1]["content"]
        self.assertNotIn("Action/Pose: 'ass_on_heels'", user_message)
        self.assertIn("blocked", warnings)

    @patch("LMStudioPromptEnhancerNode.get_lmstudio_models")
    @patch("requests.post")
    def test_nsfw_allows_explicit_pose(self, mock_post, mock_get_models):
        """Explicit sexual poses are allowed when prompt_tone is NSFW."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "prompt"}}]
        }
        mock_post.return_value = mock_response

        params = self.optional_params.copy()
        params["subject"] = "People"
        params["action_pose"] = "ass_on_heels"
        params["prompt_tone"] = "NSFW"

        positive, negative, warnings = self.node.generate_prompt(
            enable_advanced_options=True,
            theme_a="a",
            theme_b="b",
            blend_mode="Simple Mix",
            riff_on_last_output=False,
            creativity=0.7,
            seed=0,
            lmstudio_endpoint="http://f",
            refresh_models=False,
            model_identifier="fake-model",
            **params,
        )

        user_message = mock_post.call_args[1]["json"]["messages"][1]["content"]
        self.assertIn("Action/Pose: 'ass_on_heels'", user_message)
        self.assertEqual(warnings, "")


if __name__ == "__main__":
    unittest.main()
