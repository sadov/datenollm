import datenollm.jupiter_nb
import json

with open('datenollm/examples/queries.json', 'r') as f:
    queries_data = json.load(f)

# Usage examples:
# =====================================

# Custom text formatting function
def custom_format_text(idx, query):
    question = query['query']
    if query.get('filters'):
        qfilters = [f'{f["name"]}={f["value"]}' for f in query['filters']]
        qfilters = ', '.join(qfilters)
        checkbox_text = f'Query: {question} | Filters: {qfilters}'
    else:
        checkbox_text = f'Query: {question}'
    return checkbox_text

# Handler functions that return results
def search_dateno(selected_queries):
    print(f"🔍 Starting search for {len(selected_queries)} queries:")
    results = []
    for i, query_data in enumerate(selected_queries, 1):
        print(f"  {i}. Searching: {query_data['query']}")
        # Simulate search result
        result = f"Search result for: {query_data['query']}"
        results.append(result)
    return results

def analyze_queries(selected_queries):
    print(f"📊 Analyzing {len(selected_queries)} queries:")
    analysis = {
        'total_queries': len(selected_queries),
        'queries_with_filters': len([q for q in selected_queries if q.get('filters')]),
        'query_details': []
    }
    for i, query_data in enumerate(selected_queries, 1):
        print(f"  {i}. Analyzing: {query_data['query']}")
        analysis['query_details'].append({
            'query': query_data['query'],
            'has_filters': bool(query_data.get('filters')),
            'filter_count': len(query_data.get('filters', []))
        })
    return analysis

def export_queries(selected_queries):
    print(f"💾 Exporting {len(selected_queries)} queries:")
    export_data = []
    for i, query_data in enumerate(selected_queries, 1):
        print(f"  {i}. Exporting: {query_data['query']}")
        export_data.append(query_data)
    return export_data

def validate_queries(selected_queries):
    print(f"✅ Validating {len(selected_queries)} queries:")
    validation_results = []
    for i, query_data in enumerate(selected_queries, 1):
        print(f"  {i}. Validating: {query_data['query']}")
        # Simulate validation
        is_valid = len(query_data['query']) > 3  # Simple validation rule
        validation_results.append({
            'query': query_data['query'],
            'is_valid': is_valid,
            'message': 'Valid' if is_valid else 'Query too short'
        })
    return validation_results

# Action buttons configuration
action_buttons = [
    {
        'name': 'Execute Search',
        'func': search_dateno,
        'style': 'success',
        'description': 'Run search for selected queries'
    },
    {
        'name': 'Analyze',
        'func': analyze_queries,
        'style': 'info',
        'description': 'Analyze selected queries'
    },
    {
        'name': 'Export',
        'func': export_queries,
        'style': 'warning',
        'description': 'Export selected queries'
    },
    {
        'name': 'Validate',
        'func': validate_queries,
        'style': 'danger',
        'description': 'Validate query correctness'
    }
]

# =====================================

# Example 1: Get result after button click
def example1():
    selector = QuerySelector(queries_data=response['queries'], execute_func=search_dateno)
    selector.display()
    # After clicking button:
    result = selector.get_last_result()
    print("Last result:", result)

# Example 2: Get results from multiple action buttons
def example2():
    selector = QuerySelector(queries_data=response['queries'], action_buttons=action_buttons)
    selector.display()
    # After clicking various buttons:
    all_results = selector.get_action_results()
    print("All action results:", all_results)

# Example 3: Execute queries programmatically
def example3():
    selector = QuerySelector(queries_data=response['queries'], execute_func=search_dateno)
    selector.set_selected([0, 2, 3])  # Select queries by indices
    result = selector.execute_queries_directly()  # Execute without button click
    print("Direct execution result:", result)

# Example 4: Execute specific queries by indices
def example4():
    selector = QuerySelector(queries_data=response['queries'], execute_func=search_dateno)
    result = selector.execute_queries_directly(query_indices=[1, 3, 5])
    print("Specific queries result:", result)
