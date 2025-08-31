# Before usning this, make sure you have exported your OpenAI API key as an environment variable:
# export OPENAI_API_KEY="your-openai-api-key"
#
# Optional environment variables:
# OPENAI_API_MODEL - LLM model identifier (default: 'openai/gpt-4.1-mini')
# OPENAI_API_MAX_TOKENS - Maximum number of tokens in LLM response (default: 512)
# OPENAI_API_TEMPERATURE - Generation temperature (default: 0.7)
# OPENAI_API_TOP_P - Nucleus sampling parameter (default: 0.95)
# OPENAI_API_BASE - API base URL (default: "https://openrouter.ai/api/v1")
# DATENOLLM_DEBUG - Set logging level (INFO, DEBUG, WARNING, ERROR, CRITICAL, default: INFO)

import json
import os
import re
import logging

from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage

# Configure logging
log_level = getattr(logging, os.environ.get('DATENOLLM_DEBUG', 'INFO').upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Defaults setting
try:
    with open('prompt.md') as f:
        default_prompt = f.read()
except FileNotFoundError:
    default_prompt = ""
    
try:
    default_model = os.environ['OPENAI_API_MODEL']
except KeyError:
    default_model = 'openai/gpt-4.1-mini'
try:
    default_max_tokens = int(os.environ['OPENAI_API_MAX_TOKENS'])
except:
    #default_max_tokens = 512
    default_max_tokens = 2048
try:
    default_temperature = float(os.environ['OPENAI_API_TEMPERATURE'])
except:
    default_temperature = 0.7
try:
    default_top_p = float(os.environ['OPENAI_API_TOP_P'])
except:
    default_top_p = 0.95

try:
    default_openai_api_base = os.environ['OPENAI_API_BASE']
except KeyError:
    default_openai_api_base = "https://openrouter.ai/api/v1"

try:
    default_flagging_dir = os.environ['GRADIO_FLAGGING_DIR']
except KeyError:
    default_flagging_dir = ".gradio/flagged"

if not default_flagging_dir:
    default_flagging_dir = ".gradio/flagged"


class Server:
    def __init__(self, validator=None,
                 prompt=None, model=None, max_tokens=None,
                 temperature=None, top_p=None,
                 openai_api_base=None, flagging_dir=None):
        if not prompt:  # Use default prompt if not provided
            self.prompt = default_prompt
        if not model:  # Use default model if not provided
            self.model = default_model
        if not max_tokens:  # Use default max_tokens if not provided
            self.max_tokens = default_max_tokens
        if not temperature:  # Use default temperature if not provided
            self.temperature = default_temperature
        if not top_p:  # Use default top_p if not provided
            self.top_p = default_top_p
        if not openai_api_base:  # Use default openai_api_base if not provided
            self.openai_api_base = default_openai_api_base
        if not flagging_dir:  # Use default flagging_dir if not provided
            self.flagging_dir = default_flagging_dir
        logger.debug(f'{self.flagging_dir=}')
        self.validator = validator

    def clean_json_response(self, response_text):
        # Clean markdown blocks
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        return cleaned.strip()    
    
    def llm_query(self, message, history,
                  prompt=None, model=None, max_tokens=None,
                  temperature=None, top_p=None, openai_api_base=None):
        if not prompt: # Use default prompt if not provided
            prompt = self.prompt
        if not model:  # Use default model if not provided
            model = self.model
        if not max_tokens:  # Use default max_tokens if not provided
            max_tokens = self.max_tokens
        if not temperature:  # Use default temperature if not provided
            temperature = self.temperature
        if not top_p:  # Use default top_p if not provided
            top_p = self.top_p
        if not openai_api_base:  # Use default openai_api_base if not provided
            openai_api_base = self.openai_api_base
        
        logger.debug(f"llm_query() parameters:")
        logger.debug(f'  {message=}')
        logger.debug(f'  {history=}')
        logger.debug(f'  {prompt=}')
        logger.debug(f'  {model=}')
        logger.debug(f'  {max_tokens=}')
        logger.debug(f'  {temperature=}')
        logger.debug(f'  {top_p=}')
        logger.debug(f'  {openai_api_base=}')

        llm = ChatOpenAI(
            openai_api_base = openai_api_base,
            model = model,
            max_tokens = max_tokens,
            temperature=temperature,
            top_p = top_p,
        )

        history_langchain_format = [AIMessage(content=self.prompt),]
        for msg in history:
            logger.debug(f'{msg=}')
            if msg['role'] == "user":
                history_langchain_format.append(
                    HumanMessage(content=msg['content']))
            elif msg['role'] == "assistant":
                history_langchain_format.append(AIMessage(content=msg['content']))
        logger.debug(f'{message=}')
        history_langchain_format.append(HumanMessage(content=message))
        
        response = llm.invoke(history_langchain_format)
        response = self.clean_json_response(response.content)

        if self.validator:
            # Responce validation
            try:
                validated_data = self.validator.model_validate_json(response)
                logger.debug(f'{validated_data=}')
            except Exception as e:
                logger.error(f"Validation error: {e}")
                logger.error(f"Cleaned response: {response}")
                response = {"question": "There seems to be something wrong with request processing. An invalid result was received. Try increasing 'Max new tokens' (max_tokens) parameter. If that doesn't help, contact support.", "queries": []}
                return json.dumps(response)
        
        return response

    def llm_filter(self, message, history, data,
                  prompt=None, model=None, max_tokens=None,
                  temperature=None, top_p=None, openai_api_base=None):
        if not prompt: # Use default prompt if not provided
            prompt = self.prompt
        if not model:  # Use default model if not provided
            model = self.model
        if not max_tokens:  # Use default max_tokens if not provided
            max_tokens = self.max_tokens
        if not temperature:  # Use default temperature if not provided
            temperature = self.temperature
        if not top_p:  # Use default top_p if not provided
            top_p = self.top_p
        if not openai_api_base:  # Use default openai_api_base if not provided
            openai_api_base = self.openai_api_base

        logger.debug(f"llm_filter() parameters:")
        logger.debug(f'  {message=}')
        logger.debug(f'  {history=}')
        logger.debug(f'  {type(data)=} {data=}')
        logger.debug(f'  {prompt=}')
        logger.debug(f'  {model=}')
        logger.debug(f'  {max_tokens=}')
        logger.debug(f'  {temperature=}')
        logger.debug(f'  {top_p=}')
        logger.debug(f'  {openai_api_base=}')

        llm = ChatOpenAI(
            openai_api_base = openai_api_base,
            model = model,
            max_tokens = max_tokens,
            temperature=temperature,
            top_p = top_p,
        )

        history_langchain_format = [AIMessage(content=self.prompt),]
        for msg in history:
            logger.debug(f'{msg=}')
            if msg['role'] == "user":
                history_langchain_format.append(
                    HumanMessage(content=msg['content']))
            elif msg['role'] == "assistant":
                history_langchain_format.append(AIMessage(content=msg['content']))

        message = f"""
        # User query
        {message}

        # Data
        ```json
        {json.dumps(data, indent=2)}
        ```
        """
        logger.debug(f'{message=}')

        history_langchain_format.append(HumanMessage(content=message))

        response = llm.invoke(history_langchain_format)
        history_langchain_format.append(HumanMessage(content=message))

        response = llm.invoke(history_langchain_format)
        response = self.clean_json_response(response.content)

        if self.validator:
            # Responce validation
            try:
                validated_data = self.validator.model_validate_json(response)
                logger.debug(f'{validated_data=}')
            except Exception as e:
                logger.error(f"Validation error: {e}")
                logger.error(f"Cleaned response: {response}")
                response = {"question": "There seems to be something wrong with request processing. An invalid result was received. Try increasing 'Max new tokens' (max_tokens) parameter. If that doesn't help, contact support.", "queries": []}
                return json.dumps(response)

        return response

    def validate(self, response):
        # Responce validation
        if self.validator:
            try:
                validated_data = self.validator.model_validate(response)
                logger.debug(f'{validated_data=}')
            except Exception as e:
                logger.error(f"Validation error: {e}")
                logger.error(f"Cleaned response: {response}")
                raise e

    def ask(self,
            message: str,
            params: str,
    ) -> str:
        """Send query to LLM"""
        params_dict = json.loads(params)
        llm_history = params_dict.get('history', [])
        llm_prompt = params_dict.get('prompt', self.prompt)
        llm_model = params_dict.get('model', self.model)
        llm_max_tokens = params_dict.get('max_tokens', self.max_tokens)
        llm_temperature = params_dict.get('temperature', self.temperature)
        llm_top_p = params_dict.get('top_p', self.top_p)

        response = self.llm_query(message, llm_history, llm_prompt, llm_model,
                                llm_max_tokens, llm_temperature, llm_top_p)

        if type(response) is not str and self.validator:
            response = response.model_dump_json()

        logger.debug(f'{response=}')
        return response

    def logs(self):
        """Download logs"""
        if self.flagging_dir:
            log_path = f"{self.flagging_dir}/log.csv"
        else:
            logger.error("Flagging directory is not set.")
            return None

        if os.path.exists(log_path):
            return log_path
        else:
            return None

    def load_prompt_with_datetime(self):
        """Load prompt from file and inject current GMT date/time placeholders."""
        try:
            with open('prompt.md', 'r', encoding='utf-8') as f:
                prompt_content = f.read()

            # Get current date/time in GMT
            import datetime
            current_datetime = datetime.datetime.now(datetime.timezone.utc)
            current_date = current_datetime.strftime("%Y-%m-%d")
            current_year = current_datetime.strftime("%Y")
            current_datetime_full = current_datetime.strftime("%Y-%m-%d %H:%M:%S GMT")
            
            # Replace placeholders with actual values
            prompt_content = prompt_content.replace('{datetime}', current_date)
            prompt_content = prompt_content.replace('{year}', current_year)
            prompt_content = prompt_content.replace('{datetime_full}', current_datetime_full)

            logger.debug(f"Prompt content: {prompt_content}")
            return prompt_content
        except FileNotFoundError:
            logger.warning("prompt.md not found, using default prompt")
            return self.prompt
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return self.prompt
