import openai
from openai import OpenAI
import os
from tqdm import tqdm
import json
from typing import List
import json
from cache import Cache, CacheKey, CacheValue
import streamlit as st

client = OpenAI(api_key=st.secrets['api_key'])
engine='gpt-3.5-turbo'
cache = Cache() 


def amnbiguous_response(ambiguity: str):
    resp = f'''Your query is ambiguous. {ambiguity}. Can you please provide more details?'''
    return resp


def steps_response(steps: List[str]):
    template = '''Here are the steps to complete the action:
{steps}'''
    return template.format(steps='\n'.join(steps))

def get_query(user_input: str):
    """
    user_input: string, the user's current input
    
    """
    query = f'This is the user command : {user_input}.'
    query += '''Can you detect if the sentence is ambiguous or not in terms of the action the user wants to execute.
If there are no amguities then generate a set of steps that needs to be executed to complete the action. 
Return your response in the following format:
{
    "is_ambiguous": "yes / no",
    "why_ambiguous": "... reason for ambiguity if ambigious",
    "steps": [
        "step 1: ... (in 10 words or less)",
        "step 2: ... (in 10 words or less)",
        "step 3: ... (in 10 words or less)",
        ...
    ]
}
'''
    return query

def get_messages(
        user_messages: List[str],
        chatbot_messages: List[str],
        user_input: str,
        system_prompt: str = None,
        include_chat_history: bool = False
    ):

    """
    user_messages: list of strings, each string is a user message
    chatbot_messages: list of strings, each string is a chatbot response
    user_input: string, the user's current input
    system_prompt: string, the system prompt to use
    include_chat_history: bool, whether to include chat history in the prompt
    
    """
    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    if include_chat_history:
        for user_message, chatbot_message in zip(user_messages, chatbot_messages):
            messages.append({
                "role": "user",
                "content": user_message
            })
            messages.append({
                "role": "assistant",
                "content": chatbot_message
            })

    messages.append({
            "role": "user",
            "content": get_query(user_input)
        })
    return messages

def process_response(response: str):
    """ Process the response from the chatbot and return the relevant information

    response: string, the chatbot's response

    """

    

    response = json.loads(response)

    print('response after json processing', response)
    ambiguous = response['is_ambiguous'] == 'yes'

    if ambiguous:
        return amnbiguous_response(response['why_ambiguous'])
    return steps_response(response['steps'])



def get_chatbot_response(user_messages: List[str], chatbot_messages: List[str], user_input: str):
    """
    user_messages: list of strings, each string is a user message
    chatbot_messages: list of strings, each string is a chatbot response
    user_input: string, the user's current input

    """
    system_prompt = '''You are a system that detects ambiguity in user's query.'''
    print(f'quertyng {engine}')
    messages = get_messages(user_messages, chatbot_messages, user_input, system_prompt, include_chat_history=True)


    cache_key = CacheKey(
        model=engine,
        messages=messages,
        temperature=1.0,
        max_tokens=512
    )
    
    response = None
    if cache.get(cache_key):
        print('cache hit')
        response = cache.get(cache_key).response
        print('cached response', response)

    else:
        generated_str = client.chat.completions.create(
            model=engine,
            messages=messages,
            temperature=1.0,
            max_tokens=512
        )

        print('generated string', generated_str)
        response = generated_str.choices[0].message.content.strip()
        cache_value = CacheValue(response=response)
        cache.set(cache_key, cache_value)
        print('full response', response)

    processed_response = ''
    try:
        processed_response = process_response(response)
    except Exception as e:
        print(f'Error processing response: {response}. {e}')
    return processed_response

