import os
import re
import json
from collections import OrderedDict

def parse_existing_menu(file_path):
    """Parse an existing menu PHP file into a structured format"""
    menu = {
        'main_items': [],
        'submenus': OrderedDict()
    }
    
    if not os.path.exists(file_path):
        return menu
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # First pass - identify all main menu items
    main_item_pattern = r'<li class="sidebar-item .*?<\s*?\/li>'
    for match in re.finditer(main_item_pattern, content, re.DOTALL):
        item_html = match.group(0)
        active_page = re.search(r'\$active_page==[\'"](.*?)[\'"]', item_html)
        href = re.search(r'href=[\'"](.*?)[\'"]', item_html)
        icon = re.search(r'data-feather=[\'"](.*?)[\'"]', item_html)
        text = re.search(r'<span class="align-middle">(.*?)<\/span>', item_html)
        
        if active_page and href and icon and text:
            menu['main_items'].append({
                'active_page': active_page.group(1),
                'url': href.group(1).replace(get_site_url_placeholder(), ''),
                'icon': icon.group(1),
                'text': text.group(1)
            })
    
    # Second pass - identify submenus and their items
    submenu_pattern = r'<\?php if \(.*?\$active_page==[\'"](.*?)[\'"]\)\{ \?>(.*?)<\?php \} \?>'
    for match in re.finditer(submenu_pattern, content, re.DOTALL):
        active_page = match.group(1)
        submenu_content = match.group(2)
        
        # Verify this active_page exists in main_items
        if not any(item['active_page'] == active_page for item in menu['main_items']):
            continue  # Skip if not a valid main menu item
        
        submenu_items = []
        subitem_pattern = r'<li class="sidebar-item .*?<\s*?\/li>'
        for sub_match in re.finditer(subitem_pattern, submenu_content, re.DOTALL):
            item_html = sub_match.group(0)
            active_sub = re.search(r'\$active_sub_m==[\'"](.*?)[\'"]', item_html)
            href = re.search(r'href=[\'"](.*?)[\'"]', item_html)
            icon = re.search(r'data-feather=[\'"](.*?)[\'"]', item_html)
            text = re.search(r'<span class="align-middle">(.*?)<\/span>', item_html)
            
            if active_sub and href and icon and text:
                submenu_items.append({
                    'active_sub': active_sub.group(1),
                    'url': href.group(1).replace(get_site_url_placeholder(), ''),
                    'icon': icon.group(1),
                    'text': text.group(1)
                })
        
        if submenu_items:
            menu['submenus'][active_page] = submenu_items
    
    return menu

def get_site_url_placeholder():
    return '<?php echo get_site_url(); ?>'

def generate_menu_php(menu_config):
    """Generate the PHP menu code from the configuration"""
    php_code = """<ul class="sidebar-nav">
        <li class="sidebar-header">
            System
        </li>
"""
    
    # Generate main menu items
    for item in menu_config['main_items']:
        php_code += f"""
        <li class="sidebar-item <?php if ($active_page=='{item['active_page']}'){{echo 'active';}}?>">
            <a class="sidebar-link" href="{get_site_url_placeholder()}{item['url']}">
                <i class="align-middle" data-feather="{item['icon']}"></i> <span class="align-middle">{item['text']}</span>
            </a>
        </li>
"""
    
    # Generate submenus
    for active_page, submenu_items in menu_config['submenus'].items():
        php_code += f"""
        <?php if ($active_page=='{active_page}') {{ ?>
        <li class="sidebar-header">
            Menu
        </li>
"""
        for item in submenu_items:
            php_code += f"""
        <li class="sidebar-item <?php if ($active_sub_m=='{item['active_sub']}'){{echo 'active';}}?>">
            <a class="sidebar-link" href="{get_site_url_placeholder()}{item['url']}">
                <i class="align-middle" data-feather="{item['icon']}"></i> <span class="align-middle">{item['text']}</span>
            </a>
        </li>
"""
        php_code += """
        <?php } ?>
"""
    
    php_code += """
    </ul>"""
    
    return php_code

