"""
Realistic E-Commerce Dataset Generator
Generates enterprise-grade, relational e-commerce data with realistic distributions,
economic properties, customer repurchase cycles, seasonality, and intentional data quality issues.

Tables Generated:
1. customers.csv
2. products.csv
3. orders.csv
4. order_items.csv
5. payments.csv
"""

import os
import random
import datetime
import math
import csv
from typing import Dict, List, Tuple

# Set random seeds for deterministic reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

START_DATE = datetime.date(2024, 1, 1)
END_DATE = datetime.date(2026, 6, 30)
TOTAL_DAYS = (END_DATE - START_DATE).days

US_STATES_CITIES = {
    'CA': ['Los Angeles', 'San Francisco', 'San Diego', 'San Jose', 'Sacramento', 'Fresno'],
    'NY': ['New York', 'Buffalo', 'Rochester', 'Yonkers', 'Syracuse', 'Albany'],
    'TX': ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso'],
    'FL': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'St. Petersburg', 'Tallahassee'],
    'IL': ['Chicago', 'Aurora', 'Naperville', 'Joliet', 'Rockford', 'Springfield'],
    'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie', 'Reading', 'Scranton'],
    'OH': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo', 'Akron', 'Dayton'],
    'GA': ['Atlanta', 'Augusta', 'Columbus', 'Macon', 'Savannah', 'Athens'],
    'NC': ['Charlotte', 'Raleigh', 'Greensboro', 'Durham', 'Winston-Salem'],
    'MI': ['Detroit', 'Grand Rapids', 'Warren', 'Sterling Heights', 'Ann Arbor'],
    'NJ': ['Newark', 'Jersey City', 'Paterson', 'Elizabeth', 'Trenton'],
    'VA': ['Virginia Beach', 'Norfolk', 'Chesapeake', 'Richmond', 'Newport News'],
    'WA': ['Seattle', 'Spokane', 'Tacoma', 'Vancouver', 'Bellevue'],
    'AZ': ['Phoenix', 'Tucson', 'Mesa', 'Chandler', 'Scottsdale', 'Glendale'],
    'MA': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Lowell'],
    'TN': ['Nashville', 'Memphis', 'Knoxville', 'Chattanooga', 'Clarksville'],
    'IN': ['Indianapolis', 'Fort Wayne', 'Evansville', 'South Bend', 'Carmel'],
    'MO': ['Kansas City', 'St. Louis', 'Springfield', 'Columbia', 'Independence'],
    'MD': ['Baltimore', 'Frederick', 'Rockville', 'Gaithersburg', 'Bowie'],
    'WI': ['Milwaukee', 'Madison', 'Green Bay', 'Kenosha', 'Racine'],
    'CO': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood'],
    'MN': ['Minneapolis', 'Saint Paul', 'Rochester', 'Bloomington', 'Duluth'],
    'SC': ['Charleston', 'Columbia', 'North Charleston', 'Mount Pleasant', 'Greenville'],
    'AL': ['Huntsville', 'Birmingham', 'Montgomery', 'Mobile', 'Tuscaloosa'],
    'LA': ['New Orleans', 'Baton Rouge', 'Shreveport', 'Lafayette', 'Lake Charles'],
    'KY': ['Louisville', 'Lexington', 'Bowling Green', 'Owensboro', 'Covington'],
    'OR': ['Portland', 'Salem', 'Eugene', 'Gresham', 'Hillsboro'],
    'OK': ['Oklahoma City', 'Tulsa', 'Norman', 'Broken Arrow', 'Edmond'],
    'CT': ['Bridgeport', 'New Haven', 'Stamford', 'Hartford', 'Waterbury'],
    'UT': ['Salt Lake City', 'West Valley City', 'Provo', 'West Jordan', 'Orem'],
    'NV': ['Las Vegas', 'Henderson', 'Reno', 'North Las Vegas', 'Sparks']
}

