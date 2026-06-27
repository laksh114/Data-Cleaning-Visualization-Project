import numpy as np
import pandas as pd

class DataCleaner:
    """
    DataCleaner class encapsulates the data cleaning pipeline.
    It supports column name normalization, data type conversions, text standardization,
    duplicate row removal, missing value imputation, and IQR-based outlier treatment.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Keep track of all cleaning operations for reporting
        self.logs = {
            "initial_shape": df.shape,
            "missing_before": df.isnull().sum().to_dict(),
            "duplicates_removed": 0,
            "outliers_removed": {},
            "imputations": {},
            "type_conversions": {},
            "text_standardizations": []
        }

    def clean_column_names(self):
        """
        Cleans and standardizes column headers:
        - Strips whitespace
        - Converts to lowercase
        - Replaces spaces with underscores
        - Replaces multiple underscores with a single underscore
        """
        old_cols = list(self.df.columns)
        new_cols = []
        for col in old_cols:
            cleaned = str(col).strip().lower().replace(" ", "_")
            while "__" in cleaned:
                cleaned = cleaned.replace("__", "_")
            new_cols.append(cleaned)
            
        self.df.columns = new_cols
        self.logs["column_name_mapping"] = dict(zip(old_cols, new_cols))

    def remove_duplicates(self) -> int:
        """
        Identifies and removes duplicate rows from the dataset.
        """
        duplicate_count = int(self.df.duplicated().sum())
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        self.logs["duplicates_removed"] = duplicate_count
        return duplicate_count

    def convert_numeric_column(self, col: str, replace_rules: dict = None):
        """
        Parses a column to numeric, removing characters like currency symbols,
        commas, and unit descriptors, then handles custom string mappings.
        """
        if col not in self.df.columns:
            return
            
        initial_nulls = int(self.df[col].isnull().sum())
        
        # Convert to string series for clean text processing
        col_series = self.df[col].astype(str).str.strip()
        
        # Standard cleaning: remove symbols and units
        col_series = col_series.str.replace("$", "", regex=False)
        col_series = col_series.str.replace(",", "", regex=False)
        col_series = col_series.str.replace("USD", "", regex=False, case=False)
        col_series = col_series.str.strip()
        
        # Apply custom mappings (e.g., mapping 'Free' to '0')
        if replace_rules:
            for pattern, val in replace_rules.items():
                if isinstance(val, str):
                    col_series = col_series.str.replace(pattern, val, case=False, regex=False)
                else:
                    # For non-string replacements (like np.nan), match case-insensitively
                    mask = col_series.str.lower() == str(pattern).lower()
                    col_series = col_series.mask(mask, val)
                
        # Force convert to numeric (invalid characters become NaN)
        self.df[col] = pd.to_numeric(col_series, errors="coerce")
        
        new_nulls = int(self.df[col].isnull().sum())
        self.logs["type_conversions"][col] = {
            "to_type": "numeric",
            "coerced_to_nan": new_nulls - initial_nulls
        }

    def convert_date_column(self, col: str):
        """
        Converts a column to datetime format, parsing multiple common date layouts.
        Invalid dates are coerced to NaT.
        """
        if col not in self.df.columns:
            return
            
        initial_nulls = int(self.df[col].isnull().sum())
        
        # Parse to datetime
        self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
        
        new_nulls = int(self.df[col].isnull().sum())
        self.logs["type_conversions"][col] = {
            "to_type": "datetime",
            "coerced_to_nat": new_nulls - initial_nulls
        }

    def standardize_text_column(self, col: str, replacement_map: dict = None):
        """
        Trims whitespace, replaces null-like strings with NaN,
        and standardizes inconsistent labels.
        """
        if col not in self.df.columns:
            return
            
        # Strip whitespace
        self.df[col] = self.df[col].astype(str).str.strip()
        
        # Handle nan-like strings
        null_likes = ["nan", "none", "null", "undefined", "n/a", "?"]
        self.df[col] = self.df[col].apply(lambda x: np.nan if str(x).lower().strip() in null_likes else x)
        
        # Apply custom text corrections/replacements
        if replacement_map:
            # First normalize the keys of the map to simplify lookup
            self.df[col] = self.df[col].apply(
                lambda val: replacement_map.get(str(val).strip(), val) if pd.notnull(val) else val
            )
            
        # Re-strip clean entries
        self.df[col] = self.df[col].apply(lambda val: str(val).strip() if pd.notnull(val) else val)
        self.logs["text_standardizations"].append(col)

    def detect_missing_values(self) -> pd.DataFrame:
        """
        Detects missing values and returns a summary DataFrame.
        """
        missing_count = self.df.isnull().sum()
        missing_pct = (missing_count / len(self.df)) * 100
        summary_df = pd.DataFrame({
            "missing_count": missing_count,
            "missing_percentage": missing_pct
        })
        return summary_df

    def impute_missing_values(self, col: str, strategy: str, fill_value=None):
        """
        Resolves missing values in a column using a selected strategy:
        'mean', 'median', 'mode', 'ffill', 'bfill', 'drop', 'constant'.
        """
        if col not in self.df.columns:
            return
            
        missing_count = int(self.df[col].isnull().sum())
        if missing_count == 0:
            return
            
        imputed_value = None
        
        if strategy == "mean":
            imputed_value = float(self.df[col].mean())
            self.df[col] = self.df[col].fillna(imputed_value)
        elif strategy == "median":
            imputed_value = float(self.df[col].median())
            self.df[col] = self.df[col].fillna(imputed_value)
        elif strategy == "mode":
            imputed_value = self.df[col].mode()[0] if not self.df[col].mode().empty else None
            if imputed_value is not None:
                self.df[col] = self.df[col].fillna(imputed_value)
        elif strategy == "ffill":
            self.df[col] = self.df[col].ffill()
            imputed_value = "Forward Fill"
        elif strategy == "bfill":
            self.df[col] = self.df[col].bfill()
            imputed_value = "Backward Fill"
        elif strategy == "drop":
            self.df = self.df.dropna(subset=[col]).reset_index(drop=True)
            imputed_value = "Dropped Rows"
        elif strategy == "constant" and fill_value is not None:
            self.df[col] = self.df[col].fillna(fill_value)
            imputed_value = fill_value
        else:
            raise ValueError(f"Unknown missing value strategy: '{strategy}'")
            
        self.logs["imputations"][col] = {
            "strategy": strategy,
            "count": missing_count,
            "value_used": str(imputed_value)
        }

    def detect_outliers_iqr(self, col: str) -> tuple:
        """
        Identifies outliers in a numeric column using the Interquartile Range (IQR) method.
        Returns: (lower_bound, upper_bound, outlier_count, indices)
        """
        if col not in self.df.columns:
            return None
            
        series = self.df[col].dropna()
        if series.empty:
            return (0.0, 0.0, 0, [])
            
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = float(q1 - 1.5 * iqr)
        upper_bound = float(q3 + 1.5 * iqr)
        
        outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
        outlier_count = len(outliers)
        outlier_indices = list(outliers.index)
        
        return lower_bound, upper_bound, outlier_count, outlier_indices

    def remove_outliers_iqr(self, col: str) -> int:
        """
        Detects and drops outliers in a numeric column using the IQR method.
        """
        if col not in self.df.columns:
            return 0
            
        res = self.detect_outliers_iqr(col)
        if not res:
            return 0
            
        lower, upper, count, indices = res
        if count == 0:
            return 0
            
        self.df = self.df.drop(index=indices).reset_index(drop=True)
        self.logs["outliers_removed"][col] = {
            "count": count,
            "lower_bound": lower,
            "upper_bound": upper
        }
        return count

    def get_cleaned_data(self) -> pd.DataFrame:
        """
        Finalizes the cleaning, logs the final shape, and returns the DataFrame.
        """
        self.logs["final_shape"] = self.df.shape
        self.logs["missing_after"] = self.df.isnull().sum().to_dict()
        return self.df
