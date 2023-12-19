odoo.define('ye_dynamic_odoo.AutomationContent', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var FormView = require('web.FormView');
    var FormController = require('web.FormController');
    var Bus = require('web.Bus');
    var ControlPanel = require('web.ControlPanel');
    var WidgetBase = require('ye_dynamic_odoo.FieldBasic').WidgetBase;

    FormView.include({
        init: function (viewInfo, params) {
            this._super(viewInfo, params);
            const {fromStudio} = params;
            this.controllerParams.fromStudio = fromStudio;
        },
    });

    FormController.include({
        init: function (parent, model, renderer, params) {
            this._super(parent, model, renderer, params);
            this.props = params;
        },
        _updateEnv: function () {
            const {fromStudio} = this.props;
            if (!fromStudio) {
                this._super();
            }
        },
        _pushState: function (state) {
            const {fromStudio} = this.props;
            if (!fromStudio) {
                this._super(state);
            }
        },
    });

    ListView.include({
        init: function (viewInfo, params) {
            this._super(viewInfo, params);
            const {fromStudio, onOpenRecord} = params;
            this.controllerParams.fromStudio = fromStudio;
            this.controllerParams.onOpenRecord = onOpenRecord;
        },
    });

    ListController.include({
        init: function (parent, model, renderer, params) {
            this._super(parent, model, renderer, params);
            this.props = params;
        },
        _updateEnv: function () {
            const {fromStudio} = this.props;
            if (!fromStudio) {
                this._super();
            }
        },
        _pushState: function (state) {
            const {fromStudio} = this.props;
            if (!fromStudio) {
                this._super(state);
            }
        },
        _onOpenRecord: function (ev) {
            ev.stopPropagation();
            const {fromStudio, onOpenRecord} = this.props;
            if (fromStudio && onOpenRecord) {
                var record = this.model.get(ev.data.id, {raw: true});
                return onOpenRecord(record.res_id);
            }
            this._super(ev);
        },
        _onCreateRecord: function (ev) {
            if (ev) {
                ev.stopPropagation();
            }
            const {fromStudio, onOpenRecord} = this.props;
            if (fromStudio && onOpenRecord) {
                return onOpenRecord(false);
            }
            this._super(ev);
        },
    });


    var AutomationView = WidgetBase.extend({
        template: "Studio.ControlView",
        custom_events: _.extend({}, WidgetBase.prototype.custom_events, {
            stOpenRecord: 'openRecord',
        }),
        init: function (parent, params) {
            this._super(parent, params);
            this.views = {list: {title: 'List', render: this.renderListView.bind(this)}, form: {render: this.renderFormView.bind(this)}};
            this.state = {viewInfo: false, viewType: 'list'};
        },
        openRecord: function (res_id) {
            this.setState({viewType: 'form', res_id: res_id});
            this.renderView();
        },
        renderListView: function () {
            const self = this, {modelName, title, viewInfo, domain} = this.props;
            // var $content = $('<div>').addClass('o_content').appendTo($web_client);

          /*  if (params.interceptsPropagate) {
                _.each(params.interceptsPropagate, function (cb, name) {
                    testUtilsMock.intercept(widget, name, cb, true);
                });
            }*/

            const listView = new ListView(viewInfo.list, {
                viewInfo: viewInfo,
                context: session.user_context,
                domain: domain || [],
                groupBy: [],
                limit: 80,
                filter: [],
                modelName: modelName,
                displayName: title,
                fromStudio: true,
                withControlPanel: true,
                withSearchPanel: true,
                searchView: true,
                onOpenRecord: this.openRecord.bind(this),
            });
            var controlPanel = new ControlPanel(listView);
            controlPanel.appendTo(self.$el.find(".controlPanel"));
            listView.getController(self).then(function (widget) {
                self.ref.view = widget;
                widget.set_cp_bus(controlPanel.get_bus());
                widget.appendTo(self.$el.find(".viewContent").empty()).then(() => {
                    self.bindAction();
                });
            });
        },
        renderFormView: function () {
            const self = this, {modelName, viewInfo} = this.props, {res_id} = this.state;
            const formView = new FormView(viewInfo.form, {
                modelName: modelName,
                context: session.user_context,
                ids: res_id ? [res_id] : [],
                currentId: res_id || undefined,
                index: 0,
                fromStudio: true,
                mode: res_id ? 'readonly' : 'edit',
            });
            var controlPanel = new ControlPanel(formView);
            formView.getController(self).then(function (widget) {
                self.ref.view = widget;
                controlPanel.appendTo(self.$el.find(".controlPanel").empty());
                widget.set_cp_bus(controlPanel.get_bus());
                widget.appendTo(self.$el.find(".viewContent").empty().addClass("hide")).then(() => {
                    self.$el.find(".viewContent").removeClass("hide");
                    self.bindAction();
                });
            });
        },
        renderView: async function () {
            var {viewType} = this.state;
            this.views[viewType].render();
        }
    });

    return AutomationView;

});