def show_main_menu_items(menu_config):
    print("\nCurrent Main Menu Items:")
    for i, item in enumerate(menu_config['main_items'], 1):
        print(f"{i}. {item['text']} ({item['active_page']})")

def show_submenu_items(menu_config, active_page):
    if active_page not in menu_config['submenus']:
        print(f"No submenu exists for {active_page}")
        return []
    
    print(f"\nCurrent Submenu Items for {active_page}:")
    for i, item in enumerate(menu_config['submenus'][active_page], 1):
        print(f"{i}. {item['text']} ({item['active_sub']})")
    
    return menu_config['submenus'][active_page]

def add_main_menu_item(menu_config):
    print("\nAdd New Main Menu Item:")
    item = {
        'active_page': input("Active page variable (e.g., 'dashboard', 'inventory'): ").strip(),
        'url': input("URL path (e.g., '/', '/inventory'): ").strip(),
        'icon': input("Feather icon name (e.g., 'sliders', 'box'): ").strip(),
        'text': input("Menu text (e.g., 'Dashboard', 'Inventory'): ").strip()
    }
    menu_config['main_items'].append(item)
    return menu_config

def add_submenu_item(menu_config):
    print("\nAdd New Submenu Item:")
    active_page = input("For which main menu? (enter active_page value): ").strip()
    
    if active_page not in menu_config['submenus']:
        create = input(f"No submenu exists for {active_page}. Create one? (y/n): ").strip().lower()
        if create != 'y':
            return menu_config
        menu_config['submenus'][active_page] = []
    
    item = {
        'active_sub': input("Active submenu variable (e.g., 'products', 'brands'): ").strip(),
        'url': input(f"URL path (e.g., '/{active_page}/products'): ").strip(),
        'icon': input("Feather icon name (e.g., 'box', 'bold'): ").strip(),
        'text': input("Menu text (e.g., 'Products', 'Brands'): ").strip()
    }
    menu_config['submenus'][active_page].append(item)
    return menu_config

def remove_menu_item(menu_config):
    print("\n1. Remove main menu item")
    print("2. Remove submenu item")
    choice = input("Select option (1-2): ").strip()
    
    if choice == '1':
        show_main_menu_items(menu_config)
        if not menu_config['main_items']:
            return menu_config
        
        index = input("Enter number of item to remove (or 0 to cancel): ").strip()
        try:
            index = int(index) - 1
            if 0 <= index < len(menu_config['main_items']):
                removed = menu_config['main_items'].pop(index)
                print(f"Removed: {removed['text']}")
                
                # Also remove any associated submenu
                if removed['active_page'] in menu_config['submenus']:
                    del menu_config['submenus'][removed['active_page']]
                    print(f"Also removed submenu for {removed['active_page']}")
        except ValueError:
            print("Invalid input")
    
    elif choice == '2':
        active_page = input("Enter main menu active_page value: ").strip()
        if active_page not in menu_config['submenus']:
            print(f"No submenu exists for {active_page}")
            return menu_config
        
        submenu_items = show_submenu_items(menu_config, active_page)
        if not submenu_items:
            return menu_config
        
        index = input("Enter number of item to remove (or 0 to cancel): ").strip()
        try:
            index = int(index) - 1
            if 0 <= index < len(menu_config['submenus'][active_page]):
                removed = menu_config['submenus'][active_page].pop(index)
                print(f"Removed: {removed['text']}")
                
                # Remove submenu entirely if last item
                if not menu_config['submenus'][active_page]:
                    del menu_config['submenus'][active_page]
                    print(f"Submenu for {active_page} is now empty and has been removed")
        except ValueError:
            print("Invalid input")
    
    return menu_config

