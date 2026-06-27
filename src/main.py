import os
# Set environment variables to limit OpenBLAS threads to 1 and prevent deadlock on import
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import pandas as pd
import numpy as np

# Import modular components
from generate_raw_data import generate_messy_dataset
from load_data import DataLoader
from cleaning import DataCleaner
from visualization import DataVisualizer
from report import ReportGenerator

def main():
    # Define project directories relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "output")
    charts_dir = os.path.join(output_dir, "charts")
    
    # Create directories
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)
    
    raw_csv_path = os.path.join(data_dir, "raw_dataset.csv")
    clean_csv_path = os.path.join(output_dir, "cleaned_dataset.csv")
    report_txt_path = os.path.join(output_dir, "summary_report.txt")
    dashboard_png_path = os.path.join(output_dir, "dashboard.png")
    
    print("========================================================================")
    print("            STARTING DATA CLEANING & VISUALIZATION PIPELINE")
    print("========================================================================")
    
    # 1. Dataset Generation if not exists
    if not os.path.exists(raw_csv_path):
        print(f"Raw dataset not found. Generating a messy mock dataset at: {raw_csv_path}")
        generate_messy_dataset(raw_csv_path, num_rows=1000)
    else:
        print(f"Found existing raw dataset at: {raw_csv_path}")
        
    # 2. Data Loading & Profiling
    print("\n[Step 1] Loading Dataset & Checking Structure...")
    loader = DataLoader(raw_csv_path)
    df_raw = loader.load_data()
    loader.print_summary()
    
    # Save a copy of raw df to analyze missingness later
    df_dirty_copy = df_raw.copy()
    
    # 3. Initialize Cleaning Engine
    print("\n[Step 2] Cleaning & Preprocessing Dataset...")
    cleaner = DataCleaner(df_raw)
    
    # Standardize column headers to snake_case
    cleaner.clean_column_names()
    print("  -> Column headers standardized to snake_case.")
    
    # Correct invalid numerical text strings and convert to float/int
    # Price rules: "Free" -> 0.0, "unknown" -> NaN
    cleaner.convert_numeric_column("sale_price", replace_rules={"Free": "0.0", "unknown": np.nan})
    cleaner.convert_numeric_column("quantity")
    cleaner.convert_numeric_column("customer_rating")
    print("  -> Numerical columns (sale_price, quantity, customer_rating) parsed and cleaned.")
    
    # Parse Date columns
    cleaner.convert_date_column("order_date")
    print("  -> Date columns parsed to datetime.")
    
    # Standardize text/categorical columns
    category_replacements = {
        "electrnics": "Electronics",
        "electronics": "Electronics",
        "ELECTronics": "Electronics",
        "ELECTronics": "Electronics",
        "home & kitchen": "Home & Kitchen",
        "HOME & KITCHEN": "Home & Kitchen",
        "Home": "Home & Kitchen",
        "clothing": "Clothing",
        "CLOTHing": "Clothing",
        "Clothes": "Clothing",
        "books": "Books",
        "books": "Books",
        "Bks": "Books"
    }
    location_replacements = {
        "new york": "New York",
        "NEW YORK": "New York",
        "chicago": "Chicago",
        "CHICAGO": "Chicago",
        "los angeles": "Los Angeles",
        "LOS ANGELES": "Los Angeles",
        "houston": "Houston",
        "HOUSTON": "Houston"
    }
    cleaner.standardize_text_column("customer_name")
    cleaner.standardize_text_column("product_category", replacement_map=category_replacements)
    cleaner.standardize_text_column("store_location", replacement_map=location_replacements)
    print("  -> Text columns (customer_name, product_category, store_location) standardized.")
    
    # Duplicate Removal
    dups = cleaner.remove_duplicates()
    print(f"  -> Duplicate rows detected and removed: {dups}")
    
    # Save missing value metrics before imputations for visual charts
    missing_report = cleaner.detect_missing_values()
    
    # Impute missing values based on feature characteristics
    # Key identifiers: drop row if transaction_id is missing
    cleaner.impute_missing_values("transaction_id", strategy="drop")
    # Impute categorical text columns
    cleaner.impute_missing_values("customer_id", strategy="constant", fill_value="C-Unknown")
    cleaner.impute_missing_values("customer_name", strategy="constant", fill_value="Unknown Customer")
    cleaner.impute_missing_values("product_category", strategy="mode")
    cleaner.impute_missing_values("store_location", strategy="mode")
    # Impute numerical columns
    cleaner.impute_missing_values("sale_price", strategy="median")
    cleaner.impute_missing_values("quantity", strategy="median")
    cleaner.impute_missing_values("customer_rating", strategy="mean")
    # Impute date column
    cleaner.impute_missing_values("order_date", strategy="ffill")
    print("  -> Missing values resolved using customized imputation strategies.")
    
    # Treat outliers in numeric columns using the IQR method
    # Also clean logical bounds: rating should be in [1.0, 5.0], quantity and price should be positive
    # Filter rating outliers first
    rating_outliers = cleaner.remove_outliers_iqr("customer_rating")
    price_outliers = cleaner.remove_outliers_iqr("sale_price")
    qty_outliers = cleaner.remove_outliers_iqr("quantity")
    print(f"  -> Outliers treated via IQR method:")
    print(f"     * customer_rating: {rating_outliers} outliers removed.")
    print(f"     * sale_price: {price_outliers} outliers removed.")
    print(f"     * quantity: {qty_outliers} outliers removed.")
    
    # Ensure remaining logical bounds
    cleaner.df = cleaner.df[cleaner.df["quantity"] > 0].reset_index(drop=True)
    cleaner.df = cleaner.df[cleaner.df["sale_price"] >= 0].reset_index(drop=True)
    cleaner.df = cleaner.df[(cleaner.df["customer_rating"] >= 1.0) & (cleaner.df["customer_rating"] <= 5.0)].reset_index(drop=True)
    
    # Round quantity to integer
    cleaner.df["quantity"] = cleaner.df["quantity"].astype(int)
    
    # Finalize dataset
    df_clean = cleaner.get_cleaned_data()
    print(f"  -> Data cleaning finished. Final dimensions: {df_clean.shape}")
    
    # 4. Generate Visualizations
    print("\n[Step 3] Generating Visualizations...")
    visualizer = DataVisualizer()
    
    # Save individual charts
    visualizer.plot_missing_values_bar(missing_report, os.path.join(charts_dir, "missing_values.png"))
    visualizer.plot_histogram(df_clean, "sale_price", os.path.join(charts_dir, "price_distribution.png"))
    visualizer.plot_bar_chart(df_clean, "product_category", "sale_price", os.path.join(charts_dir, "avg_price_by_category.png"))
    visualizer.plot_line_chart(df_clean, "order_date", "sale_price", os.path.join(charts_dir, "sales_trend.png"))
    visualizer.plot_pie_chart(df_clean, "product_category", os.path.join(charts_dir, "category_distribution.png"))
    visualizer.plot_scatter_plot(df_clean, "customer_rating", "sale_price", os.path.join(charts_dir, "price_vs_rating.png"))
    visualizer.plot_box_plot(df_clean, "product_category", "sale_price", os.path.join(charts_dir, "price_box_plot.png"))
    visualizer.plot_count_plot(df_clean, "store_location", os.path.join(charts_dir, "transactions_by_location.png"))
    
    # Correlation heatmaps
    numeric_cols = ["sale_price", "quantity", "customer_rating"]
    visualizer.plot_heatmap(df_clean, numeric_cols, os.path.join(charts_dir, "correlation_heatmap.png"))
    visualizer.plot_pair_plot(df_clean, numeric_cols, os.path.join(charts_dir, "pair_plot.png"))
    visualizer.plot_violin_plot(df_clean, "product_category", "customer_rating", os.path.join(charts_dir, "rating_violin_plot.png"))
    
    print(f"  -> All 11 individual charts saved to {charts_dir}")
    
    # Generate unified executive dashboard
    print("\n[Step 4] Compiling Executive Dashboard Infographic...")
    visualizer.generate_dashboard(df_clean, df_dirty_copy, cleaner.logs, dashboard_png_path)
    
    # 5. Export cleaned dataset
    print("\n[Step 5] Exporting Cleaned CSV...")
    df_clean.to_csv(clean_csv_path, index=False)
    print(f"  -> Cleaned dataset exported to: {clean_csv_path}")
    
    # 6. Export Summary Report
    print("\n[Step 6] Compiling Analytical Summary Report...")
    reporter = ReportGenerator(df_clean, cleaner.logs)
    reporter.save_report(report_txt_path)
    
    print("\n========================================================================")
    print("             PIPELINE COMPLETE - ALL ARTIFACTS EXPORTED")
    print("========================================================================")

if __name__ == "__main__":
    main()
