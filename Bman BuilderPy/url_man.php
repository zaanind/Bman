<?php
function sitehome_content($template) {
    $request_uri = $_SERVER['REQUEST_URI'];
    status_header(200);

    $routes = [
        'unauthorized'                            => 'public/unauthorized.php',
        'sys-login'                               => 'public/poslogin.php',
        'prs/add'                                 => 'public/employee_prs_add.php',
        'prs'                                     => 'public/employee_prs_list.php',
        'projects/view'                           => 'public/projects_view.php',
        'projects/stocks/mark_as_checked'         => 'public/stock_mark_as_checked.php',
        'projects/stocks/delete'                  => 'public/projects_stocks_del.php',
        'projects/stocks/add'                     => 'public/projects_stocks_add.php',
        'projects/stocks'                         => 'public/projects_stocks.php',
        'projects/resources'                      => 'public/projects_resources.php',
        'projects/gallery'                        => 'public/projects_gallery.php',
        'projects/edit'                           => 'public/projects_edit.php',
        'projects/delete'                         => 'public/project_delete.php',
        'projects/cost'                           => 'public/projects_cost.php',
        'projects/add'                            => 'public/projects_add.php',
        'projects'                                => 'public/projects.php',
        'payroll'                                 => 'public/payroll.php',
        'orders/start_project'                    => 'public/orders_start_project.php',
        'orders/receipts'                         => 'public/order_receipts.php',
        'orders/quotations/to_invoice'            => 'public/orders_quotations_convert_to_invoice.php',
        'orders/quotations/pdf'                   => 'public/orders_quotations_pdf.php',
        'orders/quotations/edit'                  => 'public/orders_quotations_edit.php',
        'orders/quotations/delete'                => 'public/Orders_Quotations_delete.php',
        'orders/quotations'                       => 'public/orders_quotations.php',
        'orders/purchase-requests/edit'           => 'public/orders_purchase_requests_edit.php',
        'orders/purchase-requests/delete'         => 'public/delete_pr.php',
        'orders/purchase-requests/add'            => 'public/orders_purchase_requests_add.php',
        'orders/purchase-requests'                => 'public/orders_purchase_requests_list.php',
        'orders/pr_to_boq'                        => 'public/pr_to_boq.php',
        'orders/pdf_receipt'                      => 'public/pdf_receipt.php',
        'orders/pdf_invoice'                      => 'public/pdf_invoice.php',
        'orders/edit'                             => 'public/orders_edit.php',
        'orders/delete'                           => 'public/delete_order.php',
        'orders/boqs/view'                        => 'public/orders_boq_view.php',
        'orders/boqs/pdf'                         => 'public/orders_boq_pdf.php',
        'orders/boqs/edit'                        => 'public/orders_boq_edit.php',
        'orders/boqs/delete'                      => 'public/orders_boq_del.php',
        'orders/boqs/boq-to-quotation'            => 'public/boq-to-quotation.php',
        'orders/boqs/add'                         => 'public/orders_boq_add.php',
        'orders/boqs'                             => 'public/orders_boq.php',
        'orders/add'                              => 'public/orders_add.php',
        'orders'                                  => 'public/orders.php',
        'order/paynow'                            => 'public/order_pay.php',
        'logout'                                  => 'public/logout.php',
        'inventory/suppliers/delete'              => 'public/supplier_delete.php',
        'inventory/suppliers/add'                 => 'public/inventory_suppliers_add.php',
        'inventory/suppliers'                     => 'public/inventory_suppliers.php',
        'inventory/products/view'                 => 'public/product_view.php',
        'inventory/products/edit'                 => 'public/product_edit_gpt.php',
        'inventory/products/delete'               => 'public/product_delete.php',
        'inventory/products/add'                  => 'public/inventory_products_add.php',
        'inventory/products'                      => 'public/inventory_products.php',
        'inventory/invoices'                      => 'public/inventory_invoices.php',
        'inventory/company-tools/view'            => 'public/inventory_company_tools_view.php',
        'inventory/company-tools/edit'            => 'public/inventory_comptools_edit.php',
        'inventory/company-tools/delete'          => 'public/company_tools_delete.php',
        'inventory/company-tools/add'             => 'public/inventory_comptools_add.php',
        'inventory/company-tools'                 => 'public/inventory_comptools.php',
        'inventory/company-materials/view'        => 'public/inventory_mets_view.php',
        'inventory/company-materials/edit'        => 'public/inventory_mets_edit.php',
        'inventory/company-materials/delete'      => 'public/company_materials_delete.php',
        'inventory/company-materials/add'         => 'public/inventory_mets_add.php',
        'inventory/company-materials'             => 'public/inventory_mets.php',
        'inventory/categories/delete'             => 'public/category_delete.php',
        'inventory/categories/add'                => 'public/inventory_categories_add.php',
        'inventory/categories'                    => 'public/inventory_categories.php',
        'inventory/brands/delete'                 => 'public/brand_delete.php',
        'inventory/brands/add'                    => 'public/inventory_brands_add.php',
        'inventory/brands'                        => 'public/inventory_brands.php',
        'inventory'                               => 'public/inventory.php',
        'hr/payroll'                              => 'public/hr_payroll.php',
        'hr/my-attendance/mark'                   => 'public/hr_employee_attendance_mark.php',
        'hr/my-attendance'                        => 'public/hr_employee_attendance.php',
        'hr/leaves'                               => 'public/hr_leaves.php',
        'hr/employee-list'                        => 'public/hr_employee_list.php',
        'hr/employee-edit'                        => 'public/hr_edit_employee.php',
        'hr/employee-delete'                      => 'public/delete_employee.php',
        'hr/attendance/approve'                   => 'public/hr_approve_attendence.php',
        'hr/attendance'                           => 'public/hr_admin_attendance.php',
        'hr/add-employee'                         => 'public/hr_add_employee.php',
        'hr'                                      => 'public/hr.php',
        'customers/view'                          => 'public/customers_view.php',
        'customers/edit'                          => 'public/customers_edit.php',
        'customers/delete'                        => 'public/delete_customer.php',
        'customers/add'                           => 'public/customers_add.php',
        'customers'                               => 'public/customers.php',
        'api/customers_api'                       => 'public/api/customers_api.php',
        'accounting/stock_requests/view_stock'    => 'public/stock_view_info.php',
        'accounting/stock_requests/approve'       => 'public/stock_request_approve.php',
        'accounting/stock_requests'               => 'public/stock_request_list.php',
        'accounting/saleries'                     => 'public/saleries_list.php',
        'accounting/sale'                         => 'public/acc_sale.php',
        'accounting/credits/edit'                 => 'public/credits_edit.php',
        'accounting/credits/delete'               => 'public/delete_credit.php',
        'accounting/credits/add'                  => 'public/add_credits.php',
        'accounting/credits'                      => 'public/credits_list.php',
        'accounting/chequebook/view'              => 'public/acc_cheque_view.php',
        'accounting/chequebook/edit'              => 'public/acc_cheque_edit.php',
        'accounting/chequebook/delete'            => 'public/acc_cheque_delete.php',
        'accounting/chequebook/add'               => 'public/acc_cheque_add.php',
        'accounting/chequebook'                   => 'public/acc_cheque.php',
        'accounting/categories/delete'            => 'public/acc_categories_delete.php',
        'accounting/categories/add'               => 'public/acc_categories_add.php',
        'accounting/categories'                   => 'public/acc_categories.php',
        'accounting/cashbook'                     => 'public/acc_cashbook.php',
        'accounting/buy_tool'                     => 'public/acc_buy_tool.php',
        'accounting/buy_material'                 => 'public/acc_buy_material.php',
        'accounting/banks/edit'                   => 'public/acc_banks_edit.php',
        'accounting/banks/add'                    => 'public/banks_add.php',
        'accounting/banks'                        => 'public/acc_banks.php',
        'accounting/account-receiveble'           => 'public/acc_account_receiveble.php',
        'accounting'                              => 'public/admin_accounting.php',
    ];

    	$uq_key = $request_uri;
	
	
    $uq_key_parts = explode('/', trim($uq_key, '/'));
    $best_match_key = null;
    $best_match_score = 0;
	


	
    foreach ($routes as $key => $value) {
    $key_parts = explode('/', $key);
    $current_match_score = 0;

    foreach ($uq_key_parts as $uq_part) {
        if (in_array($uq_part, $key_parts)) {
            $current_match_score++;
        }
    }

    if ($current_match_score > $best_match_score) {
        $best_match_score = $current_match_score;
        $best_match_key = $key;
    } elseif ($current_match_score === $best_match_score && $current_match_score > 0) {
        // If scores are equal, maybe prefer the shorter key (more specific?)
        if (strlen($key) < strlen($best_match_key)) {
            $best_match_key = $key;
        }
    }
   }
    
    if ($best_match_key !== null) {
       // echo "The best matching key for '$uq_key' is '$best_match_key' which points to '$routes[$best_match_key]'.";

	   
	   $key = $best_match_key;
	   $custom_template = plugin_dir_path(__FILE__) . $routes[$best_match_key];
	   $active_page_wp_pos = explode('/', $key)[0];
	   set_query_var('active_page_wp_pos', $active_page_wp_pos);
	   
	   // Handle sub-menus (e.g., inventory/products)
            if (isset(explode('/', $key)[1])) {
                $active_sub_m = explode('/', $key)[1];
                set_query_var('active_sub_m', $active_sub_m);
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
