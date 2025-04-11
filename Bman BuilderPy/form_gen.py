import json
import os
from collections import OrderedDict

def generate_form_php(config):
    # Generate the PHP file content based on the configuration
    php_code = f"""<?php
session_start();
require_once('bcore.php');

// 1. Access Control
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

// 2. Handle POST (Form Submission)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {{
    // Initialize error array
    $errors = [];

    // Validate and sanitize form data
    {generate_validation_code(config['fields'])}

    // If no errors, proceed with database operations
    if (empty($errors)) {{
        {generate_db_operations(config)}

        // Redirect on success
        $_SESSION['success'] = '{config['success_message']}';
        wp_redirect($homeurl . '{config['redirect_url']}');
        exit;
    }} else {{
        // Store errors in session and repopulate form
        $_SESSION['errors'] = $errors;
        $_SESSION['old_input'] = $_POST;
        wp_redirect($homeurl . '{config['form_url']}');
        exit;
    }}
}}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <?php
    $active_page = get_query_var('active_page_wp_pos');
    $active_sub_m = get_query_var('active_sub_m');
    include_once('header.php');
    ?>
    <title>{config['page_title']} | <?php echo get_bloginfo('name'); ?></title>
    
    <style>
        /* Custom CSS */
        {config.get('custom_css', '')}
        
        /* Suggestions styling */
        .suggestions {{
            border: 1px solid #ccc;
            max-height: 150px;
            overflow-y: auto;
            position: absolute;
            background: white;
            width: 100%;
            z-index: 1000;
            display: none;
        }}
        .suggestion-item {{
            cursor: pointer;
            padding: 8px;
        }}
        .suggestion-item:hover {{
            background: #f0f0f0;
        }}
        .is-invalid {{
            border-color: #dc3545 !important;
        }}
        .invalid-feedback {{
            color: #dc3545;
            display: none;
            width: 100%;
            margin-top: 0.25rem;
            font-size: 0.875em;
        }}
    </style>
</head>

<body>
<div class="wrapper">
    <?php include_once('sidebar.php'); ?>
    <div class="main">
        <?php include_once('navbar.php'); ?>

        <main class="content">
            <div class="container-fluid p-0">
                <h1 class="h3 mb-3">{config['page_title']}</h1>
                
                <?php if (isset($_SESSION['errors'])): ?>
                    <div class="alert alert-danger alert-dismissible" role="alert">
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        <div class="alert-message">
                            <strong>Error:</strong> Please fix the following issues:
                            <ul>
                                <?php foreach ($_SESSION['errors'] as $error): ?>
                                    <li><?php echo htmlspecialchars($error); ?></li>
                                <?php endforeach; ?>
                            </ul>
                        </div>
                    </div>
                    <?php unset($_SESSION['errors']); ?>
                <?php endif; ?>
                
                <?php if (isset($_SESSION['success'])): ?>
                    <div class="alert alert-success alert-dismissible" role="alert">
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        <div class="alert-message">
                            <?php echo htmlspecialchars($_SESSION['success']); ?>
                        </div>
                    </div>
                    <?php unset($_SESSION['success']); ?>
                <?php endif; ?>

                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title">{config['form_title']}</h5>
                            </div>
                            <div class="card-body">
                                <form method="POST" action="<?php echo esc_url($homeurl . '{config['form_url']}'); ?>" { 'enctype="multipart/form-data"' if any(field['type'] == 'file' for field in config['fields']) else '' }>
                                    {generate_form_fields(config['fields'])}
                                    
                                    <div class="row mt-4">
                                        <div class="col-12">
                                            <button type="submit" class="btn btn-primary float-end">{config['submit_button_text']}</button>
                                            <a href="<?php echo $homeurl . '{config['cancel_url']}'; ?>" class="btn btn-secondary">Cancel</a>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <?php include_once('footer.php'); ?>
    </div>
</div>

<!-- JavaScript -->
<script>
jQuery(document).ready(function($) {{
    {generate_javascript(config)}
}});
</script>
</body>
</html>
"""
    return php_code

def generate_validation_code(fields):
    code = ""
    for field in fields:
        if field.get('required', False):
            code += f"""
    // Validate {field['name']}
    ${field['name']} = isset($_POST['{field['name']}']) ? trim($_POST['{field['name']}']) : '';
    if (empty(${field['name']})) {{
        $errors[] = '{field['label']} is required';
    }} else {{
        ${field['name']} = {get_sanitization_code(field)};
    }}
"""
        else:
            code += f"""
    // Process {field['name']}
    ${field['name']} = isset($_POST['{field['name']}']) ? {get_sanitization_code(field)} : NULL;
"""
    return code

