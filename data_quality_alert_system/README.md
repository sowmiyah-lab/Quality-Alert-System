# Data Quality Alert System

A Python-based data quality validation tool that checks data integrity between source and target databases.

## Project Structure

```
data_quality_alert_system/
├── README.md                 # This file
├── scripts/
│   └── data_quality_checker.py  # Main script with all validation logic
├── data/                     # Database files (auto-generated)
│   ├── source.db             # Source database
│   └── target.db             # Target database
├── output/                   # Generated reports (auto-generated)
│   └── data_quality_report.csv
└── logs/                     # Log files (auto-generated)
    └── data_quality.log
```

## Features

This script performs three key data quality checks:

1. **Row Count Check**: Compares the number of rows between source and target tables
2. **Null Check**: Validates that key columns don't contain NULL values
3. **Duplicate Primary Key Check**: Ensures no duplicate primary keys exist

## Requirements

- Python 3.6+
- No external dependencies (uses built-in `sqlite3`, `logging`, and `csv` modules)

## Usage

### Run the Data Quality Checker

```bash
cd data_quality_alert_system
python scripts/data_quality_checker.py
```

### What Happens When You Run It

1. Sample databases are created in the `data/` directory with demo data
2. Three data quality checks are performed:
   - Row count comparison
   - Null value detection in key columns
   - Duplicate primary key detection
3. Results are displayed in the console
4. A CSV report is saved to `output/data_quality_report.csv`
5. Detailed logs are written to `logs/data_quality.log`

## Sample Output

```
================================================================================
DATA QUALITY ALERT SYSTEM REPORT
Generated at: 2026-06-04 19:45:40
================================================================================

SUMMARY: 1 PASSED, 2 FAILED, 0 ERRORS

--------------------------------------------------------------------------------

Check #1: Row Count
  Table: users
  Status: [PASS]
  Details: Source: 5, Target: 5 (Match)

Check #2: Null Check
  Table: users
  Status: [FAIL]
  Columns: ['email']
  Details: Target users.email: 1 nulls found

Check #3: Duplicate PK Check
  Table: users
  Status: [FAIL]
  PK Column: id
  Details: Target users.id: 1 duplicate keys found
```

## Demo Data

The script automatically creates sample databases with the following characteristics:

### Source Database (`data/source.db`)
- Table: `users` with 5 clean records
- Columns: `id` (PRIMARY KEY), `name`, `email`, `created_at`
- All data is valid (no nulls, no duplicates)

### Target Database (`data/target.db`)
- Table: `users` with intentional data quality issues:
  - 1 row with NULL email (fails null check)
  - 1 duplicate ID (fails duplicate PK check)
  - Same row count as source (passes row count check)

## Customization

To use your own databases:

1. Modify the database paths in `scripts/data_quality_checker.py`:
   ```python
   checker = DataQualityChecker('path/to/source.db', 'path/to/target.db')
   ```

2. Change the table name and columns as needed:
   ```python
   checker.check_row_count('your_table_name')
   checker.check_nulls_in_key_columns('your_table_name', ['column1', 'column2'])
   checker.check_duplicate_primary_keys('your_table_name', 'id_column')
   ```

## Skills Demonstrated

- **Python**: Object-oriented programming, file I/O, error handling
- **SQL**: Query execution, aggregate functions, GROUP BY, HAVING clauses
- **Logging**: Configurable logging with file and console handlers
- **Data Validation**: Row counts, null checks, duplicate detection
- **Report Generation**: CSV export and console formatting

## License

This project is for educational and demonstration purposes.
