odoo.define('ye_dynamic_odoo.EditView', function (require) {
"use strict";

    var core = require('web.core');
    var FormViewEdit = require("ye_dynamic_odoo.FormViewEdit");
    var CalendarEdit = require("ye_dynamic_odoo.CalendarViewEdit");
    var PivotViewEdit = require("ye_dynamic_odoo.PivotViewEdit");
    var ListViewEdit = require("ye_dynamic_odoo.ListViewEdit");
    var GraphViewEdit = require("ye_dynamic_odoo.GraphViewEdit");
    var KanBanViewEdit = require("ye_dynamic_odoo.KanbanViewEdit");
    var ReportKanBan = require("ye_dynamic_odoo.ReportKanBan");
    var ReportEdit = require("ye_dynamic_odoo.ReportEdit");
    var AutomationContent = require("ye_dynamic_odoo.AutomationContent");

    var BasicModel = require('web.BasicModel');

    var mixins = require('web.mixins');
    var BasicView = require('web.BasicView');
    var ActionManager = require('web.ActionManager');
    var session = require('web.session');

    var QWeb = core.qweb;
    var Widget = require('web.Widget');

    var EditBasicView = BasicView.extend({
        init: function (parent, params) {}
    });

    var EditViewModel = BasicModel.extend({
        createNewView: function (data) {
            return this['_rpc']({
                model: "odo.studio",
                method: 'create_new_view',
                args: [data],
                kwargs: {},
            });
        },
        onActionView: function (data, save=true) {
            this['_rpc']({
                model: data.model,
                method: save ? 'store_view' : 'undo_view',
                args: [data.data],
                kwargs: {},
            }).then(function (result) {
                alert("Successfully");
                location.reload();
            });
        },
        getFieldsData: function (modelName) {
            return this['_rpc']({
                model: "odo.studio",
                method: 'get_fields',
                args: [modelName],
                kwargs: {},
            });
        },
        onStoreView: function (data) {
            this.onActionView(data);
        },
        onUndoView: function (data) {
            this.onActionView(data, false);
        }
    });

    var EditView = Widget.extend(mixins.EventDispatcherMixin, {
        template: 'EditView',
        events: {
            'click ._headEdit .fa-close': 'onClose',
            'click ._headEdit .fa-minus': 'onMinus',
            'click ._headEdit .fa-expand': 'onExpand',
            'click ._aSave': 'onSaveView',
            'click ._aUndo': 'onRemoveView',
            'click ._aRemove': 'onRemoveNode',
            'click ._aStore': '_onStoreToDatabase',
        },
        init: function(parent, params) {
            this._super(parent);
            this.props = params;
            // this.controller = parent;
            this.start();
        },
        start: function () {
            this.ref = {};
            this.viewParent = this;
            this.appState = $.bbq.getState(true);
            this.basicView = new EditBasicView(this.viewParent, {});
            this.model = new EditViewModel(this.viewParent);
            this._processFieldsView = this.basicView._processFieldsView.bind(this.basicView);
            this.viewsInfo = {form: {widget: FormViewEdit, label: "FormView", icon: "fa-wpforms", subView: {form: {widget: FormViewEdit}, list: {widget: ListViewEdit}}},
                              list: {widget: ListViewEdit, label: "ListView", icon: "fa-list-ul"},
                              kanban: {widget: KanBanViewEdit, label: "Kanban", icon: "fa-th-large"},
                              calendar: {widget: CalendarEdit, label: "Calendar", icon: "fa-calendar"},
                              pivot: {widget: PivotViewEdit, label: "Pivot", icon: "fa-th"},
                              graph: {widget: GraphViewEdit, label: "KanBan", icon: "fa-bar-chart"},
            };
            this.editType = {views: {label: "Views", classes: "viewEdit", render: this.renderViewViews.bind(this)},
                reports: {label: "Report", classes: "reportEdit", render: this.renderViewReport.bind(this)},
                automation: {label: 'Automations', model: "base.automation", title: "Automated Actions", classes: "accessEdit", render: this.renderViewAccess.bind(this)},
                access_control: {label: 'Access Controls', model: "ir.model.access", title: "Access Control Lists", classes: "accessEdit", render: this.renderViewAccess.bind(this)},
                filter_rules: {label: "Filter Rules", model: "ir.filters", title: "Filter Rules", classes: "accessEdit", render: this.renderViewAccess.bind(this)}
            };
            const viewType = this.appState.view_type;
            this.state = {viewType: viewType in this.viewsInfo ? viewType : "list", typeEdit: "views"};
        },
        setState: function (params) {
            Object.keys(params).map((key) => {
                this.state[key] = params[key];
            });
        },
        _makeDefaultRecord: function (modelName, params) {
            const {res_model} = this.action;
            return this.model._makeDefaultRecord(modelName || res_model, params);
        },
        onClose: function () {
            this.$el.remove();
            this.editToBase();
            this.trigger_up("reset_edit_instance");
        },
        onMinus: function () {
            if (this.$el.hasClass("minus")) {
                this.$el.removeClass("minus");
                this.baseToEdit();
            } else {
                this.$el.addClass("minus");
                this.editToBase();
            }
        },
        onExpand: function () {
            this.$el.hasClass("expand") ? this.$el.removeClass("expand") : this.$el.addClass("expand");
        },
        onSaveView: function () {
            this.model.onStoreView(this.getViewData());
        },
        onRemoveView: function () {
            const {typeEdit} = this.state;
            this.model.onUndoView(typeEdit == "views" ? this.getViewData() : this.getReportData());
        },
        onClickView: function (viewType) {
            this.setState({viewType: viewType});
            this.switchView();
        },
        onClickTypeEdit: function (type) {
            this.setState({typeEdit: type});
            this.renderElement();
        },
        onRemoveNode: function (e) {
            e.stopPropagation();
            this.ref.view.onRemoveNode();
        },
        createNewView: function () {
            return this.model.createNewView(this.prepareNewView());
        },
        getViewState: function (viewId) {
            return this.model.get(viewId)
        },
        getViewData: function () {
            const params = {};
            if (this.ref.subView) {
                const {viewInfo, nodeId} = this.ref.subView, type = viewInfo.type;
                params.model = "odo.studio.sub_view";
                params.data = this.ref.view.getSubViewData(nodeId, type);
                if (type == "form") {
                    params.data.model_name = viewInfo.model;
                    params.data.new_fields = this.ref.subView.prepareNewField();
                }
            }else {
                params.model = "odo.studio";
                params.data = this.ref.view.getData();
            }
            return params;
        },
        getReportData: function () {
            const params = {};
            params.model = "odo.studio.report";
            params.data = this.ref.view.getReportId();
            return params;
        },
        getViewInfo: function () {
            let self = this;
            const {viewType} = this.state;
            if (viewType in self.fieldsViews) {
                let viewInfo = this._processFieldsView(self.fieldsViews[viewType], viewType);
                return  {...viewInfo, fields: {...viewInfo.fields}};
            }
        },
        prepareNewView: function () {
            let {res_model} = this.action, {viewType} = this.state, viewInfo = {view_mode: viewType, action_id: this.action.id}, data = {}, params = {};
            if (viewType == "calendar" && this.fieldsGet) {
                let fieldsDate = Object.keys(this.fieldsGet).filter((fieldName) => {
                    let field = this.fieldsGet[fieldName];
                    return ["date", "datetime"].includes(field.type)
                });
                if (fieldsDate.length) {
                    params.name = fieldsDate[0];
                }
            }
            let viewTemplate = `ViewEdit.${viewType.charAt(0).toUpperCase() + viewType.slice(1)}Default`;
            data.arch = ["calendar"].includes(viewType) ? QWeb.render(viewTemplate, params) : QWeb.templates[viewTemplate].innerHTML;
            data.name = `${res_model}.${viewType}`;
            data.model = res_model;
            viewInfo.data = data;

            return viewInfo;
        },
        reloadProperty: function () {
            this.$el.find('._editProperty ._cCeP').empty().append(this.ref.view.ref.property.$el);
        },
        showSubView: function (node, viewInfo) {
            const {viewType} = this.state, subView = this.viewsInfo[viewType].subView;
            if (viewInfo.type in subView) {
                let View = new subView[viewInfo.type].widget(this, {viewInfo: viewInfo, _processFieldsView: this._processFieldsView,
                    action: this.action, editView: this, rootViewType: viewType,
                    nodeId: node.nodeId, parent_view_id: this.getViewInfo().view_id || false});
                this.ref.subView = View;
                this.ref.view.disableSort();
                this.$el.addClass("_showSubView");
                this.$el.find('._editView ._wSubView').addClass("show").append(View._renderContent());
                this.$el.find('._editProperty ._cCeP').empty().append(View._renderProperty());
            }
        },
        closeSubView: function (e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            const nodeId = this.ref.subView.nodeId, subViewType = this.ref.subView.viewInfo.type;
            $(e.currentTarget).empty().removeClass("show");
            this.$el.removeClass("_showSubView");
            delete this.ref.subView;
            this.ref.view.onCloseSubView(nodeId, subViewType);
            this.ref.view._renderProperty(true);
            this.ref.view.enableSort();
            if (nodeId) {
                this.ref.view.ref.content.reloadNode(nodeId);
            }
        },
        switchView: function () {
            const self = this, {viewType} = this.state;
            if (viewType in self.fieldsViews) {
                const viewInfo = this.getViewInfo();
                if (!this.fieldsGet) {
                    this.fieldsGet = viewInfo.fieldsGet;
                }
                this.ref.view = new this.viewsInfo[viewType].widget(this.viewParent,
                    {
                        editView: this,
                        action: this.action,
                        _processFieldsView: this._processFieldsView,
                        rootViewType: viewType,
                        reloadProperty: this.reloadProperty.bind(this),
                        viewInfo: viewInfo,
                        // controller: this.controller,
                        showSubView: this.showSubView.bind(this)
                    });
                this.$el.find('._editView ._wMainView').empty().append(this.ref.view._renderContent());
                this.$el.find('._editProperty ._cCeP').empty().append(this.ref.view._renderProperty());
                this.$el.attr({'view-type': viewType});
            }else {
                if (window.confirm("Do you really want to active view ?")) {
                    this.createNewView().then(() => {
                        self.renderElement();
                    });
                }
            }
        },
        editToBase: function () {
            $('.o_web_client').removeClass("editMode");
            $('.o_menu_systray').removeClass("hide");
            $('.edit_menu_top').remove();
        },
        baseToEdit: function () {
            $(".edit_menu_top").remove();
            let menuTop = $(QWeb.render("Edit.MenuTop", {}));
            menuTop.find("li").click(this.onClose.bind(this));
            $('.o_main_navbar').append(menuTop);
            $(".o_content").addClass("_overHide");
            $(".o_web_client").addClass("editMode");
            $(".o_menu_systray").addClass("hide");
        },
        bindStyle: function () {
            $("._wIBi, ._editProperty").removeClass("hide");
        },
        bindAction: function () {
            this.$el.find("._wSubView").click(this.closeSubView.bind(this));
            this.$el.find("._aRemove").click(this.onRemoveNode.bind(this));
        },
        renderMenuView: function () {
            const {viewType} = this.state;
            let wrap = this.$el.find('._hEView'), wrapUl = $(QWeb.render("EditView.menu", {}))
            Object.keys(this.viewsInfo).map((type) => {
                let view = this.viewsInfo[type], item = $(QWeb.render("EditView.menuItem", {...view}));
                if (type == viewType) {
                    item.addClass("active");
                }
                if (!(type in this.fieldsViews)) {
                    item.addClass("notAvailable")
                }
                item.click(() => {
                    wrapUl.find("li.active").removeClass("active");
                    item.addClass("active");
                    this.onClickView(type);
                });
                wrapUl.append(item);
            });
            wrap.append(wrapUl);
        },
        renderMenu: function () {
            const {typeEdit} = this.state, wrap = this.$el.find('._hEView'),
                wrapUl = $(QWeb.render("EditView.menu", {}));
            wrapUl.addClass("_wrapEditType");
            Object.keys(this.editType).map((type) => {
                let typeInfo = this.editType[type], item = $(QWeb.render("EditView.menuItem", {...typeInfo}));
                if (type == typeEdit) {
                    item.addClass("active");
                }
                item.click(() => {
                    wrapUl.find("li.active").removeClass("active");
                    item.addClass("active");
                    this.onClickTypeEdit(type);
                });
                wrapUl.append(item);
            });
            wrap.append(wrapUl);
        },
        renderViewAccess: function () {
            const self = this, {typeEdit} = this.state, {model, title} = this.editType[typeEdit],
                container = self.$el.find("._wMainView").empty();
            this.viewParent.loadViews(model, session.user_context, [[false, 'list'], [false, 'form']]).then((viewInfo) => {
                const automationContent = new AutomationContent(this.viewParent, {modelName: model, viewInfo: viewInfo,
                    title: title, domain: [['model_name', '=', self.appState.model]]});
                automationContent.renderElement();
                container.append(automationContent.$el);
            });
        },
        renderViewReport: function () {
            const self = this, action_manager = new ActionManager(this.viewParent, session.user_context);
            const domain = self.action.domain || [];
            action_manager.isInDOM = true;
            action_manager._loadAction("base.ir_action_report", {}).then(function (action) {
                action_manager._preprocessAction(action, {});
                action_manager._loadViews(action).then((fieldsViews) => {
                    const viewInfo = self._processFieldsView(fieldsViews["kanban"], "kanban");
                    let reportEdit = new ReportEdit(self.viewParent,
                        {action: action, domain: domain, action_manager: action_manager, reloadProperty: self.reloadProperty.bind(self),
                            viewInfo: {...viewInfo, fields: {...viewInfo.fields}}});
                    reportEdit.attachTo(self.$el.find('._editView')).then(function () {
                        self.$el.find('._editView ._wMainView').empty().append(reportEdit._renderContent());
                        self.$el.find('._editProperty ._cCeP').empty().append(reportEdit._renderProperty());
                    });
                    self.ref.view = reportEdit;
                });
            });
        },
        renderViewViews: function () {
            const self = this, state = $.bbq.getState(true);
            this.action_manager = new ActionManager(this.viewParent, session.user_context);
            this.action_manager.isInDOM = true;
            this.action_manager.doAction = function (action, options) {
                const props = {
                    from_odo_studio: Math.random(),
                    active_id: options.additional_context.active_id,
                    active_ids: options.additional_context.active_ids,
                    active_model: options.additional_context.active_model,
                }
                return self.action_manager._loadAction(action, props).then(function (action) {
                    self.action_manager._preprocessAction(action, options);
                    return action;
                });
            };
            this.action_manager.loadState(state).then(function (action) {
                self.action = action;
                self.action.context = {...action.context, from_odo_studio: Math.random()}
                self.action_manager._loadViews(action).then((fieldsViews) => {
                    self.fieldsViews = fieldsViews;
                    self.renderMenuView();
                    self.switchView();
                    self.bindStyle();
                    self.bindAction();
                });
            });
        },
        renderView: function () {
            const {typeEdit} = this.state, {classes, render} = this.editType[typeEdit];
            this.$el.find('._hEView ._ulView').remove();
            this.$el.removeClass().addClass(`wrapEdit ${classes}`);
            this.renderMenu();
            render();
            this.baseToEdit();
        },
        reload: function (parent) {
            const state = $.bbq.getState(true);
            this.appState = state;
            this.viewParent = parent;
            this.editToBase();
            this.setState({viewType: state.view_type in this.viewsInfo ? state.view_type : "list"});
            this.basicView = new EditBasicView(this.viewParent, {});
            this.model = new EditViewModel(this.viewParent);
            this.renderElement();
        },
        renderElement: function () {
            this._super();
            this.renderView();
            this.baseToEdit();
        }
    });

    return EditView;
});
