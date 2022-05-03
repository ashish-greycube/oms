//  for navigating between modules
$('body').on('click', 'a', function(e) {
    let oms_route=frappe.get_route()
    if (oms_route.length==2 && oms_route[0]=='Workspaces' && oms_route[1]=='OMS'){
        setTimeout(() => {
            get_so_count()
        }, 600);
    }
});
//  for first time load
$( document ).ready(function() {
    // Handler for .ready() called.
    setTimeout(() => {
        get_so_count()
    }, 1500);
  });


function get_so_count() {
   
    frappe.call('oms.oms.report.problematic_report_count.problematic_report_count.get_so_count', {
        warehouse: 1
    }).then(r => {
        console.log(r.message)
        $('div .indicator-pill.ellipsis.gray').text(function () {return $(this).text().replace("0 to submit", r.message[0]+ " to submit"); }); 
    })           
    frappe.call('oms.oms.report.problematic_report_count.problematic_report_count.get_so_count', {
        warehouse: 0
    }).then(r => {
        console.log(r.message)
        $('div .indicator-pill.ellipsis.gray').text(function () {return $(this).text().replace("0 problematic orders", r.message[0]+ " problematic orders"); }); 
    })   
}