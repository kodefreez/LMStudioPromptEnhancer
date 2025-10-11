import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import random

# Add the parent directory to the system path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LMStudioPromptEnhancerNode import LMStudioPromptEnhancerNode

class TestLMStudioPromptEnhancerNode(unittest.TestCase):

    def setUp(self):
        """Set up a node instance and base parameters before each test."""
        self.node = LMStudioPromptEnhancerNode()
        self.base_params = {
            "negative_prompt": "",
            "style_preset": "Cinematic",
            "creativity": 0.7,
            "lmstudio_endpoint": "http://fake-url",
            "model_identifier": "fake-model",
            "seed": 123,
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

    @patch('requests.post')
    def test_concept_blender_modes(self, mock_post):
        """Test that the correct system prompt is generated for each blend mode."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'prompt'}}]}
        mock_post.return_value = mock_response

        blend_instructions = {
            "Simple Mix": "creatively combine two themes",
            "A vs. B": "depicting a conflict",
            "A in the world of B": "place the subject of Theme A into the world",
            "A made of B": "describe Theme A as if it were constructed",
            "Style of A, Subject of B": "apply the artistic style, mood, and aesthetic of Theme A"
        }

        for mode, instruction in blend_instructions.items():
            with self.subTest(mode=mode):
                params = self.base_params.copy()
                self.node.generate_prompt(riff_on_last_output=False, theme_a="a", theme_b="b", blend_mode=mode, **params)
                system_prompt = mock_post.call_args[1]['json']['messages'][0]['content']
                self.assertIn(instruction, system_prompt)

    @patch('requests.post')
    def test_prompt_riff_feature(self, mock_post):
        """Test the Prompt Riff functionality."""
        # 1. First run to set the last_generated_prompt
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {'choices': [{'message': {'content': 'first prompt'}}]}
        mock_post.return_value = mock_response1

        params = self.base_params.copy()
        self.node.generate_prompt(riff_on_last_output=False, theme_a="a", theme_b="b", blend_mode="Simple Mix", **params)
        
        self.assertEqual(self.node.last_generated_prompt, "first prompt")

        # 2. Second run with riff enabled
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {'choices': [{'message': {'content': 'riffed prompt'}}]}
        mock_post.return_value = mock_response2

        self.node.generate_prompt(riff_on_last_output=True, theme_a="a", theme_b="b", blend_mode="Simple Mix", **params)

        system_prompt = mock_post.call_args[1]['json']['messages'][0]['content']
        user_message = mock_post.call_args[1]['json']['messages'][1]['content']

        self.assertIn("create a creative variation", system_prompt)
        self.assertIn('The previous prompt was: "first prompt"', user_message)
        self.assertEqual(self.node.last_generated_prompt, "riffed prompt")

    @patch('requests.post')
    def test_riff_with_no_history(self, mock_post):
        """Test that riffing with no history falls back to normal generation."""
        self.node.last_generated_prompt = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'prompt'}}]}
        mock_post.return_value = mock_response

        params = self.base_params.copy()
        self.node.generate_prompt(riff_on_last_output=True, theme_a="a", theme_b="b", blend_mode="Simple Mix", **params)

        system_prompt = mock_post.call_args[1]['json']['messages'][0]['content']
        self.assertIn("creatively combine two themes", system_prompt) # Asserts normal logic was used
        self.assertNotIn("create a creative variation", system_prompt)

    @patch('requests.post')
    def test_api_connection_error(self, mock_post):
        """Test the handling of a connection error."""
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Test connection error")

        positive_prompt, _ = self.node.generate_prompt(
            riff_on_last_output=False, theme_a="test", theme_b="", blend_mode="Simple Mix", **self.base_params
        )
        self.assertIn("API Error: Could not connect to LM Studio", positive_prompt)

if __name__ == '__main__':
    unittest.main()
