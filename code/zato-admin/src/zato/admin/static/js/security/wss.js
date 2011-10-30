
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.WSS = new Class({
	toString: function() {
		var s = '<WSS id:{0} name:{1} is_active:{2}>';
		return String.format(s, this.id ? this.id : '(none)', 
								this.name ? this.name : '(none)', 
								this.is_active ? this.is_active : '(none)');
	}
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() { 
	$('#data-table').tablesorter(); 
	$.fn.zato.data_table.class_ = $.fn.zato.data_table.WSS;
	$.fn.zato.data_table.new_row_func = $.fn.zato.security.wss.data_table.new_row;
	$.fn.zato.data_table.parse();
	$.fn.zato.data_table.setup_forms(['name']);
})

$.fn.zato.security.wss.create = function() {
	$.fn.zato.data_table._create_edit('create', 'Create a new WS-Security definition', null);
}

$.fn.zato.security.wss.edit = function(id) {
	$.fn.zato.data_table._create_edit('edit', 'Update the WS-Security definition', id);
}

$.fn.zato.security.wss.data_table.new_row = function(item, data, include_tr) {
    var row = '';
	
	if(include_tr) {
		row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
	}
	
	row += "<td class='numbering'>&nbsp;</td>";
	row += "<td><input type='checkbox' /></td>";
	row += String.format('<td>{0}</td>', item.name);
	row += String.format('<td>{0}</td>', item.is_active ? 'Yes' : 'No');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.wss.edit('{0}')\">Edit</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.wss.delete_({0});'>Delete</a>", item.id));
	row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
	row += String.format("<td class='ignore'>{0}</td>", item.is_active);
	row += String.format("<td class='ignore'>{0}</td>", '');
	row += String.format("<td class='ignore'>{0}</td>", '');
	row += String.format("<td class='ignore'>{0}</td>", '');
	
	if(include_tr) {
		row += '</tr>';
	}
	
	return row;
}

$.fn.zato.security.wss.delete_ = function(id) {
	$.fn.zato.data_table.delete_(id, 'td.item_id_', 
		'Technical account [{0}] deleted', 
		'Are you sure you want to delete the technical account [{0}]?');
}
