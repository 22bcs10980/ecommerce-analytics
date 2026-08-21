import sqlite3
import pandas as pd

db_path = r'C:\Users\HP\.gemini\antigravity\scratch\ecommerce-analytics\data\processed\cleaned_ecommerce.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== SQLITE DATABASE VALIDATION & HEALTH CHECK ===')

cursor.execute('''
    SELECT 
        COUNT(*) as total_items,
        SUM(gross_revenue) as total_gross_rev,
        SUM(discount_amount) as total_discounts,
        SUM(net_revenue) as total_net_rev,
        SUM(total_cost) as total_cost,
        SUM(profit) as total_profit,
        AVG(profit_margin_pct) as avg_margin_pct,
        SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) as loss_making_items
    FROM order_items;
''')
row = cursor.fetchone()
print('\n--- Financial Ledger Summary ---')
print(f'Total Line Items:       {row[0]:,}')
print(f'Total Gross Revenue:   ${row[1]:,.2f}')
print(f'Total Discount Given:  ${row[2]:,.2f}')
print(f'Total Net Revenue:     ${row[3]:,.2f}')
print(f'Total Product Cost:    ${row[4]:,.2f}')
print(f'Total Net Profit:      ${row[5]:,.2f}')
print(f'Average Margin:         {row[6]:.2f}%')
print(f'Loss-making items:      {row[7]:,}')

conn.close()