def get_sanitization_code(field):
    field_type = field['type']
    name = field['name']
    
    if field_type in ['text', 'textarea', 'select', 'radio']:
        return f"sanitize_text_field(trim($_POST['{name}']))"
    elif field_type == 'email':
        return f"sanitize_email(trim($_POST['{name}']))"
    elif field_type == 'number':
        return f"floatval($_POST['{name}'])"
    elif field_type == 'checkbox':
        return f"isset($_POST['{name}']) ? 1 : 0"
    elif field_type == 'date':
        return f"sanitize_text_field($_POST['{name}'])"
    elif field_type == 'file':
        return f"$_FILES['{name}']"
    else:
        return f"sanitize_text_field(trim($_POST['{name}']))"

def generate_db_operations(config):
    code = f"""
        global $wpdb;
        $table_name = $wpdb->prefix . '{config['table_name']}';
        
        // Prepare data for insertion
        $data = array(
"""
    
    for field in config['fields']:
        if field['type'] == 'file':
            continue  # File handling would be separate
        code += f"            '{field['db_column']}' => ${field['name']},\n"
    
    code += f"""            'created_at' => current_time('mysql'),
            'updated_at' => current_time('mysql')
        );
        
        // Insert into database
        $inserted = $wpdb->insert($table_name, $data);
        
        if (!$inserted) {{
            $errors[] = 'Failed to save record. Please try again.';
            $_SESSION['errors'] = $errors;
            $_SESSION['old_input'] = $_POST;
            wp_redirect($homeurl . '{config['form_url']}');
            exit;
        }}
"""
    
    # Add file upload handling if any file fields exist
    if any(field['type'] == 'file' for field in config['fields']):
        code += """
        // Handle file uploads
        require_once(ABSPATH . 'wp-admin/includes/file.php');
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        
        $upload_overrides = array('test_form' => false);
"""
        for field in config['fields']:
            if field['type'] == 'file':
                code += f"""
        if (!empty(${field['name']}['name'])) {{
            ${field['name']}_file = wp_handle_upload(${field['name']}, $upload_overrides);
            
            if (isset(${field['name']}_file['error'])) {{
                $errors[] = 'Failed to upload {field['label']}: ' . ${field['name']}_file['error'];
            }} else {{
                // Update the record with file URL
                $wpdb->update(
                    $table_name,
                    array('{field['db_column']}' => ${field['name']}_file['url']),
                    array('id' => $wpdb->insert_id)
                );
            }}
        }}
"""
    
    return code

def generate_form_fields(fields):
    html = ""
    for field in fields:
        html += f"""
                                    <div class="mb-3">
                                        <label class="form-label">{field['label']}{' <span class="text-danger">*</span>' if field.get('required', False) else ''}</label>
                                        {generate_field_html(field)}
                                        <div class="invalid-feedback" id="{field['name']}-error"></div>
                                    </div>
"""
    return html

