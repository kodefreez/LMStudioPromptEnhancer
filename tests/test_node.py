import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import random

# Add the parent directory to the system path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
            "mood_organic_mechanical": 0.0
        }

    @patch('LMStudioPromptEnhancerNode.get_lmstudio_models')
    @patch('requests.post')
    def test_simple_mode_ignores_advanced_features(self, mock_post, mock_get_models):
        """Test that advanced features are ignored when enable_advanced_options is False."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'prompt'}}]}
        mock_post.return_value = mock_response

        params = self.optional_params.copy()
        params["chaos"] = 5.0 # Set an advanced parameter

        self.node.generate_prompt(
            enable_advanced_options=False, # Simple Mode is ON
            theme_a="a", theme_b="b", blend_mode="Simple Mix", riff_on_last_output=False,
            creativity=0.7, seed=123, lmstudio_endpoint="http://f", refresh_models=False, model_identifier="f-m",
            **params
        )

        user_message = mock_post.call_args[1]['json']['messages'][1]['content']
        self.assertNotIn("Wildcards", user_message)
        self.assertNotIn("Moods", user_message)

    @patch('LMStudioPromptEnhancerNode.get_lmstudio_models')
    @patch('random.sample')
    @patch('requests.post')
    def test_advanced_mode_uses_features(self, mock_post, mock_random_sample, mock_get_models):
        """Test that advanced features are used when enable_advanced_options is True."""
        mock_get_models.return_value = ["fake-model"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'prompt'}}]}
        mock_post.return_value = mock_response
        mock_random_sample.return_value = ["holographic"]

        params = self.optional_params.copy()
        params["chaos"] = 5.0
        params["mood_ancient_futuristic"] = 10.0

        self.node.generate_prompt(
            enable_advanced_options=True, # Advanced Mode is ON
            theme_a="a", theme_b="b", blend_mode="Simple Mix", riff_on_last_output=False,
            creativity=0.7, seed=123, lmstudio_endpoint="http://f", refresh_models=False, model_identifier="f-m",
            **params
        )

        user_message = mock_post.call_args[1]['json']['messages'][1]['content']
        self.assertIn("Wildcards: holographic", user_message)
        self.assertIn("Moods: futuristic", user_message)

    @patch('LMStudioPromptEnhancerNode.get_lmstudio_models')
    @patch('requests.post')
    def test_api_connection_error(self, mock_post, mock_get_models):
        """Test the handling of a connection error."""
        mock_get_models.return_value = ["fake-model"]
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Test connection error")

        positive_prompt, _ = self.node.generate_prompt(
            enable_advanced_options=False, theme_a="test", theme_b="", blend_mode="Simple Mix",
            riff_on_last_output=False, creativity=0.5, seed=0, lmstudio_endpoint="http://fake-url",
            refresh_models=False, model_identifier="", **self.optional_params
        )
        self.assertIn("API Error: Could not connect to LM Studio", positive_prompt)

if __name__ == '__main__':
    unittest.main()
