import os
import json
from collections import OrderedDict
import re

def generate_php_actions(actions):
    if not actions:
        return "[]"
    
    php_code = "[\n"
    for action in actions:
        php_code += f"        ['path' => '{action['path']}', 'text' => '{action['text']}'],\n"
    php_code = php_code.rstrip(',\n') + "\n    ]"
    return php_code


def generate_action_buttons_php():
    return """function generateActionButtons($actions, $id, $homeurl = '') {
    $html = "<div class='btn-group'><button type='button' class='btn btn-primary dropdown-toggle' data-bs-toggle='dropdown' aria-expanded='false'>Actions</button>";
    $html .= "<ul class='dropdown-menu'>";
    
    foreach ($actions as $action) {
        $path = $homeurl . $action['path'] . $id;
        $html .= "<li><a class='dropdown-item' href='{$path}'>{$action['text']}</a></li>";
    }
    
    $html .= "</ul></div>";
    return $html;
}

function createTable($headers = [], $data = []) {
    $html = '<table id="datatables-reponsive" class="table table-striped" style="width:100%">';
    
    // Add headers if provided
    if (!empty($headers)) {
        $html .= '<thead><tr>';
        foreach ($headers as $header) {
            $html .= '<th>' . htmlspecialchars($header) . '</th>';
        }
        $html .= '</tr></thead>';
    }
    
    // Add data rows
    $html .= '<tbody>';
    foreach ($data as $row) {
        $html .= '<tr>';
        foreach ($row as $cell) {
            $html .= '<td>' . $cell . '</td>';
        }
        $html .= '</tr>';
    }
    $html .= '</tbody>';
    
    $html .= '</table>';
    return $html;
}
"""

def get_table_columns():
    columns = []
    print("\nConfigure table columns:")
    
    while True:
        print("\n1. Add new column")
        print("2. Edit existing column")
        print("3. Remove column")
        print("4. Finish adding columns")
        choice = input("Select option (1-4): ").strip()
        
        if choice == '4':
            break
            
        if choice == '1':
            column_name = input("Column header name: ").strip()
            if not column_name:
                print("Column name cannot be empty")
                continue
                
            print("\nColumn data source options:")
            print("1. Direct database column")
            print("2. Custom PHP expression")
            print("3. Image from URL")
            print("4. Image from WordPress attachment")
            print("5. Data from joined table")
            
            source_type = input("Select data source type (1-5): ").strip()
            
            column_config = {
                'name': column_name,
                'type': 'direct' if source_type == '1' else 'custom'
            }
            
            if source_type == '1':
                column_config['db_column'] = input("Database column name: ").strip()
            elif source_type == '2':
                column_config['php_code'] = input("PHP expression (use $row for current row data): ").strip()
            elif source_type == '3':
                column_config['type'] = 'image_url'
                column_config['db_column'] = input("Database column containing image URL: ").strip()
                column_config['default'] = input("Default image URL (leave empty for 'No Image'): ").strip()
            elif source_type == '4':
                column_config['type'] = 'wp_image'
                column_config['db_column'] = input("Database column containing attachment ID or JSON: ").strip()
                column_config['default'] = input("Default image URL (leave empty for 'No Image'): ").strip()
            elif source_type == '5':
                column_config['type'] = 'joined'
                column_config['join_table'] = input("Table to join: ").strip()
                column_config['join_on'] = input("Join condition (e.g., 'customer_id'): ").strip()
                column_config['join_column'] = input("Column to display from joined table: ").strip()
            else:
                print("Invalid source type")
                continue
                
            columns.append(column_config)
            
        elif choice == '2' and columns:
            print("\nCurrent columns:")
            for i, col in enumerate(columns, 1):
                print(f"{i}. {col['name']} ({col['type']})")
            col_num = input("Enter column number to edit: ").strip()
            try:
                col_idx = int(col_num) - 1
                if 0 <= col_idx < len(columns):
                    col = columns[col_idx]
                    print(f"\nEditing column: {col['name']}")
                    new_name = input(f"New name [{col['name']}]: ").strip() or col['name']
                    col['name'] = new_name
                    
                    if col['type'] == 'direct':
                        new_col = input(f"Database column [{col.get('db_column', '')}]: ").strip()
                        if new_col:
                            col['db_column'] = new_col
                    elif col['type'] == 'custom':
                        new_code = input(f"PHP code [{col.get('php_code', '')}]: ").strip()
                        if new_code:
                            col['php_code'] = new_code
                    elif col['type'] == 'image_url':
                        new_col = input(f"Image URL column [{col.get('db_column', '')}]: ").strip()
                        if new_col:
                            col['db_column'] = new_col
                        new_default = input(f"Default image [{col.get('default', '')}]: ").strip()
                        if new_default:
                            col['default'] = new_default
                    elif col['type'] == 'wp_image':
                        new_col = input(f"Attachment column [{col.get('db_column', '')}]: ").strip()
                        if new_col:
                            col['db_column'] = new_col
                        new_default = input(f"Default image [{col.get('default', '')}]: ").strip()
                        if new_default:
                            col['default'] = new_default
                    elif col['type'] == 'joined':
                        new_table = input(f"Join table [{col.get('join_table', '')}]: ").strip()
                        if new_table:
                            col['join_table'] = new_table
                        new_on = input(f"Join condition [{col.get('join_on', '')}]: ").strip()
                        if new_on:
                            col['join_on'] = new_on
                        new_col = input(f"Display column [{col.get('join_column', '')}]: ").strip()
                        if new_col:
                            col['join_column'] = new_col
                else:
                    print("Invalid column number")
            except ValueError:
                print("Please enter a valid number")
                
        elif choice == '3' and columns:
            print("\nCurrent columns:")
            for i, col in enumerate(columns, 1):
                print(f"{i}. {col['name']} ({col['type']})")
            col_num = input("Enter column number to remove: ").strip()
            try:
                col_idx = int(col_num) - 1
                if 0 <= col_idx < len(columns):
                    removed = columns.pop(col_idx)
                    print(f"Removed column: {removed['name']}")
                else:
                    print("Invalid column number")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Invalid choice")
            
    return columns

