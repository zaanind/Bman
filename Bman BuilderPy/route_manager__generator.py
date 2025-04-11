import os
import re
import json
from collections import OrderedDict

def load_existing_routes(file_path):
    """Load existing routes from a PHP file"""
    routes = OrderedDict()
    
    if not os.path.exists(file_path):
        return routes
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract the routes array using regex
    match = re.search(r'\$routes\s*=\s*\[([\s\S]*?)\];', content)
    if not match:
        return routes
    
    routes_content = match.group(1)
    # Extract individual route entries
    route_matches = re.finditer(r"'(.*?)'\s*=>\s*'(.*?)'", routes_content)
    
    for match in route_matches:
        route = match.group(1).strip()
        path = match.group(2).strip()
        routes[route] = path
    
    return routes

def add_route(routes):
    """Add a new route to the routes dictionary"""
    print("\nAdd a new route:")
    while True:
        route = input("Enter the URL path (e.g., 'orders/add'): ").strip()
        if not route:
            print("Route cannot be empty. Please try again.")
            continue
        
        if route in routes:
            print(f"Warning: Route '{route}' already exists. Do you want to overwrite it?")
            choice = input("(y/n, default=n): ").strip().lower()
            if choice != 'y':
                continue
        
        path = input("Enter the PHP file path (e.g., 'public/orders_add.php'): ").strip()
        if not path:
            print("Path cannot be empty. Please try again.")
            continue
        
        routes[route] = path
        print(f"Added route: '{route}' => '{path}'")
        
        another = input("Add another route? (y/n, default=n): ").strip().lower()
        if another != 'y':
            break
    
    # Sort routes in descending order to prevent conflicts
    return OrderedDict(sorted(routes.items(), key=lambda x: x[0], reverse=True))

def remove_route(routes):
    """Remove a route from the routes dictionary"""
    if not routes:
        print("No routes available to remove.")
        return routes
    
    print("\nCurrent routes:")
    for i, (route, path) in enumerate(routes.items(), 1):
        print(f"{i}. '{route}' => '{path}'")
    
    while True:
        choice = input("\nEnter the number of the route to remove (or 0 to cancel): ").strip()
        if choice == '0':
            return routes
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(routes):
                route = list(routes.keys())[index]
                del routes[route]
                print(f"Removed route: '{route}'")
                return OrderedDict(sorted(routes.items(), key=lambda x: x[0], reverse=True))
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def generate_php_code(routes, output_file):
    """Generate the PHP routing code"""
    php_code = f"""<?php
function sitehome_content($template) {{
    $request_uri = $_SERVER['REQUEST_URI'];
    status_header(200);

    $routes = ["""
    
    # Add routes with proper indentation
    for route, path in routes.items():
        php_code += f"""
        '{route}'{' ' * (40 - len(route))}=> '{path}',"""
    
    php_code += """
    ];

   
    
 
    $matched_route = null;
    $matched_path = null;
    $longest_match_length = 0;

    foreach ($routes as $key => $path) {
        if (strpos($request_uri, $key) !== false) {
            // Only consider the most specific (longest) match
            if (strlen($key) > $longest_match_length) {
                $matched_route = $key;
                $matched_path = $path;
                $longest_match_length = strlen($key);
            }
        }
    }

    if ($matched_route !== null) {
        $custom_template = plugin_dir_path(__FILE__) . $matched_path;

        // Set WordPress query vars
        $parts = explode('/', $matched_route);
        set_query_var('active_page_wp_pos', $parts[0]);

        if (isset($parts[1])) {
            set_query_var('active_sub_m', $parts[1]);
        }

        return $custom_template;
    }



    // Handle Home & Front Page separately
    if (is_home() || is_front_page()) {
        $custom_template = plugin_dir_path(__FILE__) . 'public/index.php';
        if (file_exists($custom_template)) {
            set_query_var('active_page_wp_pos', 'dashboard');
            return $custom_template;
        }
    }

    return $template;
}

add_filter('template_include', 'sitehome_content');
?>
"""
    
    with open(output_file, 'w') as f:
        f.write(php_code)
    
    print(f"\n✅ Success! PHP routing file '{output_file}' has been generated/updated.")

def main():
    print("WordPress URL Routing PHP Generator")
    print("-----------------------------------")
    
    # Get the PHP file to edit/create
    php_file = input("Enter PHP filename (e.g., 'url_routing.php'):\n> ").strip()
    
    # Load existing routes if file exists
    routes = load_existing_routes(php_file)
    
    while True:
        print("\nCurrent routes:")
        if routes:
            for i, (route, path) in enumerate(routes.items(), 1):
                print(f"{i}. '{route}' => '{path}'")
        else:
            print("No routes defined yet.")
        
        print("\nOptions:")
        print("1. Add new route(s)")
        print("2. Remove a route")
        print("3. Generate/Update PHP file")
        print("0. Exit")
        
        choice = input("\nSelect an option (0-3): ").strip()
        
        if choice == '1':
            routes = add_route(routes)
        elif choice == '2':
            routes = remove_route(routes)
        elif choice == '3':
            generate_php_code(routes, php_file)
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