PRODUCT_TAXONOMY = {
    'Electronics': {
        'Smartphones': [('Pro Smartphone 5G 256GB', 350, 799), ('Ultra Flagship Phone 512GB', 520, 1199), ('Budget Smartphone 64GB', 95, 199), ('Foldable Smartphone 256GB', 680, 1399)],
        'Laptops & Computers': [('Ultrabook Laptop 14-inch', 420, 899), ('Pro Gaming Laptop 16-inch', 780, 1599), ('Compact Desktop Mini PC', 260, 549), ('4K USB-C Monitor 27-inch', 160, 349)],
        'Audio & Headphones': [('Wireless Noise-Cancelling Headphones', 85, 229), ('True Wireless Earbuds Pro', 45, 149), ('Portable Bluetooth Speaker IPX7', 28, 79), ('Dolby Atmos Soundbar System', 140, 329)],
        'Smart Home & Wearables': [('GPS Smart Fitness Watch', 65, 179), ('Smart Video Doorbell HD', 40, 119), ('Mesh Wi-Fi 6 Router System', 70, 189), ('Smart LED Ambient Lighting Kit', 18, 59)],
        'Accessories': [('Fast Wireless Charging Pad 15W', 9, 29), ('USB-C Multiport Hub Adapter', 14, 45), ('Ergonomic Wireless Mouse', 16, 49), ('Mechanical RGB Gaming Keyboard', 38, 99)]
    },
    'Apparel & Fashion': {
        'Men Clothing': [('Premium Oxford Cotton Shirt', 14, 48), ('Slim-Fit Stretch Denim Jeans', 18, 65), ('Merino Wool Crewneck Sweater', 24, 85), ('Waterproof Technical Parka', 45, 149)],
        'Women Clothing': [('Silk Blend Wrap Midi Dress', 22, 89), ('High-Waist Performance Leggings', 12, 54), ('Tailored Wool Blazer', 36, 135), ('Cashmere Cardigan Sweater', 38, 129)],
        'Footwear': [('Cushioned Road Running Shoes', 32, 120), ('Classic Leather Dress Loafers', 42, 140), ('Waterproof Hiking Boots', 48, 160), ('Casual Canvas Low-Top Sneakers', 15, 55)],
        'Accessories & Bags': [('Top-Grain Leather Crossbody Bag', 35, 115), ('Polarized Aviator Sunglasses', 16, 68), ('Automatic Stainless Steel Watch', 60, 195), ('Full-Grain Leather Bifold Wallet', 12, 42)]
    },
    'Home & Kitchen': {
        'Kitchenware & Cookware': [('10-Piece Tri-Ply Stainless Cookware Set', 95, 289), ('Enameled Cast Iron Dutch Oven 6Qt', 40, 129), ('Japanese High-Carbon Chef Knife 8in', 25, 89), ('Digital Air Fryer Max 6Qt', 38, 119)],
        'Appliances': [('Barista Espresso Machine Compact', 140, 399), ('Precision Variable Temp Electric Kettle', 22, 79), ('High-Speed Countertop Blender 1200W', 45, 139), ('Robotic Vacuum & Mop Combo', 160, 449)],
        'Furniture & Decor': [('Ergonomic Mesh Office Chair Pro', 85, 259), ('Adjustable Solid Bamboo Standing Desk', 150, 429), ('Dimmable Arc Floor Reading Lamp', 32, 99), ('Luxury 800 Thread Count Sheet Set', 28, 95)],
        'Storage & Organization': [('Airtight Food Storage Container Set', 12, 39), ('Heavy Duty Wire Shelving Unit 5-Tier', 34, 99), ('Bamboo Expandable Drawer Organizer', 8, 25), ('Closet Organizer System Modular', 24, 75)]
    },
    'Beauty & Personal Care': {
        'Skincare': [('Hydrating Hyaluronic Acid Serum', 8, 32), ('Anti-Aging Retinol Night Cream', 12, 48), ('Mineral Broad Spectrum Sunscreen SPF 50', 7, 26), ('Gentle Foaming Cleanser 200ml', 6, 22)],
        'Haircare': [('Ionic Salon Hair Dryer 1875W', 28, 89), ('Keratin Protein Repair Hair Mask', 9, 29), ('Ceramic Tourmaline Hair Straightener', 20, 69), ('Organic Botanical Argan Oil 100ml', 7, 24)],
        'Personal Care': [('Sonic Electric Toothbrush Smart', 22, 79), ('Precision Beard Trimmer Kit', 16, 52), ('Deep Tissue Percussion Massage Gun', 35, 119), ('Aromatherapy Essential Oil Diffuser', 10, 35)]
    },
    'Sports & Outdoors': {
        'Fitness & Exercise': [('Adjustable Quick-Select Dumbbells 50lb', 110, 299), ('High-Density Non-Slip Yoga Mat', 12, 42), ('Resistance Loop Bands Set of 5', 5, 20), ('Foldable Magnetic Rowing Machine', 160, 469)],
        'Outdoor Recreation': [('Ultralight 2-Person Backpacking Tent', 55, 179), ('Insulated Down Sleeping Bag 20F', 42, 139), ('Double Hammock with Tree Straps', 14, 45), ('Trekking Poles Carbon Fiber Pair', 18, 59)],
        'Cycling & Action': [('Commuter Bike Helmet with LED Light', 18, 59), ('Heavy-Duty U-Lock Bike Lock', 12, 38), ('Rechargeable High-Lumen Bike Light Set', 10, 32), ('Hydration Pack Backpack 2L', 15, 48)]
    },
    'Books & Media': {
        'Business & Economics': [('Principles of Modern Corporate Finance', 15, 45), ('Data-Driven Strategy & Growth', 12, 35), ('Leadership in Exponential Times', 10, 28), ('The Lean Product Lifecycle', 11, 30)],
        'Technology & Data': [('Designing Data-Intensive Applications', 18, 52), ('Python for Advanced Data Analytics', 16, 48), ('Machine Learning Engineering in Practice', 17, 50), ('Cloud Architecture Patterns', 15, 44)],
        'Fiction & Literature': [('The Midnight Chronicle Paperback', 5, 18), ('Sci-Fi Trilogy Collector Edition', 16, 45), ('Contemporary Thriller Hardcover', 8, 26), ('Classic World Literature Anthology', 12, 36)]
    },
    'Toys & Games': {
        'Building & Construction': [('Architecture Modular City Building Kit', 35, 109), ('Robotics STEM Mechanical Building Set', 28, 85), ('Magnetic Tiles Creative Play Set 100pc', 18, 55), ('Space Exploration Rocket Model Kit', 24, 75)],
        'Board Games & Puzzles': [('Strategy Civilization Board Game', 20, 60), ('Cooperative Escape Room Box Game', 12, 35), ('1000-Piece Panoramic Jigsaw Puzzle', 7, 22), ('Fast-Paced Family Card Game', 5, 16)]
    },
    'Automotive & Industrial': {
        'Auto Care & Tools': [('Portable Digital Tire Inflator Pump', 16, 49), ('OBD2 Bluetooth Vehicle Diagnostic Scanner', 14, 42), ('Dual Action Car Polisher Buffer', 38, 110), ('Heavy Duty Jump Starter Power Pack 2000A', 32, 99)],
        'Car Interior & Accessories': [('Custom-Fit All-Weather Floor Mats', 35, 115), ('Magnetic MagSafe Car Phone Mount', 8, 26), ('Compact High-Power Car Vacuum Cleaner', 14, 45), ('HD Front and Rear Dual Dash Cam', 38, 120)]
    }
}

FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Margaret', 'Anthony', 'Betty', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
    'Kenneth', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
    'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
    'Nicholas', 'Shirley', 'Eric', 'Angela', 'Jonathan', 'Helen', 'Stephen', 'Anna',
    'Larry', 'Brenda', 'Justin', 'Pamela', 'Scott', 'Nicole', 'Brandon', 'Emma',
    'Benjamin', 'Samantha', 'Samuel', 'Katherine', 'Gregory', 'Christine', 'Alexander', 'Debra',
    'Frank', 'Rachel', 'Patrick', 'Catherine', 'Raymond', 'Carolyn', 'Jack', 'Janet',
    'Dennis', 'Ruth', 'Jerry', 'Maria', 'Tyler', 'Heather', 'Aaron', 'Diane',
    'Jose', 'Virginia', 'Adam', 'Julie', 'Henry', 'Joyce', 'Nathan', 'Victoria',
    'Douglas', 'Olivia', 'Zachary', 'Kelly', 'Peter', 'Christina', 'Kyle', 'Lauren',
    'Walter', 'Joan', 'Ethan', 'Evelyn', 'Jeremy', 'Judith', 'Harold', 'Megan',
    'Keith', 'Cheryl', 'Christian', 'Andrea', 'Roger', 'Hannah', 'Noah', 'Martha',
    'Gerald', 'Jacqueline', 'Carl', 'Frances', 'Terry', 'Gloria', 'Sean', 'Ann',
    'Austin', 'Teresa', 'Arthur', 'Kathryn', 'Lawrence', 'Sara', 'Jesse', 'Janice',
    'Dylan', 'Jean', 'Bryan', 'Alice', 'Joe', 'Madison', 'Jordan', 'Doris',
    'Billy', 'Abigail', 'Albert', 'Julia', 'Bruce', 'Judy', 'Willie', 'Grace',
    'Gabriel', 'Denise', 'Logan', 'Amber', 'Alan', 'Marilyn', 'Juan', 'Beverly',
    'Wayne', 'Danielle', 'Roy', 'Theresa', 'Ralph', 'Sophia', 'Randy', 'Marie',
    'Eugene', 'Diana', 'Vincent', 'Brittany', 'Russell', 'Natalie', 'Louis', 'Isabella',
    'Philip', 'Charlotte', 'Bobby', 'Rose', 'Johnny', 'Alexis', 'Bradley', 'Kayla'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
    'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
    'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
    'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson',
    'Watson', 'Brooks', 'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza',
    'Ruiz', 'Hughes', 'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers',
    'Long', 'Ross', 'Foster', 'Jimenez', 'Powell', 'Jenkins', 'Perry', 'Russell',
    'Sullivan', 'Bell', 'Coleman', 'Butler', 'Henderson', 'Barnes', 'Gonzales', 'Fisher',
    'Vasquez', 'Simmons', 'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton', 'Graham',
    'Reynolds', 'Griffin', 'Wallace', 'Moreno', 'West', 'Cole', 'Hayes', 'Bryant',
    'Herrera', 'Gibson', 'Ellis', 'Tran', 'Medina', 'Aguilar', 'Stevens', 'Murray',
    'Ford', 'Castro', 'Marshall', 'Owens', 'Harrison', 'Fernandez', 'Mcdonald', 'Woods',
    'Washington', 'Kennedy', 'Wells', 'Vargas', 'Henry', 'Chen', 'Freeman', 'Webb',
    'Tucker', 'Guzman', 'Burns', 'Crawford', 'Olson', 'Simpson', 'Porter', 'Hunter',
    'Gordon', 'Mendez', 'Silva', 'Shaw', 'Snyder', 'Mason', 'Dixon', 'Munoz'
]

