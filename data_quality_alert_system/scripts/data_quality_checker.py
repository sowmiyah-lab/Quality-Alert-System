"""
Data Quality Alert System

This script checks data quality between source and target databases by validating:
1. Row count differences
2. Null values in key columns
3. Duplicate primary keys

It generates a simple report with pass/fail status.
"""

import logging
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3  # Using SQLite for demonstration; can be replaced with SQLAlchemy for other DBs

# Get the base directory (where the script is located)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
log_file = os.path.join(LOGS_DIR, 'data_quality.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataQualityChecker:
    def __init__(self, source_db_path: str, target_db_path: str):
        """
        Initialize the Data Quality Checker.
        
        Args:
            source_db_path: Path to the source database file.
            target_db_path: Path to the target database file.
        """
        self.source_db_path = source_db_path
        self.target_db_path = target_db_path
        self.results: List[Dict[str, Any]] = []

    def _get_connection(self, db_path: str) -> sqlite3.Connection:
        """Create a database connection."""
        try:
            conn = sqlite3.connect(db_path)
            logger.info(f"Connected to database: {db_path}")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to {db_path}: {e}")
            raise

    def check_row_count(self, table_name: str) -> Dict[str, Any]:
        """
        Check if row counts match between source and target tables.
        
        Args:
            table_name: Name of the table to check.
            
        Returns:
            Dictionary containing the check results.
        """
        result = {
            'check_type': 'Row Count',
            'table_name': table_name,
            'status': 'PASS',
            'details': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            source_conn = self._get_connection(self.source_db_path)
            target_conn = self._get_connection(self.target_db_path)
            
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            source_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            source_count = source_cursor.fetchone()[0]
            
            target_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            target_count = target_cursor.fetchone()[0]
            
            source_conn.close()
            target_conn.close()
            
            if source_count == target_count:
                result['details'] = f"Source: {source_count}, Target: {target_count} (Match)"
                logger.info(f"Row count check PASSED for {table_name}: {source_count} rows")
            else:
                result['status'] = 'FAIL'
                result['details'] = f"Source: {source_count}, Target: {target_count} (Mismatch: {abs(source_count - target_count)})"
                logger.warning(f"Row count check FAILED for {table_name}: Source={source_count}, Target={target_count}")
                
        except Exception as e:
            result['status'] = 'ERROR'
            result['details'] = str(e)
            logger.error(f"Row count check ERROR for {table_name}: {e}")
            
        self.results.append(result)
        return result

    def check_nulls_in_key_columns(self, table_name: str, key_columns: List[str]) -> Dict[str, Any]:
        """
        Check for null values in specified key columns.
        
        Args:
            table_name: Name of the table to check.
            key_columns: List of column names that should not contain nulls.
            
        Returns:
            Dictionary containing the check results.
        """
        result = {
            'check_type': 'Null Check',
            'table_name': table_name,
            'columns_checked': key_columns,
            'status': 'PASS',
            'details': '',
            'timestamp': datetime.now().isoformat()
        }
        
        null_issues = []
        
        try:
            # Check both source and target
            for db_path, db_name in [(self.source_db_path, 'Source'), (self.target_db_path, 'Target')]:
                conn = self._get_connection(db_path)
                cursor = conn.cursor()
                
                for column in key_columns:
                    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column} IS NULL"
                    cursor.execute(query)
                    null_count = cursor.fetchone()[0]
                    
                    if null_count > 0:
                        null_issues.append(f"{db_name} {table_name}.{column}: {null_count} nulls found")
                        result['status'] = 'FAIL'
                        
                conn.close()
                
            if result['status'] == 'PASS':
                result['details'] = "No nulls found in key columns"
                logger.info(f"Null check PASSED for {table_name} columns: {key_columns}")
            else:
                result['details'] = "; ".join(null_issues)
                logger.warning(f"Null check FAILED for {table_name}: {result['details']}")
                
        except Exception as e:
            result['status'] = 'ERROR'
            result['details'] = str(e)
            logger.error(f"Null check ERROR for {table_name}: {e}")
            
        self.results.append(result)
        return result

    def check_duplicate_primary_keys(self, table_name: str, pk_column: str) -> Dict[str, Any]:
        """
        Check for duplicate primary key values.
        
        Args:
            table_name: Name of the table to check.
            pk_column: Name of the primary key column.
            
        Returns:
            Dictionary containing the check results.
        """
        result = {
            'check_type': 'Duplicate PK Check',
            'table_name': table_name,
            'pk_column': pk_column,
            'status': 'PASS',
            'details': '',
            'timestamp': datetime.now().isoformat()
        }
        
        duplicate_issues = []
        
        try:
            for db_path, db_name in [(self.source_db_path, 'Source'), (self.target_db_path, 'Target')]:
                conn = self._get_connection(db_path)
                cursor = conn.cursor()
                
                query = f"""
                    SELECT {pk_column}, COUNT(*) 
                    FROM {table_name} 
                    GROUP BY {pk_column} 
                    HAVING COUNT(*) > 1
                """
                cursor.execute(query)
                duplicates = cursor.fetchall()
                
                if duplicates:
                    duplicate_issues.append(f"{db_name} {table_name}.{pk_column}: {len(duplicates)} duplicate keys found")
                    result['status'] = 'FAIL'
                    
                conn.close()
                
            if result['status'] == 'PASS':
                result['details'] = "No duplicate primary keys found"
                logger.info(f"Duplicate PK check PASSED for {table_name}.{pk_column}")
            else:
                result['details'] = "; ".join(duplicate_issues)
                logger.warning(f"Duplicate PK check FAILED for {table_name}.{pk_column}: {result['details']}")
                
        except Exception as e:
            result['status'] = 'ERROR'
            result['details'] = str(e)
            logger.error(f"Duplicate PK check ERROR for {table_name}.{pk_column}: {e}")
            
        self.results.append(result)
        return result

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a report of all check results.
        
        Args:
            output_file: Optional path to save the report as CSV. If None, returns console output.
            
        Returns:
            Report content as string.
        """
        if not self.results:
            message = "No checks have been performed yet."
            logger.info(message)
            return message
        
        # Console output
        console_output = "\n" + "="*80 + "\n"
        console_output += "DATA QUALITY ALERT SYSTEM REPORT\n"
        console_output += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        console_output += "="*80 + "\n\n"
        
        pass_count = sum(1 for r in self.results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.results if r['status'] == 'FAIL')
        error_count = sum(1 for r in self.results if r['status'] == 'ERROR')
        
        console_output += f"SUMMARY: {pass_count} PASSED, {fail_count} FAILED, {error_count} ERRORS\n\n"
        console_output += "-"*80 + "\n"
        
        for i, result in enumerate(self.results, 1):
            console_output += f"\nCheck #{i}: {result['check_type']}\n"
            console_output += f"  Table: {result['table_name']}\n"
            console_output += f"  Status: [{result['status']}]\n"
            
            if 'columns_checked' in result:
                console_output += f"  Columns: {result['columns_checked']}\n"
            elif 'pk_column' in result:
                console_output += f"  PK Column: {result['pk_column']}\n"
                
            console_output += f"  Details: {result['details']}\n"
            console_output += f"  Timestamp: {result['timestamp']}\n"
            console_output += "-"*80 + "\n"
        
        # Save to CSV if requested
        if output_file:
            try:
                with open(output_file, 'w', newline='') as csvfile:
                    fieldnames = ['check_type', 'table_name', 'status', 'details', 'timestamp']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                    
                    writer.writeheader()
                    for result in self.results:
                        writer.writerow(result)
                
                logger.info(f"Report saved to {output_file}")
                console_output += f"\nReport saved to: {output_file}\n"
                
            except Exception as e:
                logger.error(f"Failed to save report to {output_file}: {e}")
                console_output += f"\nFailed to save report: {e}\n"
        
        return console_output


def setup_sample_databases():
    """Create sample source and target databases for testing."""
    logger.info("Setting up sample databases...")
    
    source_db_path = os.path.join(DATA_DIR, 'source.db')
    target_db_path = os.path.join(DATA_DIR, 'target.db')
    
    # Create source database
    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()
    
    source_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            created_at TEXT
        )
    ''')
    
    # Insert sample data into source
    sample_data = [
        (1, 'Alice', 'alice@example.com', '2024-01-01'),
        (2, 'Bob', 'bob@example.com', '2024-01-02'),
        (3, 'Charlie', 'charlie@example.com', '2024-01-03'),
        (4, 'Diana', 'diana@example.com', '2024-01-04'),
        (5, 'Eve', 'eve@example.com', '2024-01-05')
    ]
    
    source_cursor.executemany('INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)', sample_data)
    source_conn.commit()
    source_conn.close()
    
    # Create target database with some issues for testing
    target_conn = sqlite3.connect(target_db_path)
    target_cursor = target_conn.cursor()
    
    # Drop table first to ensure clean state for duplicate insertion
    target_cursor.execute('DROP TABLE IF EXISTS users')
    
    target_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER,
            name TEXT,
            email TEXT,
            created_at TEXT
        )
    ''')
    
    # Insert data with issues: missing row, null in key column, duplicate
    # Using separate inserts to allow duplicate IDs (no PRIMARY KEY constraint)
    target_data = [
        (1, 'Alice', 'alice@example.com', '2024-01-01'),
        (2, 'Bob', None, '2024-01-02'),  # Null in email
        (3, 'Charlie', 'charlie@example.com', '2024-01-03'),
        (4, 'Diana', 'diana@example.com', '2024-01-04'),
        (4, 'Diana Duplicate', 'diana.dup@example.com', '2024-01-06')  # Duplicate ID
        # Missing ID 5
    ]
    
    target_cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', target_data)
    target_conn.commit()
    target_conn.close()
    
    logger.info(f"Sample databases created successfully in {DATA_DIR}")


def main():
    """Main function to run the data quality checks."""
    print("\n" + "="*60)
    print("DATA QUALITY ALERT SYSTEM")
    print("="*60 + "\n")
    
    # Setup sample databases for demonstration
    setup_sample_databases()
    
    # Define database paths
    source_db = os.path.join(DATA_DIR, 'source.db')
    target_db = os.path.join(DATA_DIR, 'target.db')
    
    # Initialize checker
    checker = DataQualityChecker(source_db, target_db)
    
    # Run checks
    print("Running Data Quality Checks...\n")
    
    # 1. Check row count
    checker.check_row_count('users')
    
    # 2. Check for nulls in key columns (email should not be null)
    checker.check_nulls_in_key_columns('users', ['email'])
    
    # 3. Check for duplicate primary keys
    checker.check_duplicate_primary_keys('users', 'id')
    
    # Generate and display report
    report_file = os.path.join(OUTPUT_DIR, 'data_quality_report.csv')
    report = checker.generate_report(report_file)
    print(report)
    
    print("\nData quality checks completed!")
    print(f"Log file: {os.path.join(LOGS_DIR, 'data_quality.log')}")
    print(f"CSV Report: {report_file}")


if __name__ == "__main__":
    main()
