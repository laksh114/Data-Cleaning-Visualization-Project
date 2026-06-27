import os
import pandas as pd

class ReportGenerator:
    """
    ReportGenerator compiles dataset profiling statistics, cleaning pipeline histories,
    and business insights into a structured analysis report.
    """
    def __init__(self, df_clean: pd.DataFrame, logs: dict):
        self.df_clean = df_clean
        self.logs = logs

    def generate_report_text(self) -> str:
        """
        Creates the text layout of the summary report.
        """
        total_before = self.logs["initial_shape"][0]
        total_after = self.df_clean.shape[0]
        cols_count = self.df_clean.shape[1]
        dups_removed = self.logs.get("duplicates_removed", 0)
        
        # Missing values
        missing_before = self.logs.get("missing_before", {})
        imputations = self.logs.get("imputations", {})
        
        # Outliers
        outliers = self.logs.get("outliers_removed", {})
        
        # Key metrics
        total_revenue = self.df_clean["sale_price"].sum() if "sale_price" in self.df_clean.columns else 0.0
        avg_price = self.df_clean["sale_price"].mean() if "sale_price" in self.df_clean.columns else 0.0
        avg_rating = self.df_clean["customer_rating"].mean() if "customer_rating" in self.df_clean.columns else 0.0
        total_qty = self.df_clean["quantity"].sum() if "quantity" in self.df_clean.columns else 0
        
        # Category distribution
        cat_dist = ""
        top_cat = "N/A"
        counts = pd.Series(dtype=int)
        if "product_category" in self.df_clean.columns:
            counts = self.df_clean["product_category"].value_counts()
            pcts = self.df_clean["product_category"].value_counts(normalize=True) * 100
            if not counts.empty:
                top_cat = counts.index[0]
            for cat, cnt in counts.items():
                cat_dist += f"  - {cat}: {cnt} items ({pcts[cat]:.2f}%)\n"
                
        # Location distribution
        loc_dist = ""
        if "store_location" in self.df_clean.columns:
            counts = self.df_clean["store_location"].value_counts()
            pcts = self.df_clean["store_location"].value_counts(normalize=True) * 100
            for loc, cnt in counts.items():
                loc_dist += f"  - {loc}: {cnt} transactions ({pcts[loc]:.2f}%)\n"
                
        # Assemble sections
        report = "=" * 80 + "\n"
        report += "               DATA CLEANING & ANALYTICAL PIPELINE REPORT\n"
        report += "=" * 80 + "\n\n"
        
        report += "1. EXECUTIVE SUMMARY\n"
        report += "-" * 30 + "\n"
        report += "This report summarizes the data cleaning operations, preprocessing steps,\n"
        report += "and exploratory data analysis (EDA) executed on the raw dataset. The pipeline\n"
        report += "identified and handled raw data-entry defects, missing values, duplicates,\n"
        report += "and extreme outliers to build a high-integrity cleaned dataset for analysis.\n\n"
        report += f"  - Raw Dataset Dimensions: {self.logs['initial_shape'][0]} rows, {self.logs['initial_shape'][1]} columns\n"
        report += f"  - Cleaned Dataset Dimensions: {total_after} rows, {cols_count} columns\n"
        report += f"  - Data Retention Rate: {(total_after / total_before) * 100:.2f}%\n"
        report += f"  - Duplicate Records Removed: {dups_removed}\n"
        report += f"  - Total Missing Values Imputed: {sum(x['count'] for x in imputations.values())}\n"
        report += f"  - Total Outliers Removed: {sum(x['count'] for x in outliers.values())}\n\n"
        
        report += "2. COLUMN NAME STANDARDIZATION\n"
        report += "-" * 30 + "\n"
        report += "All column headers were cleaned, trimmed, lowercased, and mapped to snake_case:\n"
        for old_col, new_col in self.logs.get("column_name_mapping", {}).items():
            report += f"  - '{old_col}' -> '{new_col}'\n"
        report += "\n"
        
        report += "3. TYPE CONVERSIONS & DATA PARSING\n"
        report += "-" * 30 + "\n"
        report += "Parsed raw string inputs into unified numeric and temporal formats:\n"
        for col, details in self.logs.get("type_conversions", {}).items():
            report += f"  - Column '{col}' successfully parsed to {details['to_type']}.\n"
            if details["to_type"] == "numeric" and details["coerced_to_nan"] > 0:
                report += f"    * {details['coerced_to_nan']} invalid string values (e.g., text) coerced to NaN.\n"
            elif details["to_type"] == "datetime" and details["coerced_to_nat"] > 0:
                report += f"    * {details['coerced_to_nat']} invalid date entries coerced to NaT.\n"
        report += "\n"
        
        report += "4. MISSING VALUES DIAGNOSTICS & RESOLUTION\n"
        report += "-" * 30 + "\n"
        report += "Missing values were identified and resolved based on custom column-specific strategies:\n\n"
        report += f"{'Column Name':<22} | {'Nulls Before':<12} | {'Imputation Strategy':<22} | {'Value Used / Method':<22}\n"
        report += "-" * 88 + "\n"
        for col in self.df_clean.columns:
            before_cnt = missing_before.get(col, 0)
            imp_details = imputations.get(col)
            if imp_details:
                strat = imp_details["strategy"]
                val = imp_details["value_used"]
            else:
                strat = "None (0 missing)" if before_cnt == 0 else "N/A"
                val = "-"
            report += f"{col:<22} | {before_cnt:<12} | {strat:<22} | {val:<22}\n"
        report += "\n"
        
        report += "5. OUTLIER ANALYSIS (IQR METHOD)\n"
        report += "-" * 30 + "\n"
        report += "Applied the Interquartile Range (IQR) technique to detect and prune extreme values:\n\n"
        if not outliers:
            report += "  - No outliers detected or removed.\n"
        else:
            for col, details in outliers.items():
                report += f"  - Column '{col}':\n"
                report += f"    * Lower Boundary Threshold: {details['lower_bound']:.2f}\n"
                report += f"    * Upper Boundary Threshold: {details['upper_bound']:.2f}\n"
                report += f"    * Outliers Removed: {details['count']} records\n"
        report += "\n"
        
        report += "6. EXPLORATORY DATA ANALYSIS SUMMARY\n"
        report += "-" * 30 + "\n"
        report += "Summary Statistics for the cleaned sales transactions:\n"
        report += f"  - Total Clean Transactions: {total_after}\n"
        report += f"  - Cumulative Sales Revenue: ${total_revenue:,.2f}\n"
        report += f"  - Average Transaction Price: ${avg_price:.2f}\n"
        report += f"  - Total Product Quantities Sold: {total_qty}\n"
        report += f"  - Average Customer Satisfaction: {avg_rating:.2f}/5.0 stars\n\n"
        
        report += "Distribution of Product Categories:\n"
        report += cat_dist + "\n"
        
        report += "Distribution of Store Locations:\n"
        report += loc_dist + "\n"
        
        report += "7. KEY BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS\n"
        report += "-" * 30 + "\n"
        report += f"1. CORE PRODUCT STRATEGY: '{top_cat}' is the highest-volume product category (representing {counts.iloc[0] if 'product_category' in self.df_clean.columns and not counts.empty else 0} units).\n"
        report += "   Focus inventory allocations and marketing budgets to support demand in this segment.\n"
        report += f"2. REVENUE FOUNDATION: Total revenue reached ${total_revenue:,.2f} with an average transaction value of ${avg_price:.2f}.\n"
        report += "   The removal of test inputs (e.g. $99,999.00 values) provides a reliable baseline for budget planning.\n"
        report += f"3. CUSTOMER SATISFACTION: The average customer score stands at {avg_rating:.2f}/5.0. Targeted satisfaction\n"
        report += "   campaigns in categories showing rating variability should be pursued.\n"
        report += "4. GEOGRAPHICAL DISPERSION: Transaction densities across cities highlight top-performing regional clusters,\n"
        report += "   informing distribution network and advertising optimizations.\n\n"
        
        report += "=" * 80 + "\n"
        report += "                           END OF SUMMARY REPORT\n"
        report += "=" * 80 + "\n"
        
        return report

    def save_report(self, output_path: str):
        """
        Saves the structured analytical report to the specified file path.
        """
        try:
            content = self.generate_report_text()
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Report written to {output_path}")
        except Exception as e:
            raise IOError(f"Failed to write summary report to {output_path}: {e}")
