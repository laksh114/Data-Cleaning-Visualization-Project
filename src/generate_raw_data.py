import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def generate_messy_dataset(filepath, num_rows=1000):
    """
    Generates a messy dataset for demonstrating data cleaning and preprocessing.
    Contains duplicates, missing values, incorrect types, formatting inconsistencies,
    and outliers.
    """
    np.random.seed(42)
    random.seed(42)
    
    # Generate base data
    transaction_ids = [10000 + i for i in range(num_rows)]
    customer_ids = [f"C-{1000 + random.randint(1, 200)}" for _ in range(num_rows)]
    
    names = [
        "John Doe", "Alice Smith", "Bob Johnson", "Emma Watson", "Michael Brown",
        "Sophia Davis", "David Miller", "Olivia Wilson", "James Taylor", "Emily Anderson"
    ]
    customer_names = [random.choice(names) for _ in range(num_rows)]
    # Add messy spacing and casing to customer names
    customer_names = [f"  {name.lower()} " if i % 5 == 0 else name for i, name in enumerate(customer_names)]
    customer_names = [name.upper() if i % 7 == 0 else name for i, name in enumerate(customer_names)]
    
    categories = ["Electronics", "Home & Kitchen", "Clothing", "Books"]
    product_categories = [random.choice(categories) for _ in range(num_rows)]
    # Add messy capitalization and spelling
    category_mess = {
        "Electronics": ["Electronics", "electronics", "  ELECTronics  ", "Electrnics"],
        "Home & Kitchen": ["Home & Kitchen", "home & kitchen", "HOME & KITCHEN", "Home"],
        "Clothing": ["Clothing", "clothing", "CLOTHing", "Clothes"],
        "Books": ["Books", "books", "  Books  ", "Bks"]
    }
    product_categories = [random.choice(category_mess[cat]) for cat in product_categories]
    
    # Sale Price - numeric with symbols, text, and outliers
    sale_prices = []
    for i in range(num_rows):
        rand_val = random.random()
        if rand_val < 0.05:
            sale_prices.append(np.nan)
        elif rand_val < 0.08:
            sale_prices.append("unknown")
        elif rand_val < 0.10:
            sale_prices.append("Free")
        elif rand_val < 0.12:
            sale_prices.append(99999.00) # Outlier
        elif rand_val < 0.14:
            sale_prices.append(-25.50) # Negative price (invalid)
        else:
            price = round(random.uniform(5.0, 500.0), 2)
            if i % 3 == 0:
                sale_prices.append(f"${price}")
            elif i % 4 == 0:
                sale_prices.append(f"{price} USD")
            else:
                sale_prices.append(str(price))
                
    # Quantity - numbers, decimals, invalid negative values, and outliers
    quantities = []
    for i in range(num_rows):
        rand_val = random.random()
        if rand_val < 0.05:
            quantities.append(np.nan)
        elif rand_val < 0.08:
            quantities.append(1000) # Outlier quantity
        elif rand_val < 0.10:
            quantities.append(-3) # Invalid negative quantity
        elif rand_val < 0.12:
            quantities.append(2.5) # Decimal quantity (invalid for discrete items)
        else:
            quantities.append(random.randint(1, 10))
            
    # Order Date - messy dates
    start_date = datetime(2023, 1, 1)
    order_dates = []
    for i in range(num_rows):
        rand_val = random.random()
        if rand_val < 0.05:
            order_dates.append(np.nan)
        elif rand_val < 0.07:
            order_dates.append("invalid_date")
        else:
            days_to_add = random.randint(0, 365)
            date_obj = start_date + timedelta(days=days_to_add)
            if i % 4 == 0:
                order_dates.append(date_obj.strftime("%Y/%m/%d"))
            elif i % 5 == 0:
                order_dates.append(date_obj.strftime("%d-%b-%Y"))
            elif i % 6 == 0:
                order_dates.append(date_obj.strftime("%Y.%m.%d"))
            else:
                order_dates.append(date_obj.strftime("%Y-%m-%d"))
                
    # Store Location
    locations = ["New York", "Los Angeles", "Chicago", "Houston"]
    store_locations = [random.choice(locations) for _ in range(num_rows)]
    store_locations = [f"  {loc.lower()} " if i % 6 == 0 else loc for i, loc in enumerate(store_locations)]
    store_locations = [loc.upper() if i % 8 == 0 else loc for i, loc in enumerate(store_locations)]
    # Add some nulls
    store_locations = [np.nan if random.random() < 0.05 else loc for loc in store_locations]
    
    # Customer Rating
    ratings = []
    for i in range(num_rows):
        rand_val = random.random()
        if rand_val < 0.10:
            ratings.append(np.nan)
        elif rand_val < 0.12:
            ratings.append(99.0) # outlier
        elif rand_val < 0.14:
            ratings.append(-1.5) # invalid negative rating
        else:
            ratings.append(round(random.uniform(1.0, 5.0), 1))
            
    # Build DataFrame
    df = pd.DataFrame({
        " Transaction ID ": transaction_ids,
        "Customer ID": customer_ids,
        "Customer Name": customer_names,
        "Product Category": product_categories,
        "Sale Price": sale_prices,
        "Quantity": quantities,
        "Order Date": order_dates,
        "Store Location": store_locations,
        "Customer Rating": ratings
    })
    
    # Introduce duplicate rows (identical)
    duplicates = df.sample(n=30, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Introduce duplicate Transaction IDs with different data
    dup_ids = df.sample(n=10, random_state=100).copy()
    dup_ids[" Transaction ID "] = df.sample(n=10, random_state=100)[" Transaction ID "].values
    dup_ids["Sale Price"] = "$99.99"
    df = pd.concat([df, dup_ids], ignore_index=True)
    
    # Introduce nulls in transaction ID
    df.loc[df.sample(frac=0.02, random_state=24).index, " Transaction ID "] = np.nan
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Create directories
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df.to_csv(filepath, index=False)
    print(f"Generated messy raw dataset with {len(df)} rows at {filepath}")

if __name__ == "__main__":
    generate_messy_dataset("data/raw_dataset.csv")
