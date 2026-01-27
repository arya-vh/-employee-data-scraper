import requests
import pandas as pd
import json
import time
import sys
import argparse
from typing import Dict, List

try:
    import streamlit as st
except ImportError:
    st = None

def scrape_employees(url: str, max_retries: int = 3) -> pd.DataFrame:
    """Fetch and normalize employee data with error handling."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            
            # Data Normalization
            # 1. Designation based on years_of_experience
            def get_designation(exp: int) -> str:
                if exp < 3:
                    return "System Engineer"
                elif 3 <= exp < 5:
                    return "Data Engineer"
                elif 5 <= exp < 10:
                    return "Senior Data Engineer"
                else:
                    return "Lead"
            
            df['designation'] = df['years_of_experience'].apply(get_designation)
            
            # 2. Full name
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
            
            # 3. Phone validation - convert invalid numbers (containing 'x') to NaN
            df['phone_clean'] = pd.to_numeric(df['phone'].apply(lambda p: None if 'x' in str(p).lower() else p), errors='coerce').astype('Int64')
            
            # 4. Data types (string/int as specified)
            df['full_name'] = df['full_name'].astype(str)
            df['email'] = df['email'].astype(str)
            df['gender'] = df['gender'].astype(str)
            df['job_title'] = df['job_title'].astype(str)
            df['department'] = df['department'].astype(str)
            df['age'] = df['age'].astype(int)
            df['years_of_experience'] = df['years_of_experience'].astype(int)
            df['salary'] = df['salary'].astype(int)
            
            return df[['full_name', 'email', 'phone_clean', 'gender', 'age', 'job_title', 
                       'years_of_experience', 'salary', 'department', 'designation']]
        
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    
    
    raise ValueError("Failed to fetch data after retries")


def dynamic_cli_query(df: pd.DataFrame, rows: int = 5, filters: Dict = None, columns: List = None) -> None:
    """
    Dynamic CLI Query System for employee data with flexible filtering and display.
    
    Args:
        df: DataFrame to query
        rows: Number of rows to display (default 5, can be overridden via CLI)
        filters: Dictionary of column:value pairs for filtering
        columns: List of specific columns to display (default: all)
    """
    result_df = df.copy()
    
    # Apply filters if provided
    if filters:
        for col, value in filters.items():
            if col in result_df.columns:
                result_df = result_df[result_df[col] == value]
    
    # Select specific columns if provided
    if columns:
        cols_to_show = [c for c in columns if c in result_df.columns]
        result_df = result_df[cols_to_show]
    
    # Display results
    print(f"\n{'='*80}")
    print(f"Query Results: Displaying {min(rows, len(result_df))} of {len(result_df)} rows")
    print(f"{'='*80}\n")
    print(result_df.head(rows).to_string())
    print(f"\n{'='*80}\n")


def launch_pygwalker_ui(df: pd.DataFrame) -> None:
    """
    Launch Streamlit interactive BI dashboard.
    Drag & drop style visualization (no code needed).
    
    Args:
        df: DataFrame to explore
    """
    if st is None:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
        return
    
    st.set_page_config(page_title="Employee Analytics", layout="wide")
    st.title("📊 Employee Analytics Dashboard")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    selected_department = st.sidebar.multiselect("Department", df['department'].unique(), default=df['department'].unique())
    selected_designation = st.sidebar.multiselect("Designation", df['designation'].unique(), default=df['designation'].unique())
    selected_gender = st.sidebar.multiselect("Gender", df['gender'].unique(), default=df['gender'].unique())
    
    # Apply filters
    filtered_df = df[
        (df['department'].isin(selected_department)) &
        (df['designation'].isin(selected_designation)) &
        (df['gender'].isin(selected_gender))
    ]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Employees", len(filtered_df))
    col2.metric("Avg Salary", f"${filtered_df['salary'].mean():,.0f}")
    col3.metric("Avg Age", f"{filtered_df['age'].mean():.1f}")
    col4.metric("Avg Experience", f"{filtered_df['years_of_experience'].mean():.1f} years")
    
    # Charts using native Streamlit
    st.subheader("📈 Salary by Department")
    salary_by_dept = filtered_df.groupby('department')['salary'].mean().sort_values(ascending=False)
    st.bar_chart(salary_by_dept)
    
    st.subheader("👥 Employee Distribution")
    col1, col2 = st.columns(2)
    with col1:
        dept_count = filtered_df['department'].value_counts()
        st.write("By Department")
        st.bar_chart(dept_count)
    with col2:
        desig_count = filtered_df['designation'].value_counts()
        st.write("By Designation")
        st.bar_chart(desig_count)
    
    st.subheader("📊 Experience vs Salary")
    scatter_data = filtered_df[['years_of_experience', 'salary']].rename(
        columns={'years_of_experience': 'Experience', 'salary': 'Salary'}
    )
    st.scatter_chart(scatter_data)
    
    # Data Table
    st.subheader("📋 Employee Data")
    st.dataframe(filtered_df, use_container_width=True)


# Usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dynamic Employee Data Query System")
    parser.add_argument("--rows", type=int, default=5, help="Number of rows to display (default: 5)")
    parser.add_argument("--department", type=str, help="Filter by department")
    parser.add_argument("--designation", type=str, help="Filter by designation")
    parser.add_argument("--gender", type=str, help="Filter by gender")
    parser.add_argument("--columns", nargs="+", help="Specific columns to display")
    parser.add_argument("--all", action="store_true", help="Display all rows")
    parser.add_argument("--ui", action="store_true", help="Launch PyGWalker interactive BI dashboard")
    
    args = parser.parse_args()
    
    url = "https://api.slingacademy.com/v1/sample-data/files/employees.json"
    df_normalized = scrape_employees(url)
    df_normalized.to_csv('employees_normalized.csv', index=False)
    
    # Launch Streamlit dashboard if requested
    if args.ui:
        launch_pygwalker_ui(df_normalized)
    else:
        # Build filters from arguments
        filters = {}
        if args.department:
            filters['department'] = args.department
        if args.designation:
            filters['designation'] = args.designation
        if args.gender:
            filters['gender'] = args.gender
        
        # Determine rows to display
        rows_to_show = len(df_normalized) if args.all else args.rows
        
        # Execute dynamic query
        dynamic_cli_query(df_normalized, rows=rows_to_show, filters=filters, columns=args.columns)
