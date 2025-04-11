
import json

def generate_table_creator_php(table_name, columns, php_filename):
    # Create a dictionary with all the table settings
    db_settings = {
        "table_name": table_name,
        "columns": [],
        "php_filename": php_filename
    }
    
    # Parse columns into a more structured format for JSON
    for col in columns.split(",\n        "):
        if "PRIMARY KEY" in col or "FOREIGN KEY" in col:
            continue
        parts = col.split()
        col_name = parts[0]
        col_type = parts[1]
        col_def = {
            "name": col_name,
            "type": col_type,
            "null": "NOT NULL" if "NOT NULL" in col else "NULL",
            "default": None
        }
        
        # Extract default value if exists
        if "DEFAULT" in col:
            default_start = col.index("DEFAULT") + 8
            if "'" in col[default_start:]:
                col_def["default"] = col[default_start:].split("'")[1]
            else:
                col_def["default"] = col[default_start:].split()[0]
        
        db_settings["columns"].append(col_def)
    
    # Save the settings to JSON
    json_filename = f"db_settings_{table_name}.json"
    with open(json_filename, "w") as json_file:
        json.dump(db_settings, json_file, indent=4)
    
    # Generate the PHP code
    php_code = f"""<?php
// {php_filename} - WordPress table creation script

function {table_name}_create_table() {{
    global $wpdb;
    $charset_collate = $wpdb->get_charset_collate();
    $full_table_name = $wpdb->prefix . '{table_name}';
    
    $sql = "CREATE TABLE $full_table_name (
        {columns}
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
    
    // Add version option to track updates
   // add_option('{table_name}_db_version', '1.0');
}}


{table_name}_create_table();

?>
"""

    with open('db_installer_' + php_filename, "w") as file:
        file.write(php_code)
    print(f"\n✅ Success! PHP table creator '{php_filename}' has been generated.")
    print(f"✅ Database settings saved to '{json_filename}' for use in tabledesigngenerator.")


def show_column_types():
    print("\nAvailable Column Types:")
    print("1.  Integer (INT)")
    print("2.  Auto-increment ID (INT AUTO_INCREMENT)")
    print("3.  Variable string (VARCHAR)")
    print("4.  Text (TEXT)")
    print("5.  Long text (LONGTEXT)")
    print("6.  Boolean (TINYINT(1))")
    print("7.  Float (FLOAT)")
    print("8.  Decimal (DECIMAL)")
    print("9.  Date (DATE)")
    print("10. DateTime (DATETIME)")
    print("11. Timestamp (TIMESTAMP)")
    print("12. Foreign Key (INT)")
    print("13. JSON (JSON)")
    print("0.  Finish adding columns")

def get_column_definition(choice):
    column_types = {
        1: "INT",
        2: "INT AUTO_INCREMENT",
        3: "VARCHAR(255)",
        4: "TEXT",
        5: "LONGTEXT",
        6: "TINYINT(1)",
        7: "FLOAT",
        8: "DECIMAL(10,2)",
        9: "DATE",
        10: "DATETIME",
        11: "TIMESTAMP",
        12: "INT",
        13: "JSON"
    }
    return column_types.get(choice, "TEXT")

def get_columns_from_user():
    columns = []
    print("\nDefine your table columns:")
    
    while True:
        show_column_types()
        try:
            choice = int(input("\nSelect column type (1-13) or 0 to finish: "))
            if choice == 0:
                break
            if choice < 0 or choice > 13:
                print("Invalid choice. Please select 1-13 or 0 to finish.")
                continue
                
            col_name = input("Enter column name: ").strip()
            col_type = get_column_definition(choice)
            
            # Special handling for certain types
            if choice == 3:  # VARCHAR
                size = input("Enter VARCHAR length (default 255): ").strip()
                col_type = f"VARCHAR({size or 255})"
            elif choice == 8:  # DECIMAL
                precision = input("Enter DECIMAL precision (e.g., '10,2'): ").strip()
                col_type = f"DECIMAL({precision or '10,2'})"
            elif choice == 12:  # Foreign Key
                ref_table = input("Reference table name (e.g., 'users'): ").strip()
                ref_column = input("Reference column (e.g., 'ID'): ").strip()
                columns.append(f"{col_name} {col_type}")
                columns.append(f"FOREIGN KEY ({col_name}) REFERENCES {ref_table}({ref_column})")
                continue
            
            # Add NULL/NOT NULL
            null_option = input("Allow NULL? (y/n, default=n): ").strip().lower()
            if null_option != 'y':
                col_type += " NOT NULL"
                
            # Add default value if needed
            if choice in [9, 10, 11]:  # Date/time types
                default = input("Add DEFAULT CURRENT_TIMESTAMP? (y/n, default=y): ").strip().lower()
                if default != 'n':
                    col_type += " DEFAULT CURRENT_TIMESTAMP"
            elif choice != 2:  # Not auto-increment
                default = input("Default value (leave empty for none): ").strip()
                if default:
                    col_type += f" DEFAULT '{default}'"
            
            columns.append(f"{col_name} {col_type}")
            
        except ValueError:
            print("Please enter a valid number.")
    
    # Add primary key if not specified
    if not any("PRIMARY KEY" in col.upper() for col in columns):
        first_col = columns[0].split()[0] if columns else "id"
        columns.append(f"PRIMARY KEY ({first_col})")
    
    # Add timestamps if not specified
    if not any("created_at" in col.lower() for col in columns):
        columns.append("created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    if not any("updated_at" in col.lower() for col in columns):
        columns.append("updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    
    return ",\n        ".join(columns)

def main():
    print("WordPress Table Creator PHP Generator")
    print("------------------------------------")
    
    table_name = input("Enter table name (without wp_ prefix, e.g., 'zn_system_invoices'):\n> ").strip()
    columns = get_columns_from_user()
    php_filename = input("\nEnter output PHP filename (e.g., 'create_invoices_table.php'):\n> ").strip()
    
    generate_table_creator_php(
        table_name=table_name,
        columns=columns,
        php_filename=php_filename
    )

if __name__ == "__main__":
    main()
