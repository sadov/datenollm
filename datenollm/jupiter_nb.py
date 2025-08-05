from datetime import datetime
import json
import os
import shutil

import pandas as pd
from IPython.display import display
import ipywidgets as widgets

from .file_utils import (
    DRIVE_PATH,
    mount_drive_if_needed,
    get_full_path,
    file_exists,
    read_json_file,
    save_json_file
)

def ask_llm(client, query, context_file=None, history_file=None, params=None):
  if not query:
    return None, None, None, "Ask something"

  history = []

  if context_file:
    context_file = get_full_path(context_file, DRIVE_PATH)
    print(f'{context_file=}')

    if file_exists(context_file):
      history.extend(read_json_file(context_file))

  if history_file:
    history_file = get_full_path(history_file, DRIVE_PATH)
  else:
    history_file = get_full_path('history.json', DRIVE_PATH)

  print(f'{history_file=}')

  if file_exists(history_file):
    history.extend(read_json_file(history_file))

  if not params:
    params = {}

  params['history'] = history
  params = json.dumps(params)

  result = client.ask(query=query, history_path=history_file)

  history.append({'role': 'user', 'metadata': None, 'content': query, 'options': None})
  history.append({'role': 'assistant', 'metadata': None, 'content': result, 'options': None})
  save_json_file(history, history_file)

  return query, result, history, None

def history2context(history_file, context_file):
  history_file = get_full_path(history_file, DRIVE_PATH)
  context_file = get_full_path(context_file, DRIVE_PATH)
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
    def __init__(self, history_file=None):
        self.like = None
        mount_drive_if_needed()
        if history_file:
            self.history_file = get_full_path(history_file, DRIVE_PATH)
        else:
            self.history_file = get_full_path('history.json', DRIVE_PATH)
        self.load_history()
        self.create_widgets()

    def load_history(self):
        if file_exists(self.history_file):
          self.history = read_json_file(self.history_file)
        else:
          self.history = []

    def save_history(self):
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
                    out += '<div style="margin:0.2em 0 0.7em 1.5em;">'
                    out += f"<strong>Dateno query:</strong> <em>{query['query']}</em> "
                    if query['filters']:
                        out += '&nbsp;&nbsp;&nbsp;&nbsp;<strong>Filters:</strong>'
                        for f in query['filters']:
                            out += f"&nbsp;&nbsp;{f['name']}={f['value']}"
                    out += "</div>"
        return out

    def last_history_out(self):
        out = self._history2html(self.history[-2:])
        return out

    def history_out(self):
        out = self._history2html()
        return out

    def get_result_text(self):
        return self.last_history_out()

    def display(self):
        buttons = widgets.HBox([self.like_btn, self.dislike_btn, self.none_btn])
        return widgets.VBox([self.result_label, buttons])

def dateno2df(results):
    df_data = []
    for result in results:
        df_data.append({
            '_id': result['_id'],
            'title': result['_source']['dataset']['title'],
            'description': result['_source']['dataset'].get('description', ''),
            'datasets': f'<a href="https://dateno.io/search/#{result["_id"]}">{result["_source"]["dataset"]["title"]}</a><br>'
        })

    df = pd.DataFrame(df_data)
    display_df = df[['datasets']]

    return display_df

def display_table(df, table_id='nb-table'):
    html_table = df.to_html(escape=False, table_id=table_id)

    styled_html = f"""
    <style>
    #{table_id} td, #{table_id} th {{
        text-align: left !important;
        vertical-align: top;
        padding: 8px;
    }}
    </style>
    {html_table}
    """

    return widgets.HTML(styled_html)

def copy_test_data(path=DRIVE_PATH):
    os.makedirs(path, exist_ok=True)
    # Получаем путь к текущему файлу и находим папку test в пакете datenollm
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(current_dir, 'test')
    if os.path.exists(test_dir):
        for file_name in os.listdir(test_dir):
            source_file = os.path.join(test_dir, file_name)
            if os.path.isfile(source_file):
                shutil.copy(source_file, path)
    