def generate_field_html(field):
    field_type = field['type']
    name = field['name']
    required = 'required' if field.get('required', False) else ''
    
    if field_type == 'text':
        return f"""<input type="text" class="form-control" name="{name}" id="{name}" {required}
                   value="<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>">"""
    
    elif field_type == 'email':
        return f"""<input type="email" class="form-control" name="{name}" id="{name}" {required}
                   value="<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>">"""
    
    elif field_type == 'number':
        min_val = field.get('min', '')
        max_val = field.get('max', '')
        step = field.get('step', 'any')
        return f"""<input type="number" class="form-control" name="{name}" id="{name}" 
                   min="{min_val}" max="{max_val}" step="{step}" {required}
                   value="<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>">"""
    
    elif field_type == 'textarea':
        return f"""<textarea class="form-control" name="{name}" id="{name}" {required} rows="3">
<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>
</textarea>"""
    
    elif field_type == 'select':
        options = "\n".join(
            f"""<option value='{opt['value']}' <?php echo (isset($_SESSION['old_input']['{name}']) && $_SESSION['old_input']['{name}'] == '{opt['value']}') ? 'selected' : ''; ?>>{opt['label']}</option>"""
            for opt in field['options']
        )
        return f"""<select class="form-select" name="{name}" id="{name}" {required}>
            <option value="">Select {field['label']}</option>
            {options}
        </select>"""
    
    elif field_type == 'checkbox':
        return f"""<div class="form-check">
            <input class="form-check-input" type="checkbox" name="{name}" id="{name}" value="1"
                   <?php echo (isset($_SESSION['old_input']['{name}']) && $_SESSION['old_input']['{name}'] == '1') ? 'checked' : ''; ?>>
            <label class="form-check-label" for="{name}">{field.get('checkbox_label', '')}</label>
        </div>"""
    
    elif field_type == 'radio':
        radios = "\n".join(
            f"""<div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="{name}" id="{name}-{opt['value']}" value="{opt['value']}"
                       <?php echo (isset($_SESSION['old_input']['{name}']) && $_SESSION['old_input']['{name}'] == '{opt['value']}') ? 'checked' : ''; ?>>
                <label class="form-check-label" for="{name}-{opt['value']}">{opt['label']}</label>
            </div>"""
            for opt in field['options']
        )
        return f"""<div class="form-group">
            {radios}
        </div>"""
    
    elif field_type == 'date':
        return f"""<input type="date" class="form-control" name="{name}" id="{name}" {required}
                   value="<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>">"""
    
    elif field_type == 'file':
        return f"""<input type="file" class="form-control" name="{name}" id="{name}" {required}>
                   <small class="text-muted">{field.get('file_types', 'Allowed file types: jpg, png, pdf')}</small>"""
    
    elif field_type == 'hidden':
        return f"""<input type="hidden" name="{name}" id="{name}" value="<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>">"""
    
    else:
        return f"""<input type="text" class="form-control" name="{name}" id="{name}" {required}
                   value="<?php echo isset($_SESSION['old_input']['{name}']) ? htmlspecialchars($_SESSION['old_input']['{name}']) : ''; ?>">"""

def generate_javascript(config):
    js = """
    // Client-side validation
    function validateForm() {
        let isValid = true;
"""
    
    for field in config['fields']:
        if field.get('required', False):
            js += f"""
        // Validate {field['name']}
        const {field['name']} = $('#{field['name']}').val().trim();
        if (!{field['name']}) {{
            $('#{field['name']}').addClass('is-invalid');
            $('#{field['name']}-error').text('{field['label']} is required').show();
            isValid = false;
        }} else {{
            $('#{field['name']}').removeClass('is-invalid');
            $('#{field['name']}-error').hide();
        }}
"""
    
    js += """
        return isValid;
    }
    
    // Form submission handler
    $('form').on('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            $('.is-invalid').first().focus();
        }
    });
"""
    
    # Add autocomplete/suggestion logic for fields that need it
    for field in config['fields']:
        if field.get('autocomplete', False):
            extra_fields_js = " ".join(
                f"data-{k}='${{item.{v} || ''}}' "
                for k, v in field['autocomplete'].get('extra_fields', {}).items()
            )
            
            js += f"""
    // Autocomplete for {field['name']}
    $('#{field['name']}').on('input', function() {{
        const query = $(this).val();
        if (query.length > 2) {{
            $.ajax({{
                url: '{field['autocomplete']['api_url']}',
                method: 'POST',
                data: {{
                    {field['autocomplete']['search_param']}: query
                }},
                success: function(data) {{
                    let suggestions = '';
                    if (Array.isArray(data) && data.length > 0) {{
                        data.forEach(item => {{
                            suggestions += `<div class='suggestion-item' 
                                data-value='${{item.{field['autocomplete']['value_field']} || ''}}'
                                {extra_fields_js}>
                                ${{item.{field['autocomplete']['display_field']} || 'Unknown'}}
                            </div>`;
                        }});
                    }} else {{
                        suggestions = '<div class="suggestion-item">No results found</div>';
                    }}
                    $('#{field['name']}-suggestions').html(suggestions).show();
                }}
            }});
        }} else {{
            $('#{field['name']}-suggestions').hide();
        }}
    }});
    
    // Handle suggestion selection
    $(document).on('click', '#{field['name']}-suggestions .suggestion-item', function() {{
        $('#{field['name']}').val($(this).data('value'));
"""
            for extra_field, extra_value in field['autocomplete'].get('extra_fields', {}).items():
                js += f"""
        $('#{extra_field}').val($(this).data('{extra_field}'));
"""
            js += f"""
        $('#{field['name']}-suggestions').hide();
    }});
    
    // Hide suggestions when clicking outside
    $(document).click(function(e) {{
        if (!$(e.target).closest('#{field['name']}, #{field['name']}-suggestions').length) {{
            $('#{field['name']}-suggestions').hide();
        }}
    }});
"""
    
    return js

