from datetime import datetime
import json
import os
from pathlib import Path

from google.colab import drive
import pandas as pd

import ipywidgets as widgets
from IPython.display import display


# Connect Google Drive
def mount_drive_if_needed():
    """Connects Drive if it is not already connected"""
    if not os.path.exists('/content/drive'):
        drive.mount('/content/drive')

def drive_path_name(file_path):
    """Returns full path to file"""
    mount_drive_if_needed()

    # If the path does not start with /content/drive, add a prefix
    if not file_path.startswith(DRIVE_PATH):
        file_path = f'{DRIVE_PATH}/{file_path}'

    return file_path

def file_exists(file_path):
    """Simple check for file existence"""
    file_path = drive_path_name(file_path)
    exists = os.path.exists(file_path)

    return exists


def ask_llm(client, query, context_file=None, history_file=None, params=None):
  if not query:
    return None, None, None, "Ask something"

  history = []

  if context_file:
    context_file = drive_path_name(context_file)
    print(f'{context_file=}')

    if file_exists(context_file):
      history.extend(read_json_file(context_file))

  if history_file:
    history_file = drive_path_name(history_file)
  else:
    history_file = drive_path_name('history.json')

  print(f'{history_file=}')

  if file_exists(history_file):
    history.extend(read_json_file(history_file))

  if not params:
    params = {}

  params['history'] = history
  params = json.dumps(params)

  result = client.ask(query, history, prompt, model,
                      max_tokens, temperature, top_p)

  #result = client.predict(message=query, params=params, api_name="/ask_llm")

  history.append({'role': 'user', 'metadata': None, 'content': query, 'options': None})
  history.append({'role': 'assistant', 'metadata': None, 'content': result, 'options': None})
  save_json_file(history, history_file)

  return query, result, history, None

def history2context(history_file, context_file):
  history_file = drive_path_name(history_file)
  context_file = drive_path_name(context_file)
  history = read_json_file(history_file)
  context = []
  for item in history:
    if item['role'] == 'user':
      user = item
    elif item['role'] == 'assistant':
      assistant = item
      if assistant.get('metadata') and assistant['metadata'].get("like_dislike"):
        context.append(user)
        context.append(assistant)
  save_json_file(context, context_file)

class ChatWidget:
    def __init__(self, history_file='history.json'):
        self.like = None
        mount_drive_if_needed()
        self.history_file = drive_path_name(history_file)
        self.load_history()
        self.create_widgets()

    def load_history(self):
        if file_exists(self.history_file):
          self.history = read_json_file(self.history_file)
        else:
          self.history = []

    def save_history(self):
        metadata = self.history[-1]['metadata']
        save_json_file(self.history, self.history_file)

    def create_widgets(self):
        self.like_btn = widgets.Button(
            description='👍 Like',
            button_style='success',
            layout=widgets.Layout(width='100px'),
            tooltip='Like this answer',
            icon='thumbs-up'
        )

        self.dislike_btn = widgets.Button(
            description='👎 Dislike',
            button_style='danger',
            layout=widgets.Layout(width='100px'),
            tooltip='Dislike this answer',
            icon='thumbs-down'
        )

        self.none_btn = widgets.Button(
            description='No feedback',
            button_style='',
            layout=widgets.Layout(width='100px'),
            tooltip='No feedback given',
            icon='minus-circle'
        )

        self.result_label = widgets.HTML(
            value=self.get_result_text()
        )

        self.like_btn.on_click(self.on_like)
        self.dislike_btn.on_click(self.on_dislike)
        self.none_btn.on_click(self.on_none)

    def handle_cick(self, like=None):
        self.like = like
        metadata = self.history[-1]['metadata']
        if like is not None:
            if metadata is None:
                metadata = {}
            metadata['like_dislike'] = self.like
            metadata['index'] = len(self.history)
            metadata['timestamp'] = str(datetime.now())
        else:
            metadata = {}
        self.history[-1]['metadata'] = metadata
        self.save_history()
        self.update_display()

    def on_like(self, b):
        self.handle_cick('Like')

    def on_dislike(self, b):
        self.handle_cick('Dislike')

    def on_none(self, b):
        self.handle_cick(None)

    def update_display(self):
        self.result_label.value = self.get_result_text()

    def _history2html(self, history=None):
        if not history:
            history = self.history
        out = ''
        idx = 1
        num = ''
        for item in history:
            icon = ''
            if item['role'] == 'user':
                question = item['content']
                num = f'{idx}. '
                idx += 1
            elif item['role'] == 'assistant':
                metadata = item['metadata']
                if metadata and metadata.get('like_dislike'):
                    if metadata['like_dislike'] == 'Like':
                        icon = "👍 "
                    elif metadata['like_dislike'] == 'Dislike':
                        icon = "👎 "
                    else:
                        icon = ''
                out += f"<strong>{num}Question:</strong> <strong><em>{question}</em></strong> {icon}<br>"
                queries=json.loads(item['content'])
                for query in queries['queries']:
                    out += f'<div style="margin:0.2em 0 0.7em 1.5em;">'
                    out += f"<strong>Dateno query:</strong> <em>{query['query']}</em> "
                    if query['filters']:
                        out += '&nbsp;&nbsp;&nbsp;&nbsp;<strong>Filters:</strong>'
                        for f in query['filters']:
                            out += f"&nbsp;&nbsp;{f['name']}={f['value']}"
                    out += "</div>" #<br>"
        return out

    def last_history_out(self):
        out = self._history2html(self.history[-2:]) # Last question & answer
        return out

    def history_out(self):
        out = self._history2html()
        return out

    def get_result_text(self):
        #return f"<b>Like: {self.like}</b>"
        return self.last_history_out()

    def display(self):
        history = widgets.HTML(self.history_out())
        buttons = widgets.HBox([self.like_btn, self.dislike_btn, self.none_btn])
        #return widgets.VBox([self.result_label, buttons, history])
        return widgets.VBox([self.result_label, buttons])

def dateno2df(results):
    # Создаем DataFrame напрямую из вложенной структуры
    df_data = []
    for result in results:
        df_data.append({
            '_id': result['_id'],
            'title': result['_source']['dataset']['title'],
            'description': result['_source']['dataset'].get('description', ''),
            'datasets': f'<a href="https://dateno.io/search/#{result["_id"]}">{result["_source"]["dataset"]["title"]}</a><br>'
        })

    df = pd.DataFrame(df_data)

    # Выбираем только нужные поля для отображения
    #display_df = df[['html_link', 'description']]
    display_df = df[['datasets']]

    # Сохраняем в HTML
    html = display_df[2:6].to_html(escape=False)

    retutn display_df

# Создаем стилизованную таблицу для Jupyter
def display_left_aligned_table(df):
    html_table = df.to_html(escape=False, table_id='nb-table')

    styled_html = f"""
    <style>
    #nb-table td, #nb-table th {{
        text-align: left !important;
        vertical-align: top;
        padding: 8px;
    }}
    </style>
    {html_table}
    """

    return widgets.HTML(styled_html)
