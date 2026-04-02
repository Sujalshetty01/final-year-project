# run_notebook.py
"""
Script to automatically execute all cells of 'GNN_API_Demo.ipynb' and save the output.
- Uses nbformat and nbconvert's ExecutePreprocessor.
- Handles errors gracefully and shows which cell failed.
- Checks if FastAPI server is running before execution.
- Saves executed notebook as 'GNN_API_Demo_executed.ipynb'.
- Can be run from terminal: python run_notebook.py
"""

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
import requests
import sys
import time
import os

NOTEBOOK_FILENAME = "GNN_API_Demo.ipynb"
EXECUTED_NOTEBOOK_FILENAME = "GNN_API_Demo_executed.ipynb"
API_URL = "http://127.0.0.1:8000/health"
TIMEOUT = 600  # seconds

def is_api_running(url=API_URL, retries=3, delay=2):
    """Check if the FastAPI server is running by pinging the /health endpoint."""
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(delay)
    return False

def prompt_start_server():
    print("\n[ERROR] FastAPI server is not running at http://127.0.0.1:8000.")
    print("Please start your FastAPI server (e.g., 'uvicorn backend.main:app --reload') and then re-run this script.\n")
    sys.exit(1)

def run_notebook(notebook_path, executed_path, timeout=TIMEOUT):
    """Load, execute, and save the notebook. Print outputs and handle errors."""
    print(f"Loading notebook: {notebook_path}")
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=timeout, kernel_name="python3")
    try:
        print("Executing notebook cells...")
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path) or '.'}})
    except CellExecutionError as e:
        print("\n[ERROR] Error executing the notebook. See details below:\n")
        print(e)
        for i, cell in enumerate(nb.cells):
            if "outputs" in cell and cell.outputs:
                for output in cell.outputs:
                    if output.output_type == "error":
                        print(f"\n[Cell {i+1}] Error:")
                        print("".join(output.traceback))
        print(f"\nNotebook execution stopped due to error. Partial output saved to {executed_path}")
    else:
        print("\nNotebook executed successfully!")

    # Print outputs of all cells
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            print(f"\n[Cell {i+1} Output]:")
            if "outputs" in cell and cell.outputs:
                for output in cell.outputs:
                    if output.output_type == "stream":
                        print(output.text)
                    elif output.output_type == "execute_result":
                        print(output.data.get("text/plain", ""))
                    elif output.output_type == "error":
                        print("".join(output.traceback))
            else:
                print("(No output)")

    # Save the executed notebook
    with open(executed_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"\nExecuted notebook saved as: {executed_path}")

if __name__ == "__main__":
    # Check if FastAPI server is running
    if not is_api_running():
        prompt_start_server()

    # Run the notebook
    run_notebook(NOTEBOOK_FILENAME, EXECUTED_NOTEBOOK_FILENAME, timeout=TIMEOUT)
    print("\n[Success] All cells executed. Demo complete!")