def get_action_buttons():
    actions = []
    print("\nConfigure action buttons:")
    
    while True:
        print("\nCurrent actions:")
        for i, action in enumerate(actions, 1):
            print(f"{i}. {action['text']} -> {action['path']}")
            
        print("\n1. Add new action")
        print("2. Edit action")
        print("3. Remove action")
        print("4. Finish configuring actions")
        choice = input("Select option (1-4): ").strip()
        
        if choice == '4':
            break
            
        if choice == '1':
            text = input("Button text (e.g., 'View', 'Edit'): ").strip()
            if not text:
                print("Text cannot be empty")
                continue
                
            path = input("URL path (e.g., '/products/view?id='): ").strip()
            if not path:
                print("Path cannot be empty")
                continue
                
            actions.append({
                'text': text,
                'path': path
            })
            
        elif choice == '2' and actions:
            action_num = input("Enter action number to edit: ").strip()
            try:
                action_idx = int(action_num) - 1
                if 0 <= action_idx < len(actions):
                    action = actions[action_idx]
                    new_text = input(f"New text [{action['text']}]: ").strip() or action['text']
                    new_path = input(f"New path [{action['path']}]: ").strip() or action['path']
                    actions[action_idx] = {'text': new_text, 'path': new_path}
                else:
                    print("Invalid action number")
            except ValueError:
                print("Please enter a valid number")
                
        elif choice == '3' and actions:
            index = input(f"Enter action number to remove (1-{len(actions)}): ").strip()
            try:
                index = int(index) - 1
                if 0 <= index < len(actions):
                    removed = actions.pop(index)
                    print(f"Removed action: {removed['text']}")
                else:
                    print("Invalid index")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Invalid choice")
            
    return actions

def get_allowed_roles():
    roles = []
    print("\nConfigure allowed roles (leave empty to finish):")
    
    while True:
        role = input("Add role (e.g., 'administrator', 'editor'): ").strip()
        if not role:
            break
        roles.append(role)
        
    return roles if roles else ['administrator']

def generate_php_file(config):
    php_code = f"""<?php
{generate_action_buttons_php()}

$homeurl = get_site_url();
$wpuser_ob = wp_get_current_user();
$allowed_roles = {json.dumps(config['allowed_roles'])};

$has_allowed_role = false;
foreach ($wpuser_ob->roles as $role) {{
    if (in_array($role, $allowed_roles)) {{
        $has_allowed_role = true;
        break; 
    }}
}}

if (!$has_allowed_role) {{
    status_header(401);
    wp_redirect($homeurl . '/unauthorized');
    exit;
}}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <?php
    $active_page = get_query_var('active_page_wp_pos'); 
    $active_sub_m = get_query_var('active_sub_m'); 
    include_once('header.php'); ?>
    <title>{config['page_title']} | <?php echo get_bloginfo( 'name' ); ?></title>
</head>

<body>
    <div class="wrapper">
        <?php include_once('sidebar.php'); ?>
        <div class="main">
            <?php include_once('navbar.php'); ?>

            <main class="content">
                <div class="container-fluid p-0">
                    <a href="<?php echo get_site_url(); ?>{config['add_button']['path']}" class="btn btn-primary float-end mt-n1"><i class="fas fa-plus"></i> {config['add_button']['text']}</a>

                    <div class="mb-3">
                        <h1 class="h3 d-inline align-middle">{config['page_title']}</h1>
                    </div>

                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-body">
                                    <?php
                                    global $wpdb;
                                    $query = "{config['sql_query']}";
                                    $results = $wpdb->get_results($query);                               
                                    ?>
                                    
                                    <?php 
                                    $headers = {json.dumps([col['name'] for col in config['columns']])};
                                    $data = [];  

                                    $actions = {generate_php_actions(config['actions'])};

                                    foreach ($results as $row) {{
                                        $row_data = [];
                                        {generate_column_processing(config['columns'])}
                                        $row_data[] = generateActionButtons($actions, $row->id, $homeurl); 
                                       
                                        $data[] = $row_data;
                                    }}
                                    
                                    echo createTable($headers, $data);
                                    ?>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
            
            <?php include_once('footer.php');?>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            // Datatables Responsive
            $("#datatables-reponsive").DataTable({{
                responsive: true,
                order: {json.dumps(config['default_sort'])}
            }});
        }});
    </script>
</body>
</html>
"""
    return php_code

