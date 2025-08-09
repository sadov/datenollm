Here’s a **condensed, polished English version** styled like official documentation:

---

# QuerySelector Usage Example with Automatic DataFrame Display

## Overview

This example demonstrates how to use **QuerySelector** in a Jupyter Notebook to execute natural language queries and interactively view results as paginated DataFrames.

## Quick Start

```python
from datenollm.client import DatenoClient
from datenollm.jupiter_nb import ask_llm_and_create_selector, create_dateno_search_selector

# Initialize client
client = DatenoClient('datenoio/dateno-search', hf_token='YOUR_TOKEN')

# Recommended: wrapper function
query = "the trade turnover between Armenia and Cyprus"
selector, response, history, error = ask_llm_and_create_selector(client, query)

if error:
    print(f"Error: {error}")
else:
    selector.display()
```

**Alternative (manual parsing):**

```python
# query_text, result_json, history, error = ask_llm(client, query)
# import json
# response = json.loads(result_json)
# selector = create_dateno_search_selector(client, response['queries'])
# selector.display()
```

## How It Works

1. **Interface Creation** – RadioButtons allow selecting a single query.
2. **Query Execution** – On "Execute Selected Queries," the chosen query is run.
3. **Data Display** – Results are converted to a DataFrame and shown in a widget.
4. **Client-Side Pagination** – Data is paginated locally without re-fetching.
5. **Controls** – Navigation buttons, page size selection, and page info are available.

## Accessing Results Programmatically

```python
# Get DataFrames
display_dfs = selector.get_display_dfs()

# Get raw query results
query_results = selector.get_query_results()

# Example: inspect the first DataFrame
if display_dfs:
    df = display_dfs[0]
    print(f"Rows in first query: {len(df)}")
    if not df.empty:
        print(df.head())
```

## Key Features

* **Single-query selection** via ipywidgets RadioButtons
* **Separation of concerns** – query execution and display are independent
* **Client-side pagination** for smooth navigation
* **Customizable page size** (5, 10, 25, 50, 100 rows)
* **Page navigation & info**
* **Alternating row formatting** for improved readability
* **Full programmatic access** to results

---

If you want, I can also make a **one-page minimal “cheat sheet”** version with just the essentials for quick reference. That way you have both detailed docs and a fast-start guide.
