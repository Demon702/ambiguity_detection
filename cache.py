from dataclasses import dataclass
from typing import List, Dict
import json
import os

DEFAULT_MAX_TOKENS = 512

@dataclass
class CacheKey:
    model: str
    messages: List[Dict[str, str]]
    temperature: float
    max_tokens: int = DEFAULT_MAX_TOKENS

    def __hash__(self):
        return hash((self.model, self.tuple_messages(self.messages), self.temperature, self.max_tokens))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @staticmethod
    def tuple_messages(messages):
        l = [tuple(sorted(d.items())) for d in messages]
        return tuple(l)
    
    def to_json(self):
        return {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    @staticmethod
    def from_json(json):
        return CacheKey(
            model=json["model"],
            messages=json["messages"],
            temperature=json["temperature"],
            max_tokens=json["max_tokens"]
        )

@dataclass
class CacheValue:
    response: str

    def __hash__(self):
        return hash(self.response)
        
    def to_json(self):
        return {
            "response": self.response
        }
    
    @staticmethod
    def from_json(json):
        return CacheValue(
            response=json["response"]
        )


class Cache:
    def __init__(self, cache_file='cache.jsonl'):
        self.cache_file = cache_file
        self.load_cache()


    def load_cache(self):
        self.cache = {}
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                for line in f.readlines():
                    j = json.loads(line)
                    key = CacheKey.from_json(j)
                    value = CacheValue.from_json(j)
                    self.cache[key] = value

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            for key, value in self.cache.items():
                j = {
                    **key.to_json(),
                    **value.to_json()
                }
                f.write(json.dumps(j) + '\n')

    def get(self, key: CacheKey):
        return self.cache.get(key, None)
    
    def set(self, key: CacheKey, value: CacheValue):
        self.cache[key] = value
        self.save_cache()