def generate_column_processing(columns):
    processing_code = ""
    
    for col in columns:
        if col['type'] == 'direct':
            processing_code += f"$row_data[] = $row->{col['db_column']};\n"
        elif col['type'] == 'custom':
            processing_code += f"$row_data[] = {col['php_code']};\n"
        elif col['type'] == 'image_url':
            default = col.get('default', 'No Image')
            processing_code += f"""
            ${col['db_column']}_url = $row->{col['db_column']} ? $row->{col['db_column']} : '{default}';
            $row_data[] = ${col['db_column']}_url ? '<img src="' . esc_url(${col['db_column']}_url) . '" style="width: 60px; height: 60px; object-fit: cover;" alt="Image">' : 'No Image';
            """
        elif col['type'] == 'wp_image':
            default = col.get('default', 'No Image')
            processing_code += f"""
            ${col['db_column']}_url = '';
            ${col['db_column']}_link = json_decode($row->{col['db_column']});
            
            if (${col['db_column']}_link && isset(${col['db_column']}_link->id)) {{
                ${col['db_column']}_url = wp_get_attachment_url(${col['db_column']}_link->id);
            }} elseif (${col['db_column']}_link && isset(${col['db_column']}_link->url)) {{
                ${col['db_column']}_url = ${col['db_column']}_link->url;
            }} elseif ('{default}') {{
                ${col['db_column']}_url = '{default}';
            }}
            
            $row_data[] = ${col['db_column']}_url ? '<img src="' . esc_url(${col['db_column']}_url) . '" style="width: 60px; height: 60px; object-fit: cover;" alt="Image">' : 'No Image';
            """
        elif col['type'] == 'joined':
            processing_code += f"""
            $join_query = "SELECT {col['join_column']} FROM {col['join_table']} WHERE {col['join_on']} = {{$row->{col['join_on']}}}";
            $join_result = $wpdb->get_row($join_query);
            $row_data[] = $join_result ? $join_result->{col['join_column']} : 'N/A';
            """
    
    return processing_code

