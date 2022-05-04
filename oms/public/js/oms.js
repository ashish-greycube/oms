$(document).on('startup', function () {
    // Monkey patch workspace.show to reset link url
    if (frappe.workspace) {
        let original_show = frappe.workspace.show;
        frappe.workspace.show = function () {
            original_show.apply(this, arguments);
            if (frappe.desk_page.page_name == "OMS") {
                frappe.call({
                    method: "oms.oms_sales_order_controller.get_all_so_count",
                    callback: function (r, rt) {
                        setTimeout(() => {
                            $('div.widget-title:contains("Problematic Orders")').closest('.shortcut-widget-box').off('click').find('.indicator-pill').html(
                                '<div style="color:red"><b>' + r.message[0].count + "</b> orders</div>")
                            $('div.widget-title:contains("To Submit")').closest('.shortcut-widget-box').off('click').find('.indicator-pill').html(
                                '<div style="color:brown"><b>' + r.message[1].count + "</b> orders</div>")
                        }, 300);
                    }
                });
            }
        }
    }
});

$(document).ready(function () {
    setTimeout(() => {
        if (frappe.workspace) {
            if (frappe.desk_page.page_name == "OMS") {
                frappe.call({
                    method: "oms.oms_sales_order_controller.get_all_so_count",
                    callback: function (r, rt) {
                        setTimeout(() => {
                            $('div.widget-title:contains("Problematic Orders")').closest('.shortcut-widget-box').off('click').find('.indicator-pill').html(
                                '<div style="color:red"><b>' + r.message[0].count + "</b> orders</div>")
                            $('div.widget-title:contains("To Submit")').closest('.shortcut-widget-box').off('click').find('.indicator-pill').html(
                                '<div style="color:brown"><b>' + r.message[1].count + "</b> orders</div>")
                        }, 100);
                    }
                });
            }
        }
    }, 1700);
})