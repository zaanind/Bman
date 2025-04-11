import pyperclip

def generate_save_function(function_name, table_name, data_fields):
    """
    Generates a PHP function to save data to a WordPress database table.

    Args:
        function_name (str): The name of the PHP function.
        table_name (str): The name of the WordPress database table.
        data_fields (list): A list of the fields (column names) in the table.
                             This is used for comments to make the function clearer.

    Returns:
        str: The generated PHP function as a string.
    """
    php_code = f"""


function {function_name}($data) {{
    global $wpdb;
    $table_name = '{table_name}';

    // Check if 'id' exists for update
    if (!empty($data['id'])) {{
        $id = $data['id'];
        unset($data['id']);
        $updated = $wpdb->update($table_name, $data, ['id' => $id]);

        if ($wpdb->last_error) {{
            error_log("MySQL Error (Update): " . $wpdb->last_error);
            return false;
        }}

        return $updated !== false ? $id : false;
    }} else {{
        // Insert new record
        $inserted = $wpdb->insert($table_name, $data);

        if ($wpdb->last_error) {{
            error_log("MySQL Error (Insert): " . $wpdb->last_error);
            return false;
        }}

        return $inserted ? $wpdb->insert_id : false;
    }}
}}

"""
    return php_code

if __name__ == "__main__":
    table = input("Enter the database table name (e.g., wp_my_table): ")
    function = input("Enter the desired function name (e.g., save_my_data): ")
    fields_str = input("Enter the table fields (comma-separated, e.g., name, email, age): ")
    fields_list = [field.strip() for field in fields_str.split(',')]

    php_function = generate_save_function(function, table, fields_list)
    print("\nGenerated PHP Function:")
    print(php_function)

    try:
        pyperclip.copy(php_function)
        print("\nPHP function copied to clipboard!")
    except pyperclip.PyperclipException:
        print("\nCould not copy to clipboard. Make sure you have pyperclip installed (`pip install pyperclip`).")
