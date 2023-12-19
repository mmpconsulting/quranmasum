odoo.define('ye_dynamic_odoo.AbstractWebClient', function (require) {
"use strict";

    var WebClient = require('web.WebClient');
    var config = require('web.config');
    var core = require('web.core');
    var data_manager = require('web.data_manager');
    var dom = require('web.dom');
    var Menu = require('web.Menu');
    var session = require('web.session');

    WebClient.include({
        custom_events: _.extend({}, WebClient.prototype.custom_events, {
            reset_edit_instance: 'resetEditInstance',
        }),
        resetEditInstance: function () {
            if (this.editInstance) {
                delete this.loadEdit;
                delete this.editInstance;
            }
        },
        on_menu_clicked: function (ev) {
            if (this.editInstance) {
                this.loadEdit = true;
            }
            this._super(ev);
        },
        on_app_clicked: function (ev) {
            if (this.editInstance) {
                this.loadEdit = true;
            }
            return this._super(ev);
        },
        do_push_state: function (state) {
            this._super(state);
            if (this.editInstance && this.loadEdit) {
                delete this.loadEdit;
                this.editInstance.reload(this);
            }
        },
    });
});