class QuerySelector:
    """
    Class for creating interactive query checklist in Google Colab
    """
    
    def __init__(self, queries_data, format_text_func=None, execute_func=None, action_buttons=None):
        """
        Initialize query selector
        
        Args:
            queries_data: list of query dictionaries (usually response['queries'])
            format_text_func: function for formatting checkbox text
                             takes (idx, query) and returns checkbox_text
            execute_func: function for executing selected queries (used for default button)
                         takes list of selected query objects
            action_buttons: list of action button configurations
                           [{'name': 'button_name', 'func': function, 'style': 'style', 'description': 'tooltip'}]
                           where function takes list of selected query objects
        """
        self.queries = queries_data
        self.format_text_func = format_text_func or self._default_format_text
        self.execute_func = execute_func or self._default_execute
        self.action_buttons = action_buttons or []
        self.checkboxes = []
        self.action_button_widgets = []
        self._create_interface()
    
    def _default_format_text(self, idx, query):
        """
        Default text formatting function
        
        Args:
            idx: query index
            query: query object
            
        Returns:
            str: checkbox_text
        """
        question = query['query']
        
        if query.get('filters'):
            qfilters = [f'{f["name"]}={f["value"]}' for f in query['filters']]
            qfilters = ', '.join(qfilters)
            checkbox_text = f'Query: {question} Filters: {qfilters}'
        else:
            checkbox_text = f'Query: {question}'
            
        return checkbox_text
    
    def _default_execute(self, selected_queries):
        """
        Default query execution function
        
        Args:
            selected_queries: list of selected query objects
        """
        print(f"Executing search for {len(selected_queries)} queries:")
        for i, query_data in enumerate(selected_queries, 1):
            print(f"{i}. {query_data}")
    
    def _create_interface(self):
        """Create user interface"""
        # Create checkboxes
        for idx, query in enumerate(self.queries):
            checkbox_text = self.format_text_func(idx, query)
            
            checkbox = widgets.Checkbox(
                value=False,
                description=checkbox_text,
                layout=widgets.Layout(
                    width='auto',
                    margin='2px 0px',
                    min_width='300px'
                ),
                style={
                    'description_width': 'initial'
                }
            )
            
            self.checkboxes.append((checkbox, query))
        
        # Create control buttons
        self._create_control_buttons()
        # Create action buttons
        self._create_action_buttons()
        
        # Create main container
        self._create_main_container()
    
    def _create_control_buttons(self):
        """Create buttons for mass select/deselect"""
        self.select_all_button = widgets.Button(
            description="Select All",
            button_style='info',
            layout=widgets.Layout(width='120px', margin='2px')
        )
        self.select_all_button.on_click(self._select_all_click)
        
        self.deselect_all_button = widgets.Button(
            description="Deselect All",
            button_style='warning',
            layout=widgets.Layout(width='120px', margin='2px')
        )
        self.deselect_all_button.on_click(self._deselect_all_click)
    
    def _create_action_buttons(self):
        """Create action buttons"""
        self.action_button_widgets = []
        
        # If custom buttons exist, create them
        if self.action_buttons:
            for button_config in self.action_buttons:
                button = widgets.Button(
                    description=button_config.get('name', 'Action'),
                    button_style=button_config.get('style', 'primary'),
                    tooltip=button_config.get('description', ''),
                    layout=widgets.Layout(
                        width='auto',
                        margin='5px 2px'
                    )
                )
                
                # Create handler for each button
                def make_action_handler(func):
                    def on_action_click(b):
                        selected_queries = self._get_selected_queries()
                        if selected_queries:
                            result = func(selected_queries)
                            # Store the result with button name as key
                            if not hasattr(self, 'action_results'):
                                self.action_results = {}
                            self.action_results[button_config.get('name', 'Action')] = result
                            return result
                        else:
                            print("No queries selected!")
                            # Clear action results when no queries selected
                            button_name = button_config.get('name', 'Action')
                            if hasattr(self, 'action_results') and button_name in self.action_results:
                                del self.action_results[button_name]
                            return None
                    return on_action_click
                
                button.on_click(make_action_handler(button_config['func']))
                self.action_button_widgets.append(button)
        
        # If no custom buttons, create default button
        else:
            default_button = widgets.Button(
                description="Execute Selected Queries",
                button_style='success',
                layout=widgets.Layout(
                    width='auto',
                    margin='10px 0px'
                )
            )
            default_button.on_click(self._on_execute_click)
            self.action_button_widgets.append(default_button)
    
    def _get_selected_queries(self):
        """Get list of selected queries (internal method)"""
        selected_queries = []
        for checkbox, query in self.checkboxes:
            if checkbox.value:
                selected_queries.append(query)
        return selected_queries
    
    def _create_main_container(self):
        """Create main interface container"""
        # Control buttons container
        control_buttons = widgets.HBox([self.select_all_button, self.deselect_all_button])
        
        # Checkbox container
        checkbox_container = widgets.VBox([checkbox for checkbox, _ in self.checkboxes])
        
        # Action buttons container
        if len(self.action_button_widgets) > 1:
            # If multiple buttons, place them horizontally
            action_buttons_container = widgets.HBox(self.action_button_widgets)
        else:
            # If single button, place vertically
            action_buttons_container = widgets.VBox(self.action_button_widgets)
        
        # Main container
        self.main_container = widgets.VBox([
            control_buttons,
            checkbox_container,
            action_buttons_container
        ])
    
    def _select_all_click(self, b):
        """Handler for 'Select All' button"""
        for checkbox, _ in self.checkboxes:
            checkbox.value = True
    
    def _deselect_all_click(self, b):
        """Handler for 'Deselect All' button"""
        for checkbox, _ in self.checkboxes:
            checkbox.value = False
    
    def _on_execute_click(self, b):
        """Handler for default execute button"""
        selected_queries = self._get_selected_queries()
        
        if selected_queries:
            result = self.execute_func(selected_queries)
            # Store the result for later access
            self.last_result = result
            return result
        else:
            print("No queries selected!")
            # Clear last result when no queries selected
            if hasattr(self, 'last_result'):
                delattr(self, 'last_result')
            return None
    
    def display(self):
        """Display interface"""
        display(self.main_container)
    
    def get_last_result(self):
        """
        Get result of last executed function
        
        Returns:
            Result of the last executed function or None
        """
        return getattr(self, 'last_result', None)
    
    def get_action_results(self):
        """
        Get results of all action button executions
        
        Returns:
            dict: Dictionary with button names as keys and results as values
        """
        return getattr(self, 'action_results', {})
    
    def execute_queries_directly(self, query_indices=None):
        """
        Execute queries directly without button click
        
        Args:
            query_indices: list of indices to execute, if None - execute selected
            
        Returns:
            Result of execute_func
        """
        if query_indices is not None:
            # Execute specific queries by indices
            selected_queries = [self.queries[i] for i in query_indices if i < len(self.queries)]
        else:
            # Execute currently selected queries
            selected_queries = self._get_selected_queries()
        
        if selected_queries:
            result = self.execute_func(selected_queries)
            self.last_result = result
            return result
        else:
            print("No queries to execute!")
            # Clear last result when no queries to execute
            if hasattr(self, 'last_result'):
                delattr(self, 'last_result')
            return None
    
    def clear_results(self):
        """
        Clear all stored results
        """
        if hasattr(self, 'last_result'):
            delattr(self, 'last_result')
        if hasattr(self, 'action_results'):
            delattr(self, 'action_results')
    
    def get_selected_queries(self):
        """
        Get list of selected queries
        
        Returns:
            list: list of selected query objects
        """
        return self._get_selected_queries()
    
    def set_selected(self, indices):
        """
        Programmatically set selected queries by indices
        
        Args:
            indices: list of query indices to select
        """
        for i, (checkbox, _) in enumerate(self.checkboxes):
            checkbox.value = i in indices


