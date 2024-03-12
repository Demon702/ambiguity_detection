import unittest
from unittest.mock import patch, mock_open
from cache import CacheKey, CacheValue, Cache  # Replace 'your_module' with the name of your Python file

class TestCacheComponents(unittest.TestCase):

    def setUp(self):
        # Setup that runs before each test method
        self.messages = [
            {"role": "user", "content": "How's the weather today?"},
            {"role": "bot", "content": "It's sunny!"}
        ]
        self.cache_key = CacheKey(model="gpt-3.5", messages=self.messages, temperature=0.5)
        self.cache_value = CacheValue(response="It's sunny!")

    def test_cache_key_hash_and_equality(self):
        # Create another CacheKey with the same parameters
        another_key = CacheKey(model="gpt-3.5", messages=self.messages, temperature=0.5)
        # Hash and equality checks
        self.assertEqual(hash(self.cache_key), hash(another_key))
        self.assertEqual(self.cache_key, another_key)

    def test_cache_key_hash_inequality(self):
        # Create another CacheKey with the same parameters
        different_key = CacheKey(model="gpt-3.5", messages=self.messages, temperature=1)
        # Hash and equality checks
        self.assertNotEqual(hash(self.cache_key), hash(different_key))
        self.assertNotEqual(self.cache_key, different_key)

        different_key = CacheKey(model="gpt-4", messages=self.messages, temperature=1)
        # Hash and equality checks
        self.assertNotEqual(hash(self.cache_key), hash(different_key))
        self.assertNotEqual(self.cache_key, different_key)

        different_key = CacheKey(model="gpt-3.5", messages=[], temperature=1)
        # Hash and equality checks
        self.assertNotEqual(hash(self.cache_key), hash(different_key))
        self.assertNotEqual(self.cache_key, different_key)

    def test_cache_key_to_from_json(self):
        '''Check if to and from json are working'''
    
        json_data = self.cache_key.to_json()
        new_key = CacheKey.from_json(json_data)
        self.assertEqual(self.cache_key, new_key)

    def test_cache_value_to_from_json(self):
        '''Check if from and to json are working'''
        json_data = self.cache_value.to_json()
        new_value = CacheValue.from_json(json_data)
        self.assertEqual(self.cache_value.response, new_value.response)