def edit_menu_item(menu_config):
    print("\n1. Edit main menu item")
    print("2. Edit submenu item")
    choice = input("Select option (1-2): ").strip()
    
    if choice == '1':
        show_main_menu_items(menu_config)
        if not menu_config['main_items']:
            return menu_config
        
        index = input("Enter number of item to edit (or 0 to cancel): ").strip()
        try:
            index = int(index) - 1
            if 0 <= index < len(menu_config['main_items']):
                item = menu_config['main_items'][index]
                print(f"\nEditing: {item['text']}")
                print("Leave field blank to keep current value")
                
                new_active = input(f"Active page [{item['active_page']}]: ").strip()
                new_url = input(f"URL path [{item['url']}]: ").strip()
                new_icon = input(f"Icon [{item['icon']}]: ").strip()
                new_text = input(f"Text [{item['text']}]: ").strip()
                
                if new_active: item['active_page'] = new_active
                if new_url: item['url'] = new_url
                if new_icon: item['icon'] = new_icon
                if new_text: item['text'] = new_text
                
                print("Item updated")
        except ValueError:
            print("Invalid input")
    
    elif choice == '2':
        active_page = input("Enter main menu active_page value: ").strip()
        if active_page not in menu_config['submenus']:
            print(f"No submenu exists for {active_page}")
            return menu_config
        
        submenu_items = show_submenu_items(menu_config, active_page)
        if not submenu_items:
            return menu_config
        
        index = input("Enter number of item to edit (or 0 to cancel): ").strip()
        try:
            index = int(index) - 1
            if 0 <= index < len(menu_config['submenus'][active_page]):
                item = menu_config['submenus'][active_page][index]
                print(f"\nEditing: {item['text']}")
                print("Leave field blank to keep current value")
                
                new_active = input(f"Active submenu [{item['active_sub']}]: ").strip()
                new_url = input(f"URL path [{item['url']}]: ").strip()
                new_icon = input(f"Icon [{item['icon']}]: ").strip()
                new_text = input(f"Text [{item['text']}]: ").strip()
                
                if new_active: item['active_sub'] = new_active
                if new_url: item['url'] = new_url
                if new_icon: item['icon'] = new_icon
                if new_text: item['text'] = new_text
                
                print("Item updated")
        except ValueError:
            print("Invalid input")
    
    return menu_config

def main():
    print("WordPress Menu Generator/Editor")
    print("------------------------------")
    
    # Get the PHP file to edit/create
    php_file = input("Enter PHP filename (e.g., 'sidebar-menu.php'):\n> ").strip()
    
    # Load existing menu if file exists
    menu_config = parse_existing_menu(php_file)
    
    while True:
        print("\nCurrent Menu Structure:")
        show_main_menu_items(menu_config)
        for active_page in menu_config['submenus']:
            show_submenu_items(menu_config, active_page)
        
        print("\nOptions:")
        print("1. Add main menu item")
        print("2. Add submenu item")
        print("3. Remove menu item")
        print("4. Edit menu item")
        print("5. Generate/Update PHP file")
        print("0. Exit")
        
        choice = input("\nSelect an option (0-5): ").strip()
        
        if choice == '1':
            menu_config = add_main_menu_item(menu_config)
        elif choice == '2':
            menu_config = add_submenu_item(menu_config)
        elif choice == '3':
            menu_config = remove_menu_item(menu_config)
        elif choice == '4':
            menu_config = edit_menu_item(menu_config)
        elif choice == '5':
            php_code = generate_menu_php(menu_config)
            with open(php_file, 'w') as f:
                f.write(php_code)
            print(f"\n✅ Success! Menu file '{php_file}' has been generated/updated.")
            
            # Save config for future editing
            config_file = php_file.replace('.php', '.config.json')
            with open(config_file, 'w') as f:
                json.dump(menu_config, f, indent=2)
            print(f"✅ Configuration saved to '{config_file}' for future editing.")
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
