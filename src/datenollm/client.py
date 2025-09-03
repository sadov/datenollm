import csv
import json
import os
import logging

from gradio_client import Client
from langchain.schema import AIMessage, HumanMessage

from .file_utils import read_json_file, read_text_file, save_json_file

# Configure logging
log_level = getattr(logging, os.environ.get('DATENOLLM_DEBUG', 'INFO').upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatenoClient:
    def __init__(self, client_addr, hf_token=None):
        if not hf_token:
            hf_token=os.environ.get('HF_TOKEN')
        self.client = Client(client_addr, hf_token)

    def ask(self, query, history_path=None, prompt_path=None,
            model=None, max_tokens=None, temperature=None, top_p=None):
        params = {}
        if prompt_path:
            params['prompt'] = read_text_file(prompt_path)
        if model:
            params['model'] = model
        if max_tokens:
            params['max_tokens'] = max_tokens
        if temperature:
            params['temperature'] = temperature
        if top_p:
            params['top_p'] = top_p

        if history_path:
            history = read_json_file(history_path)
            params['history'] = history

        result = self.client.predict(
            message=query,
            params=json.dumps(params),
            api_name="/ask"
        )

        if history_path:
            history = params.get('history', [])
            history.append({'role': 'user', 'metadata': None, 'content': query, 'options': None})
            history.append({'role': 'assistant', 'metadata': None, 'content': result, 'options': None})
            save_json_file(history, history_path)

        return result

    def get_logs(self):
        result = self.client.predict(
            api_name="/logs"
        )
        return result

    def like(self, index, messages, like):
        if isinstance(messages, dict):
            messages = [messages]

        self.client.predict(
            index=index,
            messages=messages,
            like=like,
            api_name="/like"
        )

    def results2html(self, data, verbose):
        result = self.client.predict(
            data=data,
            verbose=verbose,
            api_name="/results2html",
        )
        return result

class DatenoFilter(DatenoClient):
    def filter(
        self,
        messages,
        history,
        data,
        max_requests,
        max_requests_per_call,
        prompt,
        model,
        max_tokens,
        temperature,
        top_p,
        openai_api_base=None
    ):
        result = self.client.predict(
            messages=messages,
            history=history,
            data=data,
            max_requests=max_requests,
            max_requests_per_call=max_requests_per_call,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            openai_api_base=openai_api_base,
            api_name="/filter",
        )
        return result

    def filter2data(self, data, combined_output):
        result = self.client.predict(
            data=data,
            combined_output=combined_output,
            api_name="/filter2data",
        )
        return result


def read_flagged_log_csv(file_path):
    """
    Reads the flagged log CSV file and returns a list of langchain HumanMessage and AIMessage objects.
    Extra fields (like value, flag, etc) are placed in the 'kwargs' of the last AIMessage in each conversation.
    """
    history = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                conversation = json.loads(row.get('conversation', '[]'))
            except json.JSONDecodeError:
                conversation = []
            for i, msg in enumerate(conversation):
                msg_type = msg.get('role', '').lower()
                if msg_type == 'user':
                    history.append(HumanMessage(content=msg.get('content', '')))
                elif msg_type == 'assistant' or msg_type == 'ai':
                    if i == len(conversation) - 1:
                        # Place extra fields in additional_kwargs for the last AI message
                        options = {k: v for k, v in row.items() if k != 'conversation'}
                        # Move 'flag' to 'timestamp'
                        if 'flag' in options:
                            options['timestamp'] = options.pop('flag')
                        history.append(AIMessage(content=msg.get('content', ''), additional_kwargs=options if options else {}))
                    else:
                        history.append(AIMessage(content=msg.get('content', '')))
                else:
                    # Unknown role, treat as HumanMessage for compatibility
                    history.append(HumanMessage(content=msg.get('content', '')))
    return history

def get_conversation_from_csv(file_path, index):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i == index:
                index = int(row.get('index', None))
                return index, json.loads(row.get('conversation', '[]'))
    return None, None
