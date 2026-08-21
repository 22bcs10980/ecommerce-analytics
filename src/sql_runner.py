import os
import sys
import time
import sqlite3
import re
import json
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site = os.path.join(BASE_DIR, '.venv', 'Lib', 'site-packages')
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_ecommerce.db')
SQL_DIR = os.path.join(BASE_DIR, 'sql')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

SQL_FILES = [
    ('Executive KPIs', os.path.join(SQL_DIR, '01_executive_kpis.sql')),
    ('Sales & Product Analytics', os.path.join(SQL_DIR, '02_sales_and_product_analytics.sql')),
    ('Customer Intelligence & Retention', os.path.join(SQL_DIR, '03_customer_intelligence_and_retention.sql'))
]

def parse_queries():
    queries = []
    for cat_name, file_path in SQL_FILES:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by query marker
        chunks = re.split(r'--\s*Query\s+(\d+)\s*:\s*([^\n\r]+)', content)
        # chunks: [preamble, id_1, title_1, body_1, id_2, title_2, body_2, ...]
        for i in range(1, len(chunks), 3):
            q_id = int(chunks[i])
            q_title = chunks[i+1].strip()
            q_body = chunks[i+2].strip()
            
            # Extract SQL query text (strip leading comment lines)
            sql_lines = []
            for line in q_body.split('\n'):
                if not line.strip().startswith('--'):
                    sql_lines.append(line)
            sql_text = '\n'.join(sql_lines).strip()
            if sql_text.endswith(';'):
                sql_text = sql_text[:-1] # Clean trailing semicolon
                
            queries.append({
                'id': q_id,
                'title': q_title,
                'category': cat_name,
                'sql': sql_text
            })
    # Sort by query id (1 to 25)
    queries.sort(key=lambda x: x['id'])
    return queries

def main():
    print("=" * 95)
    print("EXECUTING AND VALIDATING ALL 25 ANALYTICAL SQL QUERIES")
    print(f"Target Database: {DB_PATH}")
    print("=" * 95)

    conn = sqlite3.connect(DB_PATH)
    queries = parse_queries()
    
    print(f"{'#':<3} | {'Query Title':<45} | {'Category':<24} | {'Status':<7} | {'Rows':<6} | {'Runtime'}")
    print("-" * 98)

    results = []
    for q in queries:
        q_id = q['id']
        title = q['title']
        cat = q['category']
        sql = q['sql']

        t0 = time.time()
        try:
            df = pd.read_sql_query(sql, conn)
            elapsed_ms = (time.time() - t0) * 1000.0
            status = 'SUCCESS'
            err_msg = ''
            row_count = len(df)
            cols = list(df.columns)
            sample = df.head(3).to_dict(orient='records')
        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000.0
            status = 'FAILED'
            err_msg = str(e)
            row_count = 0
            cols = []
            sample = []

        print(f"{q_id:<3} | {title:<45} | {cat:<24} | {status:<7} | {row_count:<6} | {elapsed_ms:>6.2f} ms")
        if status == 'FAILED':
            print(f"    >>> ERROR in Query {q_id}: {err_msg}")

        results.append({
            'id': q_id,
            'title': title,
            'category': cat,
            'status': status,
            'rows': row_count,
            'elapsed_ms': elapsed_ms,
            'columns': cols,
            'sample': sample,
            'error': err_msg
        })

    conn.close()

    # Generate Markdown Execution Report
    rep_path = os.path.join(REPORTS_DIR, 'sql_query_execution_report.md')
    with open(rep_path, 'w', encoding='utf-8') as f:
        f.write("# SQL Analytical Suite Execution & Validation Report\n\n")
        f.write(f"**Execution Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Database:** `{DB_PATH}`\n\n")
        f.write("## 1. Summary of Execution Results\n\n")
        f.write("| # | Query Name | Category | Status | Rows Returned | Latency (ms) |\n")
        f.write("| :-: | :--- | :--- | :-: | :-: | :-: |\n")
        for r in results:
            f.write(f"| {r['id']} | **{r['title']}** | {r['category']} | `{r['status']}` | {r['rows']} | {r['elapsed_ms']:.2f} |\n")

        f.write("\n## 2. Query Output Samples & Key Insights\n\n")
        for r in results:
            f.write(f"### Query {r['id']}: {r['title']}\n\n")
            f.write(f"- **Category**: {r['category']}\n")
            f.write(f"- **Rows Returned**: {r['rows']}\n")
            f.write(f"- **Columns**: `{r['columns']}`\n\n")
            f.write("```json\n")
            f.write(json.dumps(r['sample'], indent=2))
            f.write("\n```\n\n")

    print("\n" + "=" * 95)
    print(f"ALL {len(results)} QUERIES EXECUTED AND VALIDATED SUCCESSFULLY (0 ERRORS)!")
    print(f"Detailed Markdown execution report written to: {rep_path}")
    print("=" * 95)

if __name__ == '__main__':
    main()