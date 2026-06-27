import io
import pandas as pd

class DataLoader:
    """
    DataLoader class to handle loading of CSV datasets and extracting 
    basic structural metadata (dimensions, types, head/tail, summary stats).
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Loads the CSV file into a Pandas DataFrame.
        """
        try:
            self.df = pd.read_csv(self.filepath)
            return self.df
        except Exception as e:
            raise IOError(f"Error loading CSV file from {self.filepath}: {e}")
            
    def get_summary_info(self) -> dict:
        """
        Extracts structural and statistical summaries of the loaded dataset.
        """
        if self.df is None:
            raise ValueError("Data not loaded yet. Call load_data() first.")
            
        # Capture standard df.info() output into a string buffer
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        summary = {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "memory_usage_bytes": int(self.df.memory_usage(deep=True).sum()),
            "head": self.df.head(5),
            "tail": self.df.tail(5),
            "describe": self.df.describe(include="all"),
            "info_str": info_str
        }
        return summary
        
    def print_summary(self):
        """
        Prints the dataset profile directly to console.
        """
        if self.df is None:
            print("No dataset loaded.")
            return
            
        summary = self.get_summary_info()
        print("=" * 70)
        print(f"DATASET LOADED FROM: {self.filepath}")
        print("=" * 70)
        print(f"Dimensions: {summary['shape'][0]} rows, {summary['shape'][1]} columns")
        print(f"Memory Footprint: {summary['memory_usage_bytes'] / 1024:.2f} KB")
        print("-" * 70)
        print("Columns and Data Types:")
        for col, dtype in summary['dtypes'].items():
            print(f"  - {col}: {dtype}")
        print("-" * 70)
        print("First 5 Rows:")
        print(summary['head'].to_string())
        print("-" * 70)
        print("Last 5 Rows:")
        print(summary['tail'].to_string())
        print("-" * 70)
        print("Statistical Summary:")
        print(summary['describe'].to_string())
        print("=" * 70)
