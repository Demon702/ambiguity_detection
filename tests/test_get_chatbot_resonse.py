import unittest
from unittest.mock import patch, Mock
import sys
sys.path.append('..')
import json
import get_chatbot_response
from cache import CacheValue

cache = Mock()
cache.get = Mock()
cache.get.return_value = None

class TestChatbotFunctions(unittest.TestCase):

    def test_ambiguous_response(self):
        responses = ["Please clarify your request.", "I'm not sure what you're asking for."]
        for res in responses:
            self.assertEqual(get_chatbot_response.amnbiguous_response(res), res)

    def test_steps_response(self):
        steps = ["step 1: do X", "step 2: do Y"]
        expected_output = '''Here are the steps to complete the action:
step 1: do X
step 2: do Y'''
        self.assertEqual(get_chatbot_response.steps_response(steps), expected_output)

    def test_null_steps_response(self):
        steps = []
        expected_output = '''Here are the steps to complete the action:
'''
        self.assertEqual(get_chatbot_response.steps_response(steps), expected_output)

    def test_get_query(self):
        user_input = "Create a sheet"

        expected_output = '''This is the user command : Create a sheet.Can you detect if the sentence is ambiguous or not in terms of the action the user wants to execute.
If there are no amguities then generate a set of steps that needs to be executed to complete the action. 
Return your response in the following format:
{
    "is_ambiguous": "yes / no",
    "follow_up question": "... ask a follow up question if the query is ambiguous",
    "steps": [
        "step 1: ... (in 10 words or less)",
        "step 2: ... (in 10 words or less)",
        "step 3: ... (in 10 words or less)",
        ...
    ]
}
'''
        self.assertEqual(get_chatbot_response.get_query(user_input), expected_output)

    @patch('get_chatbot_response.get_query')
    def test_get_messages(self, mock_get_query):
        mock_get_query.return_value = "mock query"
        result = get_chatbot_response.get_messages([], [], "user input", "system prompt")
        self.assertEqual(result, [
            {
                "role": "system",
                "content": "system prompt"
            },
            {
                "role": "user",
                "content": "mock query"
            }
        ])

    def test_process_response(self):
        response = json.dumps({
            "is_ambiguous": "no",
            "follow_up question": "",
            "steps": ["step 1: do X", "step 2: do Y"]
        })
        expected_output = '''Here are the steps to complete the action:
step 1: do X
step 2: do Y'''
        self.assertEqual(get_chatbot_response.process_response(response), expected_output)

    @patch('get_chatbot_response.client.chat.completions.create')
    @patch('get_chatbot_response.cache.get')
    @patch('get_chatbot_response.cache.set')
    def test_get_chatbot_response(self, mock_cache_set, mock_cache_get, mock_chat_completions_create):
        # Mock cache miss and then a successful API response
        mock_cache_get.return_value = None
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock(content='{"is_ambiguous": "no", "follow_up question": "", "steps": ["step 1: do X", "step 2: do Y"]}')
        mock_chat_completions_create.return_value = mock_response

        user_messages = ["What's the weather like?"]
        chatbot_messages = ["It's sunny."]
        user_input = "Should I wear sunglasses?"

        expected_response = '''Here are the steps to complete the action:
step 1: do X
step 2: do Y'''

        # Execute
        response = get_chatbot_response.get_chatbot_response(user_messages, chatbot_messages, user_input)
        
        # Validate
        self.assertEqual(response, expected_response)
        mock_cache_set.assert_called()  # Check if cache.set was called indicating caching of the response

    @patch('get_chatbot_response.client.chat.completions.create')
    @patch('get_chatbot_response.cache.get')
    @patch('get_chatbot_response.cache.set')
    def test_get_chatbot_response_cache_hit(self, mock_cache_set, mock_cache_get, mock_chat_completions_create):
        # Mock cache miss and then a successful API response

        mock_cache_get.return_value = CacheValue(response = json.dumps({
            "is_ambiguous": "no",
            "follow_up question": "",
            "steps": ["step 1: do X", "step 2: do Y"]
        }))
    

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock(content='{"is_ambiguous": "no", "follow_up question": "", "steps": ["step 1: do X", "step 2: do Y"]}')
        mock_chat_completions_create.return_value = mock_response

        user_messages = ["What's the weather like?"]
        chatbot_messages = ["It's sunny."]
        user_input = "Should I wear sunglasses?"

        expected_response = '''Here are the steps to complete the action:
step 1: do X
step 2: do Y'''

        # Execute
        response = get_chatbot_response.get_chatbot_response(user_messages, chatbot_messages, user_input)
        
        # Validate
        self.assertEqual(response, expected_response)
        mock_chat_completions_create.assert_not_called()  # Check if chat.completions.create was not called
        mock_cache_set.assert_not_called()  # Check if cache.set was called indicating caching of the response

if __name__ == '__main__':
    unittest.main()