def get_field_config():
    fields = []
    print("\nConfigure form fields:")
    
    while True:
        print("\n1. Add new field")
        print("2. Finish adding fields")
        choice = input("Select option (1-2): ").strip()
        
        if choice == '2':
            break
            
        if choice != '1':
            print("Invalid choice")
            continue
            
        field = {
            'name': input("Field name (snake_case, e.g., 'customer_name'): ").strip(),
            'label': input("Field label (e.g., 'Customer Name'): ").strip(),
            'type': input("Field type (text/email/number/textarea/select/checkbox/radio/date/file/hidden): ").strip().lower(),
            'required': input("Is this field required? (y/n): ").strip().lower() == 'y',
            'db_column': input("Database column name (leave empty to match field name): ").strip() or None
        }
        
        # Type-specific configuration
        if field['type'] == 'number':
            field['min'] = input("Minimum value (leave empty for none): ").strip() or None
            field['max'] = input("Maximum value (leave empty for none): ").strip() or None
            field['step'] = input("Step value (e.g., '0.01' for currency, leave empty for 'any'): ").strip() or 'any'
        
        elif field['type'] in ['select', 'radio']:
            options = []
            print("Add options for select/radio:")
            while True:
                value = input("Option value (e.g., 'option1'): ").strip()
                if not value:
                    break
                label = input("Option label (e.g., 'Option 1'): ").strip()
                options.append({'value': value, 'label': label})
                another = input("Add another option? (y/n): ").strip().lower() != 'y'
                if another:
                    break
            field['options'] = options
        
        elif field['type'] == 'checkbox':
            field['checkbox_label'] = input("Checkbox label text (e.g., 'I agree to terms'): ").strip()
        
        elif field['type'] == 'file':
            field['file_types'] = input("Allowed file types (e.g., 'jpg, png, pdf'): ").strip()
        
        # Autocomplete configuration
        if input("Add autocomplete/suggestions for this field? (y/n): ").strip().lower() == 'y':
            field['autocomplete'] = {
                'api_url': input("API URL for suggestions (e.g., '/api/customers_api'): ").strip(),
                'search_param': input("API search parameter name (e.g., 'search_customer_query'): ").strip(),
                'value_field': input("Field in API response to use as value (e.g., 'id'): ").strip(),
                'display_field': input("Field in API response to display (e.g., 'name'): ").strip()
            }
            
            # Extra fields to populate
            extra_fields = {}
            print("Configure additional fields to populate from autocomplete:")
            while True:
                field_name = input("Field name to populate (leave empty to finish): ").strip()
                if not field_name:
                    break
                response_field = input(f"API response field for {field_name}: ").strip()
                extra_fields[field_name] = response_field
            if extra_fields:
                field['autocomplete']['extra_fields'] = extra_fields
        
        fields.append(field)
    
    return fields

def main():
    print("WordPress Form Generator")
    print("-----------------------")
    
    config = {
        'page_title': input("Page title (e.g., 'Add Customer'): ").strip(),
        'form_title': input("Form title (e.g., 'Customer Information'): ").strip(),
        'table_name': input("Database table name (without wp_ prefix, e.g., 'customers'): ").strip(),
        'form_url': input("Form URL path (e.g., '/customers/add'): ").strip(),
        'redirect_url': input("Redirect URL after submission (e.g., '/customers'): ").strip(),
        'cancel_url': input("Cancel URL (e.g., '/customers'): ").strip(),
        'submit_button_text': input("Submit button text (e.g., 'Save Customer'): ").strip(),
        'success_message': input("Success message (e.g., 'Customer added successfully!'): ").strip(),
        'allowed_roles': [],
        'fields': []
    }
    
    # Get allowed roles
    print("\nConfigure allowed roles (leave empty to finish):")
    while True:
        role = input("Add role (e.g., 'administrator', 'editor'): ").strip()
        if not role:
            break
        config['allowed_roles'].append(role)
    
    if not config['allowed_roles']:
        config['allowed_roles'] = ['administrator']
    
    # Get form fields
    config['fields'] = get_field_config()
    
    # Generate the PHP file
    php_code = generate_form_php(config)
    output_file = input("\nOutput PHP filename (e.g., 'add_customer.php'): ").strip()
    
    with open(output_file, 'w') as f:
        f.write(php_code)
    
    print(f"\n✅ Success! Form file '{output_file}' has been generated.")
    
    # Save config for future editing
    config_file = output_file.replace('.php', '.config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved to '{config_file}' for future editing.")

if __name__ == "__main__":
    main()
