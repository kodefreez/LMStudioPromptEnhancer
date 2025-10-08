import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the system path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LMStudioPromptEnhancerNode import LMStudioPromptEnhancerNode

class TestLMStudioPromptEnhancerNode(unittest.TestCase):

    def setUp(self):
        """Set up a node instance before each test."""
        self.node = LMStudioPromptEnhancerNode()

    @patch('requests.post')
    def test_generate_prompt_success(self, mock_post):
        """Test the successful generation of a prompt."""
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'A detailed, artistic prompt.'}}]
        }
        mock_post.return_value = mock_response

        # Call the function
        positive_prompt, negative_prompt = self.node.generate_prompt(
            theme="test theme",
            subtheme="",
            negative_prompt="bad stuff",
            style_preset="Cinematic",
            creativity=0.7,
            lmstudio_endpoint="http://fake-url",
            model_identifier="fake-model",
            seed=123
        )

        # Assertions
        self.assertEqual(positive_prompt, "A detailed, artistic prompt.")
        self.assertEqual(negative_prompt, "bad stuff")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_api_connection_error(self, mock_post):
        """Test the handling of a connection error."""
        # Configure the mock to raise an exception
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Test connection error")

        # Call the function
        positive_prompt, _ = self.node.generate_prompt(
            theme="test", subtheme="", negative_prompt="", style_preset="",
            creativity=0.5, lmstudio_endpoint="http://fake-url", model_identifier="", seed=0
        )

        # Assertions
        self.assertIn("API Error: Could not connect to LM Studio", positive_prompt)

    @patch('requests.post')
    def test_unexpected_api_response(self, mock_post):
        """Test the handling of a malformed API response."""
        # Configure a mock response with missing keys
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': 'bad format'} # Missing 'choices'
        mock_post.return_value = mock_response

        # Call the function
        positive_prompt, _ = self.node.generate_prompt(
            theme="test", subtheme="", negative_prompt="", style_preset="",
            creativity=0.5, lmstudio_endpoint="http://fake-url", model_identifier="", seed=0
        )

        # Assertions
        self.assertIn("API Error: Received an unexpected response format", positive_prompt)

if __name__ == '__main__':
    unittest.main()
