import os
import matplotlib
# Force Agg backend to ensure it runs headless in the background
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class DataVisualizer:
    """
    DataVisualizer handles the generation of exploratory data analysis (EDA) charts
    and compiles a professional, high-resolution infographic dashboard using pure Matplotlib.
    This avoids dependencies on seaborn and scipy which deadlock on Windows in Python 3.14.
    """
    def __init__(self, theme_palette="muted"):
        # Define clean, modern color hex codes
        self.colors = ["#2B2D42", "#4A90E2", "#2ECC71", "#FF6B6B", "#F7B801", "#9B59B6"]
        # Use built-in style to replicate whitegrid look without importing seaborn
        style_name = "seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default"
        plt.style.use(style_name)
        plt.rcParams["font.sans-serif"] = "Arial"
        plt.rcParams["font.family"] = "sans-serif"
        
    def _apply_standard_decorations(self, ax, title, xlabel, ylabel, show_legend=True):
        """
        Applies consistent aesthetic standards to individual plots.
        """
        ax.set_title(title, fontsize=16, fontweight="bold", pad=15, color="#1D1F2A")
        ax.set_xlabel(xlabel, fontsize=13, fontweight="bold", labelpad=8, color="#1D1F2A")
        ax.set_ylabel(ylabel, fontsize=13, fontweight="bold", labelpad=8, color="#1D1F2A")
        ax.tick_params(axis="both", which="major", labelsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        # Despine
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if show_legend:
            legend = ax.get_legend()
            if legend is not None:
                legend.set_frame_on(True)
                legend.get_frame().set_facecolor("white")
                legend.get_frame().set_edgecolor("none")

    def plot_missing_values_bar(self, missing_df: pd.DataFrame, output_path: str):
        """
        Generates and saves a bar chart showing the percentage of missing values per column.
        """
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        ax.bar(
            missing_df.index, 
            missing_df["missing_percentage"], 
            color="#FF6B6B",
            edgecolor="#2B2D42",
            width=0.6
        )
        plt.xticks(rotation=45, ha="right")
        self._apply_standard_decorations(
            ax, 
            "Percentage of Missing Values by Column", 
            "Columns", 
            "Missing Percentage (%)",
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_histogram(self, df: pd.DataFrame, col: str, output_path: str):
        """
        Plots the distribution of a numeric column using a Histogram.
        """
        if col not in df.columns:
            return
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        ax.hist(
            df[col].dropna(), 
            bins=30, 
            color="#4A90E2", 
            edgecolor="#2B2D42", 
            alpha=0.8,
            density=False
        )
        self._apply_standard_decorations(
            ax, 
            f"Distribution of {col.replace('_', ' ').title()}", 
            col.replace("_", " ").title(), 
            "Count",
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_bar_chart(self, df: pd.DataFrame, category_col: str, value_col: str, output_path: str):
        """
        Plots a bar chart showing aggregated values (e.g., mean) across categories.
        """
        if category_col not in df.columns or value_col not in df.columns:
            return
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        
        # Calculate mean for each category
        agg_df = df.groupby(category_col)[value_col].mean().reset_index()
        agg_df = agg_df.sort_values(by=value_col, ascending=False)
        
        colors_list = [plt.cm.Blues(x) for x in np.linspace(0.8, 0.4, len(agg_df))]
        
        ax.bar(
            agg_df[category_col], 
            agg_df[value_col], 
            color=colors_list,
            edgecolor="#2B2D42",
            width=0.6
        )
        plt.xticks(rotation=30, ha="right")
        self._apply_standard_decorations(
            ax, 
            f"Average {value_col.replace('_', ' ').title()} by {category_col.replace('_', ' ').title()}", 
            category_col.replace("_", " ").title(), 
            f"Average {value_col.replace('_', ' ').title()}",
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_line_chart(self, df: pd.DataFrame, date_col: str, value_col: str, output_path: str):
        """
        Plots a temporal line chart representing a metric over time (e.g., sales trend).
        """
        if date_col not in df.columns or value_col not in df.columns:
            return
        plt.figure(figsize=(12, 6))
        ax = plt.subplot(111)
        
        # Aggregate by date
        daily_df = df.groupby(date_col)[value_col].sum().reset_index()
        daily_df = daily_df.sort_values(by=date_col)
        
        ax.plot(
            daily_df[date_col], 
            daily_df[value_col], 
            marker="o", 
            color="#2ECC71", 
            linewidth=2.5,
            markersize=6
        )
        plt.xticks(rotation=30, ha="right")
        self._apply_standard_decorations(
            ax, 
            f"Daily {value_col.replace('_', ' ').title()} Trend", 
            "Date", 
            f"Total {value_col.replace('_', ' ').title()}",
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_pie_chart(self, df: pd.DataFrame, category_col: str, output_path: str):
        """
        Plots a pie chart representing the percentage share of each category.
        """
        if category_col not in df.columns:
            return
        plt.figure(figsize=(8, 8))
        counts = df[category_col].value_counts()
        
        plt.pie(
            counts, 
            labels=counts.index, 
            autopct="%1.1f%%", 
            startangle=140, 
            colors=self.colors[:len(counts)],
            textprops={"fontsize": 12, "fontweight": "bold"},
            wedgeprops={"edgecolor": "white", "linewidth": 2, "alpha": 0.9}
        )
        plt.title(
            f"Distribution of {category_col.replace('_', ' ').title()}", 
            fontsize=16, 
            fontweight="bold", 
            pad=20, 
            color="#1D1F2A"
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_scatter_plot(self, df: pd.DataFrame, col_x: str, col_y: str, output_path: str):
        """
        Plots a scatter plot showing relationship between two numeric columns.
        """
        if col_x not in df.columns or col_y not in df.columns:
            return
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        ax.scatter(
            df[col_x], 
            df[col_y], 
            color="#FF6B6B", 
            alpha=0.7, 
            s=80, 
            edgecolors="#2B2D42",
            linewidths=0.8
        )
        self._apply_standard_decorations(
            ax, 
            f"{col_y.replace('_', ' ').title()} vs {col_x.replace('_', ' ').title()}", 
            col_x.replace("_", " ").title(), 
            col_y.replace("_", " ").title(),
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_box_plot(self, df: pd.DataFrame, category_col: str, value_col: str, output_path: str):
        """
        Plots a box plot comparing numeric distributions across categories.
        """
        if category_col not in df.columns or value_col not in df.columns:
            return
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        
        categories = df[category_col].dropna().unique()
        data_groups = [df[df[category_col] == cat][value_col].dropna() for cat in categories]
        
        bp = ax.boxplot(
            data_groups,
            patch_artist=True,
            medianprops={"color": "#2B2D42", "linewidth": 2}
        )
        ax.set_xticks(np.arange(1, len(categories) + 1))
        ax.set_xticklabels(categories)
        
        # Color each box separately
        for i, box in enumerate(bp['boxes']):
            box.set_facecolor(self.colors[i % len(self.colors)])
            box.set_alpha(0.7)
            
        plt.xticks(rotation=30, ha="right")
        self._apply_standard_decorations(
            ax, 
            f"{value_col.replace('_', ' ').title()} Distribution by {category_col.replace('_', ' ').title()}", 
            category_col.replace("_", " ").title(), 
            value_col.replace("_", " ").title(),
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_count_plot(self, df: pd.DataFrame, category_col: str, output_path: str):
        """
        Plots a bar chart showing frequencies of categorical values.
        """
        if category_col not in df.columns:
            return
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        
        counts = df[category_col].value_counts()
        ax.bar(
            counts.index, 
            counts.values, 
            color=self.colors[:len(counts)],
            edgecolor="#2B2D42",
            width=0.6
        )
        
        plt.xticks(rotation=30, ha="right")
        self._apply_standard_decorations(
            ax, 
            f"Transaction Frequency by {category_col.replace('_', ' ').title()}", 
            category_col.replace("_", " ").title(), 
            "Transaction Count",
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_heatmap(self, df: pd.DataFrame, numeric_cols: list, output_path: str):
        """
        Plots a correlation heatmap for numerical features.
        """
        cols = [c for c in numeric_cols if c in df.columns]
        if len(cols) < 2:
            return
        plt.figure(figsize=(10, 8))
        ax = plt.subplot(111)
        corr = df[cols].corr().values
        
        # Plot using imshow
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        
        # Color bar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.tick_params(labelsize=11)
        
        # Grid/ticks setup
        ax.set_xticks(np.arange(len(cols)))
        ax.set_yticks(np.arange(len(cols)))
        ax.set_xticklabels([c.replace('_', ' ').title() for c in cols], rotation=45, ha="right")
        ax.set_yticklabels([c.replace('_', ' ').title() for c in cols])
        
        # Annotate cell numbers
        for i in range(len(cols)):
            for j in range(len(cols)):
                ax.text(
                    j, i, f"{corr[i, j]:.2f}",
                    ha="center", va="center",
                    color="white" if abs(corr[i, j]) > 0.4 else "black",
                    fontweight="bold", fontsize=12
                )
                
        self._apply_standard_decorations(
            ax, 
            "Correlation Matrix Heatmap", 
            "", 
            "",
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def plot_pair_plot(self, df: pd.DataFrame, numeric_cols: list, output_path: str):
        """
        Plots pairwise relationships in a dataset and saves to output_path.
        """
        cols = [c for c in numeric_cols if c in df.columns]
        n = len(cols)
        if n < 2:
            return
            
        fig, axes = plt.subplots(n, n, figsize=(12, 12))
        for i in range(n):
            for j in range(n):
                ax = axes[i, j]
                if i == j:
                    ax.hist(df[cols[i]].dropna(), color="#4A90E2", edgecolor="#2B2D42", bins=15)
                else:
                    ax.scatter(df[cols[j]], df[cols[i]], color="#FF6B6B", alpha=0.6, s=20)
                
                # Labels & grid
                if i == n - 1:
                    ax.set_xlabel(cols[j].replace('_', ' ').title(), fontsize=11, fontweight="bold")
                if j == 0:
                    ax.set_ylabel(cols[i].replace('_', ' ').title(), fontsize=11, fontweight="bold")
                
                ax.tick_params(labelsize=9)
                ax.grid(True, linestyle="--", alpha=0.3)
                
                # Despine
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

        plt.suptitle("Pairwise Relationships between Numeric Features", y=1.02, fontsize=16, fontweight="bold")
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

    def plot_violin_plot(self, df: pd.DataFrame, category_col: str, value_col: str, output_path: str):
        """
        Plots a violin plot comparing probability distributions of a numeric variable.
        """
        if category_col not in df.columns or value_col not in df.columns:
            return
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        
        categories = df[category_col].dropna().unique()
        data_groups = [df[df[category_col] == cat][value_col].dropna() for cat in categories]
        
        parts = ax.violinplot(data_groups, showmeans=False, showmedians=True)
        
        # Style violins
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(self.colors[i % len(self.colors)])
            pc.set_edgecolor("#2B2D42")
            pc.set_alpha(0.7)
            
        parts['cmedians'].set_color("#2B2D42")
        parts['cmedians'].set_linewidth(2)
        parts['cbars'].set_color("#8D99AE")
        parts['cbars'].set_alpha(0.5)
        parts['cmaxes'].set_color("#8D99AE")
        parts['cmaxes'].set_alpha(0.5)
        parts['cmins'].set_color("#8D99AE")
        parts['cmins'].set_alpha(0.5)
        
        ax.set_xticks(np.arange(1, len(categories) + 1))
        ax.set_xticklabels(categories)
        
        plt.xticks(rotation=30, ha="right")
        self._apply_standard_decorations(
            ax, 
            f"{value_col.replace('_', ' ').title()} Density by {category_col.replace('_', ' ').title()}", 
            category_col.replace("_", " ").title(), 
            value_col.replace("_", " ").title(),
            show_legend=False
        )
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()

    def generate_dashboard(self, df_clean: pd.DataFrame, df_dirty: pd.DataFrame, logs: dict, output_path: str):
        """
        Compiles an executive analytical infographic dashboard summarizing the clean dataset
        metrics, cleaning results, category distributions, trends, correlations, and insights.
        """
        # Set up a grid of subplots on a large canvas
        fig = plt.figure(figsize=(20, 24), facecolor="#F8F9FA")
        gs = fig.add_gridspec(4, 2, height_ratios=[0.4, 1.2, 1.2, 0.8])
        
        # ----------------------------------------------------
        # SUBPLOT 0: Header Banner
        # ----------------------------------------------------
        ax_header = fig.add_subplot(gs[0, :])
        ax_header.axis("off")
        ax_header.set_facecolor("#2B2D42")
        
        rect = plt.Rectangle((0, 0), 1, 1, color="#2B2D42", transform=ax_header.transAxes, zorder=-1)
        ax_header.add_patch(rect)
        
        ax_header.text(
            0.5, 0.6, 
            "DATA CLEANING & ANALYTICS DASHBOARD", 
            color="white", 
            fontsize=28, 
            fontweight="bold", 
            ha="center", 
            va="center"
        )
        ax_header.text(
            0.5, 0.25, 
            "Automated Preprocessing, Exploratory Data Analysis & Business Insights Pipeline (Pure Matplotlib)", 
            color="#A5C4F7", 
            fontsize=14, 
            style="italic", 
            ha="center", 
            va="center"
        )
        
        # ----------------------------------------------------
        # SUBPLOT 1: KPI Cards
        # ----------------------------------------------------
        ax_kpis = fig.add_subplot(gs[1, 0])
        ax_kpis.axis("off")
        ax_kpis.set_title("Data Quality & Cleaning Metrics", fontsize=18, fontweight="bold", pad=15, color="#2B2D42")
        
        total_records_before = logs["initial_shape"][0]
        total_records_after = df_clean.shape[0]
        total_cols = df_clean.shape[1]
        dups_removed = logs.get("duplicates_removed", 0)
        
        outliers_removed = sum(val["count"] for val in logs.get("outliers_removed", {}).values())
        missing_imputed = sum(val["count"] for val in logs.get("imputations", {}).values())
        
        card_positions = [
            (0.05, 0.70, "Total Raw Records", f"{total_records_before}", "#4A90E2"),
            (0.52, 0.70, "Cleaned Records", f"{total_records_after}", "#2ECC71"),
            (0.05, 0.38, "Duplicate Rows Removed", f"{dups_removed}", "#E74C3C"),
            (0.52, 0.38, "Missing Values Resolved", f"{missing_imputed}", "#F1C40F"),
            (0.05, 0.06, "Outlier Records Removed", f"{outliers_removed}", "#E67E22"),
            (0.52, 0.06, "Total Active Columns", f"{total_cols}", "#9B59B6")
        ]
        
        for x, y, title, val, color in card_positions:
            card = plt.Rectangle((x, y), 0.43, 0.26, fill=True, color="white", edgecolor="#D1D5DB", linewidth=1)
            ax_kpis.add_patch(card)
            bar = plt.Rectangle((x, y), 0.015, 0.26, fill=True, color=color)
            ax_kpis.add_patch(bar)
            
            ax_kpis.text(x + 0.04, y + 0.17, title, fontsize=11, color="#7F8C8D", fontweight="bold")
            ax_kpis.text(x + 0.04, y + 0.05, val, fontsize=22, color="#2C3E50", fontweight="bold")

        # ----------------------------------------------------
        # SUBPLOT 2: Product Category Distribution (Pie Chart)
        # ----------------------------------------------------
        ax_pie = fig.add_subplot(gs[1, 1])
        cat_counts = df_clean["product_category"].value_counts()
        ax_pie.pie(
            cat_counts, 
            labels=cat_counts.index, 
            autopct="%1.1f%%", 
            startangle=140, 
            colors=self.colors[:len(cat_counts)],
            textprops={"fontsize": 11, "fontweight": "bold"},
            wedgeprops={"edgecolor": "white", "linewidth": 1.5, "alpha": 0.85}
        )
        ax_pie.set_title("Product Category Distribution", fontsize=18, fontweight="bold", pad=15, color="#2B2D42")

        # ----------------------------------------------------
        # SUBPLOT 3: Sales Trend over Time (Line Chart)
        # ----------------------------------------------------
        ax_line = fig.add_subplot(gs[2, 0])
        daily_sales = df_clean.groupby("order_date")["sale_price"].sum().reset_index()
        daily_sales = daily_sales.sort_values(by="order_date")
        daily_sales["smoothed_sales"] = daily_sales["sale_price"].rolling(window=7, min_periods=1).mean()
        
        ax_line.plot(
            daily_sales["order_date"], 
            daily_sales["smoothed_sales"], 
            color="#4A90E2", 
            linewidth=3
        )
        ax_line.fill_between(daily_sales["order_date"], daily_sales["smoothed_sales"], color="#4A90E2", alpha=0.15)
        self._apply_standard_decorations(
            ax_line, 
            "7-Day Moving Avg Revenue Trend", 
            "Order Date", 
            "Revenue ($)",
            show_legend=False
        )
        ax_line.tick_params(axis='x', rotation=30)

        # ----------------------------------------------------
        # SUBPLOT 4: Correlation Heatmap (Matplotlib imshow)
        # ----------------------------------------------------
        ax_heat = fig.add_subplot(gs[2, 1])
        numeric_cols = ["sale_price", "quantity", "customer_rating"]
        corr = df_clean[numeric_cols].corr().values
        
        im = ax_heat.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax_heat.set_xticks(np.arange(len(numeric_cols)))
        ax_heat.set_yticks(np.arange(len(numeric_cols)))
        ax_heat.set_xticklabels([c.replace('_', ' ').title() for c in numeric_cols], rotation=30, ha="right")
        ax_heat.set_yticklabels([c.replace('_', ' ').title() for c in numeric_cols])
        ax_heat.set_title("Correlation Heatmap", fontsize=18, fontweight="bold", pad=15, color="#2B2D42")
        ax_heat.spines['top'].set_visible(False)
        ax_heat.spines['right'].set_visible(False)
        ax_heat.grid(False)
        
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                ax_heat.text(
                    j, i, f"{corr[i, j]:.2f}",
                    ha="center", va="center",
                    color="white" if abs(corr[i, j]) > 0.4 else "black",
                    fontweight="bold", fontsize=12
                )

        # ----------------------------------------------------
        # SUBPLOT 5: Key Business Insights & Analytical Text Box
        # ----------------------------------------------------
        ax_insights = fig.add_subplot(gs[3, :])
        ax_insights.axis("off")
        
        total_revenue = df_clean["sale_price"].sum()
        avg_rating = df_clean["customer_rating"].mean()
        top_cat = cat_counts.index[0]
        top_cat_revenue = df_clean[df_clean["product_category"] == top_cat]["sale_price"].sum()
        
        rect_insights = plt.Rectangle((0, 0), 1, 1, fill=True, color="#EDF2F7", edgecolor="#E2E8F0", linewidth=1.5)
        ax_insights.add_patch(rect_insights)
        
        ax_insights.text(0.02, 0.88, "Key Business Insights & Data Diagnostics Summary", fontsize=18, fontweight="bold", color="#2B2D42")
        
        bullet_points = [
            f"• Revenue Generation: Total revenue computed is ${total_revenue:,.2f} with an average customer rating of {avg_rating:.2f}/5.0 stars.",
            f"• Market Share: '{top_cat}' is the top-performing category by sales volume ({cat_counts.iloc[0]} units), contributing ${top_cat_revenue:,.2f} in revenue.",
            f"• Data Pipeline Success: Removed {dups_removed} identical/duplicate records, and imputed {missing_imputed} missing fields using column-tailored statistical estimators.",
            f"• Outlier Detection: Outliers in numerical columns (e.g., extremely high prices or quantities) were filtered out using IQR thresholding, saving the model from skew.",
            f"• Structural Alignment: All dates formatted correctly, numeric formats unified, and casing inconsistencies standardized to lower snake_case."
        ]
        
        y_pos = 0.70
        for bp in bullet_points:
            ax_insights.text(0.03, y_pos, bp, fontsize=12, color="#4A5568")
            y_pos -= 0.14
            
        plt.subplots_adjust(hspace=0.45)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Infographic dashboard generated and saved at {output_path}")
