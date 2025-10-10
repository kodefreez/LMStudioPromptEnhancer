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
        """Set up a node instance before each test."""
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
            "A vs. B": "depicting a conflict, confrontation, or dynamic interaction",
            "A in the world of B": "place the subject of Theme A into the world, environment, or setting of Theme B",
            "A made of B": "describe Theme A as if it were constructed from the material, substance, or concept of Theme B",
            "Style of A, Subject of B": "take the subject of Theme B and apply the artistic style, mood, and aesthetic of Theme A"
        }

        for mode, instruction in blend_instructions.items():
            with self.subTest(mode=mode):
                params = self.base_params.copy()
                self.node.generate_prompt(theme_a="a", theme_b="b", blend_mode=mode, **params)
                system_prompt = mock_post.call_args[1]['json']['messages'][0]['content']
                self.assertIn(instruction, system_prompt)

    @patch('random.sample')
    @patch('requests.post')
    def test_chaos_slider(self, mock_post, mock_random_sample):
        """Test the chaos slider functionality."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'prompt'}}]}
        mock_post.return_value = mock_response
        mock_random_sample.return_value = ["holographic"]

        params = self.base_params.copy()
        params["chaos"] = 3.0
        self.node.generate_prompt(theme_a="test", theme_b="", blend_mode="Simple Mix", **params)
        user_message = mock_post.call_args[1]['json']['messages'][1]['content']
        self.assertIn("- Wildcards: holographic", user_message)

    @patch('requests.post')
    def test_mood_matrix(self, mock_post):
        """Test the Mood Matrix functionality."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'prompt'}}]}
        mock_post.return_value = mock_response

        # Test case 1: No moods
        with self.subTest(case="No moods"):
            params = self.base_params.copy()
            self.node.generate_prompt(theme_a="a", theme_b="b", blend_mode="Simple Mix", **params)
            user_message = mock_post.call_args[1]['json']['messages'][1]['content']
            self.assertNotIn("- Moods:", user_message)

        # Test case 2: Single mood (ancient)
        with self.subTest(case="Ancient mood"):
            params = self.base_params.copy()
            params["mood_ancient_futuristic"] = -10.0
            self.node.generate_prompt(theme_a="a", theme_b="b", blend_mode="Simple Mix", **params)
            user_message = mock_post.call_args[1]['json']['messages'][1]['content']
            self.assertIn("- Moods: ancient", user_message)

        # Test case 3: Multiple moods
        with self.subTest(case="Multiple moods"):
            params = self.base_params.copy()
            params["mood_ancient_futuristic"] = 10.0
            params["mood_serene_chaotic"] = -10.0
            params["mood_organic_mechanical"] = 10.0
            self.node.generate_prompt(theme_a="a", theme_b="b", blend_mode="Simple Mix", **params)
            user_message = mock_post.call_args[1]['json']['messages'][1]['content']
            self.assertIn("- Moods: futuristic, serene, mechanical", user_message)

    @patch('requests.post')
    def test_api_connection_error(self, mock_post):
        """Test the handling of a connection error."""
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Test connection error")

        positive_prompt, _ = self.node.generate_prompt(
            theme_a="test", theme_b="", blend_mode="Simple Mix", **self.base_params
        )
        self.assertIn("API Error: Could not connect to LM Studio", positive_prompt)

if __name__ == '__main__':
    unittest.main()