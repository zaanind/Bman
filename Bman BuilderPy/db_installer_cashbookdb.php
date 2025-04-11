<?php
// cashbookdb.php - WordPress table creation script

function zn_sys_cashbook_create_table() {
    global $wpdb;
    $charset_collate = $wpdb->get_charset_collate();
    $full_table_name = $wpdb->prefix . 'zn_sys_cashbook';
    
    $sql = "CREATE TABLE $full_table_name (
        id INT AUTO_INCREMENT NOT NULL,
        date DATE DEFAULT CURRENT_TIMESTAMP,
        text TEXT,
        payee TEXT,
        class TEXT,
        payment FLOAT,
        n LONGTEXT,
        deposit FLOAT,
        balance FLOAT,
        PRIMARY KEY (id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
    
    // Add version option to track updates
   // add_option('zn_sys_cashbook_db_version', '1.0');
}


zn_sys_cashbook_create_table();

?>
