import os
import sys
import time
import nbformat
from nbclient import NotebookClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site = os.path.join(BASE_DIR, '.venv', 'Lib', 'site-packages')
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

NOTEBOOK_PATH = os.path.join(BASE_DIR, 'notebooks', 'ecommerce_eda_and_customer_intelligence.ipynb')

def execute_notebook():
    print("=" * 80)
    print(f"EXECUTING JUPYTER NOTEBOOK FROM TOP TO BOTTOM:")
    print(f"File: {NOTEBOOK_PATH}")
    print("=" * 80)

    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': os.path.dirname(NOTEBOOK_PATH)}})

    t0 = time.time()
    try:
        client.execute()
        duration = time.time() - t0
        print(f" Notebook executed successfully in {duration:.2f} seconds with 0 errors!")
        
        # Save executed notebook with generated outputs & plots
        with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print(f" Executed notebook and outputs saved to: {NOTEBOOK_PATH}")
        return True
    except Exception as e:
        print(f" Notebook Execution Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = execute_notebook()
    if not success:
        sys.exit(1)
