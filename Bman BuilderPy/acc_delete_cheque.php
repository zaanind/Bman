<?php
// acc_delete_cheque.php - generated script

$homeurl = get_site_url();

if (isset($_GET['id']) && !empty($_GET['id'])) {
    global $wpdb;
    $item_id = intval($_GET['id']); // Ensure ID is an integer to prevent SQL injection

    // Check if the cheque exists
    $sql = $wpdb->prepare("SELECT id FROM wp_zn_system_cheque_book WHERE id = %d;", $item_id);
    $result = $wpdb->get_row($sql);

    if ($result) {
        // Delete the cheque
        $sql = $wpdb->prepare("DELETE FROM wp_zn_system_cheque_book WHERE id = %d;", $item_id);
        $deleted = $wpdb->query($sql);

        if ($deleted !== false) {
            status_header(200);
            wp_redirect($homeurl . '/accounting/chequebook');
            exit;
        } else {
            echo "Error: Deletion failed.";
        }
    } else {
        echo "Cheque not found for ID: " . $item_id;
    }
} else {
    echo 'No ID provided';
}
?>