def parse_existing_php_file(filename):
    config = {
        'page_title': '',
        'sql_query': '',
        'add_button': {'text': '', 'path': ''},
        'columns': [],
        'actions': [],
        'allowed_roles': ['administrator'],
        'default_sort': [0, 'desc']
    }
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
            
            # Extract page title
            title_match = re.search(r'<h1 class="h3 d-inline align-middle">([^<]+)</h1>', content)
            if title_match:
                config['page_title'] = title_match.group(1).strip()
                
            # Extract SQL query
            query_match = re.search(r'\$query = "([^"]+)"', content)
            if query_match:
                config['sql_query'] = query_match.group(1).strip()
                
            # Extract add button
            add_button_match = re.search(r'<a href="[^"]+([^"]+)"[^>]*><i class="fas fa-plus"></i> ([^<]+)</a>', content)
            if add_button_match:
                config['add_button']['path'] = add_button_match.group(1).strip()
                config['add_button']['text'] = add_button_match.group(2).strip()
                
            # Extract allowed roles
            roles_match = re.search(r'\$allowed_roles = (\[[^\]]+\])', content)
            if roles_match:
                try:
                    config['allowed_roles'] = json.loads(roles_match.group(1).replace("'", '"'))
                except:
                    pass
                    
            # Extract default sort
            sort_match = re.search(r'order: (\[[^\]]+\])', content)
            if sort_match:
                try:
                    config['default_sort'] = json.loads(sort_match.group(1))
                except:
                    pass
                    
            # Extract headers
            headers_match = re.search(r'\$headers = (\[[^\]]+\])', content)
            if headers_match:
                try:
                    headers = json.loads(headers_match.group(1).replace("'", '"'))
                    config['columns'] = [{'name': h, 'type': 'direct', 'db_column': h.lower()} for h in headers]
                except:
                    pass
                    
            # Extract actions
            actions_match = re.search(r'\$actions = (\[[^\]]+\])', content, re.DOTALL)
            if actions_match:
                try:
                    actions_str = actions_match.group(1).replace("'", '"')
                    actions_str = re.sub(r'\/\*.*?\*\/', '', actions_str)  # Remove comments
                    config['actions'] = json.loads(actions_str)
                except Exception as e:
                    print(f"Couldn't parse actions: {e}")
                    
            # Try to find config file
            config_file = filename.replace('.php', '.config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    existing_config = json.load(f)
                    # Merge with priority to existing_config
                    for key in existing_config:
                        if key in config:
                            if isinstance(config[key], dict) and isinstance(existing_config[key], dict):
                                config[key].update(existing_config[key])
                            else:
                                config[key] = existing_config[key]
                                
    except Exception as e:
        print(f"Error parsing file: {e}")
        
    return config

def main():
    print("WordPress Table View Generator")
    print("-----------------------------")
    
    # Check if editing existing file
    edit_existing = input("Do you want to edit an existing file? (y/n): ").strip().lower() == 'y'
    config = {}
    
    if edit_existing:
        filename = input("Enter existing PHP filename: ").strip()
        if os.path.exists(filename):
            config = parse_existing_php_file(filename)
            print(f"\nLoaded existing configuration from {filename}")
        else:
            print("File not found, starting new configuration")
            edit_existing = False
    
    if not edit_existing:
        config = {
            'page_title': input("\nPage title (e.g., 'Products'): ").strip(),
            'sql_query': input("SQL query to fetch data (e.g., 'SELECT * FROM wp_products'): ").strip(),
            'add_button': {
                'text': input("Add button text (e.g., 'New Product'): ").strip(),
                'path': input("Add button URL path (e.g., '/products/add'): ").strip()
            },
            'default_sort': [0, 'desc']
        }
    
    # Configure columns
    print("\n=== Table Columns ===")
    if 'columns' in config and config['columns']:
        print("Current columns:")
        for i, col in enumerate(config['columns'], 1):
            print(f"{i}. {col['name']} ({col.get('type', 'direct')})")
        choice = input("\nKeep existing columns? (y/n): ").strip().lower()
        if choice == 'n':
            config['columns'] = get_table_columns()
        else:
            print("\nYou can edit individual columns in the next step")
            config['columns'] = get_table_columns()  # This will show existing columns for editing
    else:
        config['columns'] = get_table_columns()
    
    # Configure actions
    print("\n=== Action Buttons ===")
    if 'actions' in config and config['actions']:
        print("Current actions:")
        for i, action in enumerate(config['actions'], 1):
            print(f"{i}. {action['text']} -> {action['path']}")
        choice = input("\nKeep existing actions? (y/n): ").strip().lower()
        if choice == 'n':
            config['actions'] = get_action_buttons()
        else:
            print("\nYou can edit individual actions in the next step")
            config['actions'] = get_action_buttons()  # This will show existing actions for editing
    else:
        config['actions'] = get_action_buttons()
    
    # Configure allowed roles
    print("\n=== Allowed Roles ===")
    if 'allowed_roles' in config and config['allowed_roles']:
        print("Current roles:", ", ".join(config['allowed_roles']))
        choice = input("\nKeep existing roles? (y/n): ").strip().lower()
        if choice == 'n':
            config['allowed_roles'] = get_allowed_roles()
    else:
        config['allowed_roles'] = get_allowed_roles()
    
    # Configure default sort
    print("\n=== Default Sorting ===")
    if 'default_sort' in config and config['default_sort']:
        current_col = config['default_sort'][0] + 1
        current_dir = config['default_sort'][1]
        print(f"Current sort: Column {current_col} ({current_dir})")
    
    print("\nConfigure default table sorting:")
    print("Current columns:")
    for i, col in enumerate(config['columns'], 1):
        print(f"{i}. {col['name']}")
        
    col_choice = input("Enter column number to sort by (default 1): ").strip()
    try:
        col_index = int(col_choice) - 1 if col_choice else 0
        if 0 <= col_index < len(config['columns']):
            sort_dir = input("Sort direction (asc/desc, default desc): ").strip().lower()
            config['default_sort'] = [col_index, sort_dir if sort_dir in ['asc', 'desc'] else 'desc']
    except ValueError:
        pass
    
    # Generate the PHP file
    php_code = generate_php_file(config)
    output_file = input("\nOutput PHP filename (e.g., 'products_table.php'): ").strip()
    
    with open(output_file, 'w') as f:
        f.write(php_code)
    
    print(f"\n✅ Success! Table view file '{output_file}' has been generated.")
    
    # Save config for future editing
    config_file = output_file.replace('.php', '.config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved to '{config_file}' for future editing.")

if __name__ == "__main__":
    main()
