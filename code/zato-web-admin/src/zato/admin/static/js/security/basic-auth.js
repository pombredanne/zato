
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.BasicAuth = new Class({
    toString: function() {
        var s = '<BasicAuth id:{0} name:{1} username:{2} realm:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.username ? this.username : '(none)',
                                this.realm ? this.realm : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.BasicAuth;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.basic_auth.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username', 'realm']);
})


$.fn.zato.security.basic_auth.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new HTTP Basic Auth definition', null);
}

$.fn.zato.security.basic_auth.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the HTTP Basic Auth definition', id);
}

$.fn.zato.security.basic_auth.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', item.realm);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.basic_auth.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.basic_auth.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.basic_auth.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HTTP Basic Auth definition [{0}] deleted',
        'Are you sure you want to delete the HTTP Basic Auth definition [{0}]?',
        true);
}
