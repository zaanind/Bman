def generate_php_script(table_name, id_column, success_redirect, item_name, php_filename):
    php_code = f"""<?php
// {php_filename} - generated script

$homeurl = get_site_url();

if (isset($_GET['id']) && !empty($_GET['id'])) {{
    global $wpdb;
    $item_id = intval($_GET['id']); // Ensure ID is an integer to prevent SQL injection

    // Check if the {item_name.lower()} exists
    $sql = $wpdb->prepare("SELECT {id_column} FROM {table_name} WHERE {id_column} = %d;", $item_id);
    $result = $wpdb->get_row($sql);

    if ($result) {{
        // Delete the {item_name.lower()}
        $sql = $wpdb->prepare("DELETE FROM {table_name} WHERE {id_column} = %d;", $item_id);
        $deleted = $wpdb->query($sql);

        if ($deleted !== false) {{
            status_header(200);
            wp_redirect($homeurl . '{success_redirect}');
            exit;
        }} else {{
            echo "Error: Deletion failed.";
        }}
    }} else {{
        echo "{item_name} not found for ID: " . $item_id;
    }}
}} else {{
    echo 'No ID provided';
}}
?>
"""
    with open(php_filename, "w") as file:
        file.write(php_code)
    print(f"✅ PHP delete script '{php_filename}' generated successfully.")


print('Please enter the DATABASE TABLE NAME (e.g., "wp_products"):')
table_name = input().strip()

print('\nPlease enter the ID COLUMN NAME (e.g., "product_id"):')
id_column = input().strip()

print('\nPlease enter the SUCCESS REDIRECT PATH (e.g., "domain will auto added  +    /success-page/"):')
success_redirect = input().strip()

print('\nPlease enter the ITEM NAME (human-readable, e.g., "Product"):')
item_name = input().strip()

print('\nPlease enter the OUTPUT PHP FILENAME (e.g., "delete-product.php"):')
php_filename = input().strip()


# Example usage
generate_php_script(
    table_name=table_name,              # Database table
    id_column=id_column,                          # ID column
    success_redirect=success_redirect,  # Redirect URL
    item_name=item_name,                          # Display item name
    php_filename=php_filename             # Output PHP file
)