STREETS = ['Main St', 'Oak Ave', 'Maple Rd', 'Cedar Blvd', 'Pine St', 'Elm St', 'Washington Ave', 'Park Blvd', 'Sunset Way', 'Highland Dr', 'Broadway', 'Lakeview Ave']
EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'icloud.com', 'hotmail.com', 'proton.me', 'corporate.com', 'bizmail.io']

def generate_customers(num_customers: int = 5500) -> List[Dict]:
    customers = []
    for i in range(1, num_customers + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        cust_id = f'CUST-{10000 + i}'
        
        # Registration date distributed from 2023-01-01 to 2026-05-01
        reg_days_back = random.randint(30, 1200)
        reg_date = END_DATE - datetime.timedelta(days=reg_days_back)
        
        state = random.choice(list(US_STATES_CITIES.keys()))
        city = random.choice(US_STATES_CITIES[state])
        zip_code = f'{random.randint(10000, 99999)}'
        
        clean_email = f'{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@{random.choice(EMAIL_DOMAINS)}'
        phone = f'+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}'
        address = f'{random.randint(100, 9999)} {random.choice(STREETS)}'
        segment = random.choices(['Consumer', 'Corporate', 'Small Business'], weights=[0.70, 0.20, 0.10])[0]

        # Intentional minor data quality issues (~2% noise)
        dirty_city = city
        dirty_phone = phone
        dirty_zip = zip_code
        dirty_name = f'{fn} {ln}'

        noise_dice = random.random()
        if noise_dice < 0.025:
            dirty_phone = ''  # missing phone
        elif noise_dice < 0.04:
            dirty_zip = ''    # missing zip
        elif noise_dice < 0.06:
            dirty_city = city.lower() if random.random() < 0.5 else city.upper() # mixed casing
        elif noise_dice < 0.075:
            dirty_name = f'  {fn} {ln}  ' # leading/trailing whitespace

        customers.append({
            'customer_id': cust_id,
            'customer_name': dirty_name,
            'email': clean_email,
            'phone': dirty_phone,
            'address': address,
            'city': dirty_city,
            'state': state,
            'zip_code': dirty_zip,
            'country': 'United States',
            'signup_date': reg_date.strftime('%Y-%m-%d'),
            'customer_segment': segment
        })
    
    # Inject a tiny number of duplicate customer records (~0.5%)
    duplicates = random.sample(customers, k=int(num_customers * 0.005))
    customers.extend(duplicates)
    return customers

def generate_products(target_count: int = 550) -> List[Dict]:
    products = []
    prod_idx = 1001
    
    for category, subcats in PRODUCT_TAXONOMY.items():
        for subcat, item_templates in subcats.items():
            for base_name, base_cost, base_price in item_templates:
                variations = [
                    ('', 1.0, 1.0),
                    (' - Pro Edition', 1.25, 1.28),
                    (' - Plus', 1.15, 1.18),
                    (' - Standard Pack', 0.90, 0.92),
                    (' - Midnight Black', 1.0, 1.0),
                    (' - Space Gray', 1.0, 1.0),
                    (' - Arctic White', 1.0, 1.0),
                    (' - Special Bundle', 1.45, 1.40)
                ]
                for var_suffix, cost_mult, price_mult in variations:
                    p_id = f'PROD-{prod_idx}'
                    cost = round(base_cost * cost_mult, 2)
                    price = round(base_price * price_mult, 2)
                    weight = round(random.uniform(0.15, 12.5), 2)
                    
                    subcat_val = subcat
                    if random.random() < 0.005:
                        subcat_val = ''
                        
                    products.append({
                        'product_id': p_id,
                        'product_name': f'{base_name}{var_suffix}',
                        'category': category,
                        'sub_category': subcat_val,
                        'cost_price': cost,
                        'retail_price': price,
                        'weight_kg': weight
                    })
                    prod_idx += 1
                    if len(products) >= target_count:
                        break
            if len(products) >= target_count:
                break
        if len(products) >= target_count:
            break
            
    # Inject tiny noise: negative price anomaly for cleaner testing
    if len(products) > 10:
        products[5]['retail_price'] = -abs(products[5]['retail_price'])
    return products

def generate_orders_and_items(
    customers: List[Dict],
    products: List[Dict],
    total_orders_target: int = 26000
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    orders = []
    order_items = []
    payments = []
    
    unique_cust_ids = list(set([c['customer_id'] for c in customers]))
    random.shuffle(unique_cust_ids)
    
    n_cust = len(unique_cust_ids)
    power_custs = unique_cust_ids[:int(n_cust * 0.15)]
    repeat_custs = unique_cust_ids[int(n_cust * 0.15):int(n_cust * 0.50)]
    onetime_custs = unique_cust_ids[int(n_cust * 0.50):]
    
    cust_order_counts = {}
    for c in power_custs:
        cust_order_counts[c] = random.randint(5, 14)
    for c in repeat_custs:
        cust_order_counts[c] = random.randint(2, 4)
    for c in onetime_custs:
        cust_order_counts[c] = 1
        
    cust_lookup = {c['customer_id']: c for c in customers}
    prod_lookup = {p['product_id']: p for p in products if p['retail_price'] > 0}
    prod_id_list = list(prod_lookup.keys())
    
    order_counter = 100001
    item_counter = 500001
    payment_counter = 700001
    
    order_plan = []
    for c_id, count in cust_order_counts.items():
        cust = cust_lookup.get(c_id)
        if not cust:
            continue
        try:
            signup_dt = datetime.datetime.strptime(cust['signup_date'], '%Y-%m-%d').date()
        except Exception:
            signup_dt = START_DATE
            
        earliest_order_dt = max(START_DATE, signup_dt)
        if earliest_order_dt >= END_DATE:
            earliest_order_dt = END_DATE - datetime.timedelta(days=30)
            
        span_days = (END_DATE - earliest_order_dt).days
        if span_days < 1:
            span_days = 1
            
        for _ in range(count):
            day_offset = random.randint(0, span_days)
            ord_date = earliest_order_dt + datetime.timedelta(days=day_offset)
            
            if ord_date.month in [11, 12] and random.random() < 0.35:
                order_plan.append((c_id, ord_date))
            order_plan.append((c_id, ord_date))
            
    order_plan.sort(key=lambda x: x[1])
    
    if len(order_plan) > total_orders_target:
        order_plan = order_plan[:total_orders_target]
    elif len(order_plan) < total_orders_target:
        while len(order_plan) < total_orders_target:
            c_id = random.choice(unique_cust_ids)
            rand_day = START_DATE + datetime.timedelta(days=random.randint(0, TOTAL_DAYS))
            order_plan.append((c_id, rand_day))
        order_plan.sort(key=lambda x: x[1])
        
    for c_id, ord_date in order_plan:
        order_id = f'ORD-{ord_date.year}-{order_counter}'
        order_counter += 1
        
        cust = cust_lookup.get(c_id, {})
        state = cust.get('state', 'CA')
        city = cust.get('city', 'Los Angeles')
        
        status = random.choices(
            ['Delivered', 'Shipped', 'Processing', 'Cancelled', 'Returned'],
            weights=[0.86, 0.05, 0.03, 0.04, 0.02]
        )[0]
        
        shipping_cost = round(random.choice([0.0, 4.99, 9.99, 14.99, 19.99]), 2)
        delivery_days = random.randint(2, 7) if status in ['Delivered', 'Returned'] else (random.randint(1, 4) if status == 'Shipped' else None)
        
        if random.random() < 0.015:
            date_str = ord_date.strftime('%Y/%m/%d')
        elif random.random() < 0.005:
            date_str = ord_date.strftime('%d-%m-%Y')
        else:
            date_str = ord_date.strftime('%Y-%m-%d')
            
        orders.append({
            'order_id': order_id,
            'customer_id': c_id,
            'order_date': date_str,
            'order_status': status,
            'shipping_city': city,
            'shipping_state': state,
            'shipping_cost': shipping_cost,
            'delivery_days': delivery_days if delivery_days is not None else ''
        })
        
        num_items = random.choices([1, 2, 3, 4, 5], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]
        selected_prods = random.sample(prod_id_list, k=min(num_items, len(prod_id_list)))
        
        order_net_total = 0.0
        
        for p_id in selected_prods:
            item_id = f'ITEM-{item_counter}'
            item_counter += 1
            
            prod = prod_lookup[p_id]
            qty = random.choices([1, 2, 3, 4, 5], weights=[0.70, 0.18, 0.07, 0.03, 0.02])[0]
            
            unit_price = prod['retail_price']
            unit_cost = prod['cost_price']
            
            disc_rate = random.choices([0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], weights=[0.45, 0.15, 0.15, 0.12, 0.08, 0.03, 0.02])[0]
            
            gross_rev = round(qty * unit_price, 2)
            disc_amt = round(gross_rev * disc_rate, 2)
            net_rev = round(gross_rev - disc_amt, 2)
            tot_cost = round(qty * unit_cost, 2)
            profit = round(net_rev - tot_cost, 2)
            
            disc_rate_val = disc_rate
            if random.random() < 0.008:
                disc_rate_val = ''
                
            order_items.append({
                'order_item_id': item_id,
                'order_id': order_id,
                'product_id': p_id,
                'quantity': qty,
                'unit_price': unit_price,
                'unit_cost': unit_cost,
                'discount_rate': disc_rate_val,
                'gross_revenue': gross_rev,
                'discount_amount': disc_amt,
                'net_revenue': net_rev,
                'total_cost': tot_cost,
                'profit': profit
            })
            order_net_total += net_rev
            
        payment_id = f'PAY-{payment_counter}'
        payment_counter += 1
        
        pay_method = random.choices(
            ['Credit Card', 'PayPal', 'Debit Card', 'Apple Pay', 'BNPL'],
            weights=[0.48, 0.22, 0.14, 0.10, 0.06]
        )[0]
        
        if status == 'Cancelled':
            pay_status = random.choice(['Failed', 'Refunded'])
        elif status == 'Returned':
            pay_status = 'Refunded'
        else:
            pay_status = 'Success'
            
        pay_days_offset = random.choice([0, 0, 0, 1])
        pay_date = ord_date + datetime.timedelta(days=pay_days_offset)
        total_payment_amt = round(order_net_total + shipping_cost, 2)
        
        payments.append({
            'payment_id': payment_id,
            'order_id': order_id,
            'payment_date': pay_date.strftime('%Y-%m-%d'),
            'payment_method': pay_method,
            'payment_status': pay_status,
            'amount': total_payment_amt
        })

    dup_orders = random.sample(orders, k=int(len(orders) * 0.003))
    orders.extend(dup_orders)
    
    return orders, order_items, payments

def export_to_csv(data: List[Dict], filepath: str):
    if not data:
        return
    keys = data[0].keys()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f' Successfully exported {len(data):,} rows to {filepath}')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(base_dir, 'data', 'raw')
    
    print('=' * 70)
    print('STARTING E-COMMERCE SYNTHETIC DATA GENERATION')
    print('Target: 25,000+ Orders | 5,000+ Customers | 500+ Products | 2+ Years')
    print('=' * 70)
    
    print('1. Generating Customers (with realistic geographic & RFM weights)...')
    customers = generate_customers(num_customers=5500)
    
    print('2. Generating Products & Pricing Taxonomy...')
    products = generate_products(target_count=550)
    
    print('3. Generating Orders, Multi-Item Baskets & Payments...')
    orders, order_items, payments = generate_orders_and_items(
        customers=customers,
        products=products,
        total_orders_target=26000
    )
    
    print('\nSaving raw dataset files...')
    export_to_csv(customers, os.path.join(raw_data_dir, 'customers.csv'))
    export_to_csv(products, os.path.join(raw_data_dir, 'products.csv'))
    export_to_csv(orders, os.path.join(raw_data_dir, 'orders.csv'))
    export_to_csv(order_items, os.path.join(raw_data_dir, 'order_items.csv'))
    export_to_csv(payments, os.path.join(raw_data_dir, 'payments.csv'))
    
    print('=' * 70)
    print('DATA GENERATION COMPLETED SUCCESSFULLY!')
    print(f'Customers count:   {len(customers):,}')
    print(f'Products count:    {len(products):,}')
    print(f'Orders count:      {len(orders):,}')
    print(f'Order Items count: {len(order_items):,}')
    print(f'Payments count:    {len(payments):,}')
    print('=' * 70)

if __name__ == '__main__':
    main()
