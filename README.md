# Dateno LLM

Framework and toolkit for interacting with Dateno LLM services.

## Installation

To install the package, run the following command:

```bash
pip install .
```
Or from GitHub:

```bash
pip install git+https://github.com/datenoio/datenollm
```

Python >=3.10 required. Dependencies: gradio_client, logfire>=3.24.2

## Framework
The main modules are located in [`src/datenollm/`](src/datenollm/):
- [`client.py`](src/datenollm/client.py) — API client for Dateno LLM services
- [`dateno.py`](src/datenollm/dateno.py) — Dateno search API core logic
- [`file_utils.py`](src/datenollm/file_utils.py) — file operations
- [`jupiter_nb.py`](src/datenollm/jupiter_nb.py) — Jupyter/Colab notebook helpers
- [`server.py`](src/datenollm/server.py) — server logic
- [`cli/`](src/datenollm/cli/) — command-line tools:
	- [`ask.py`](src/datenollm/cli/ask.py), [`logs.py`](src/datenollm/cli/logs.py), [`like.py`](src/datenollm/cli/like.py), [`flagged_log.py`](src/datenollm/cli/flagged_log.py), [`collab2gist.py`](src/datenollm/cli/collab2gist.py)
- [`test/`](src/datenollm/test/) — test data (context files)

## Examples

The `examples/` directory contains Jupyter notebooks (Google Colab compatible).

- [`examples/dateno_llm_context_search.ipynb`](examples/dateno_llm_context_search.ipynb) — An example research study using Dateno's context-switching LLM search agent.
- [`dateno-deep-research-workflow.ipynb`](examples/dateno-deep-research-workflow.ipynb) — An example of Deep Research Workflow


## Utilities

This package provides the following command-line tools:

### `dateno-ask-llm`

Generate structured queries for Dateno from user input using LLM.

**Usage:**

```bash
dateno-ask-llm <addr> <query> [--history <history_file>] [--prompt <prompt_file>] [--model <model_id>] [--max-tokens <max_tokens>] [--temperature <temperature>] [--top-p <top_p>]
```

### `dateno-get-logs`

Download Gradio's flagged logs from the Gradio's app.

**Usage:**

```bash
dateno-get-logs <addr>
```

### `dateno-like`

Flag logs in the app.

**Usage:**

```bash
dateno-like <addr> <index> <like|dislike> <csv_path>
```

### `dateno-flagged-log`

Read and print Gradio's flagged logs from a CSV file.

**Usage:**

```bash
dateno-flagged-log <flagged_log_csv_file>
```

### `dateno-collab2gist`

Fix Jupyter notebooks from Google Colab to a format that displays properly on GitHub Gist. It does this by reading a JSON notebook file from stdin, removing the `metadata.widgets` section, and writing the modified JSON to stdout.

**Usage:**

```bash
dateno-collab2gist < input.ipynb > output.ipynb
```

## License

This project is licensed under the Apache-2.0 License. See LICENSE for details.
