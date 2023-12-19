from odoo import models, api, fields
from odoo.addons.base.models import ir_ui_view
from odoo.tools.safe_eval import safe_eval
from odoo.osv import orm
# from odoo.tools import ConstantMapping

super_transfer_node_to_modifiers = orm.transfer_node_to_modifiers

def inherit_transfer_node_to_modifiers(node, modifiers, context=None, in_tree_view=False):
    super_transfer_node_to_modifiers(node, modifiers, context=context, in_tree_view=in_tree_view)
    if context.get("DynamicOdo", False):
        for a in ('invisible', 'readonly', 'required'):
            if node.get(a):
                v = bool(safe_eval(node.get(a), {'context': context or {}}))
                if in_tree_view and a == 'invisible':
                    a = "column_invisible"
                modifiers[a] = v

orm.transfer_node_to_modifiers = inherit_transfer_node_to_modifiers


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _apply_group(self, model, node, modifiers, fields):
        groups = node.get('groups')
        res = super(IrUiView, self)._apply_group(model, node, modifiers, fields)
        if self.env.context.get("from_odo_studio", False) and groups:
            node.set('groups', groups)
        return res

    def read_combined(self, fields=None):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        res = super(IrUiView, self.with_context(inherit_branding=True) if from_odo_studio else self).read_combined(fields=fields)
        return res

    def read(self, fields=None, load='_classic_read'):
        report_id = self.env.context.get("REPORT_ID", False)
        res = super(IrUiView, self).read(fields=fields, load=load)
        if len(self) == 1 and self.type == "qweb" and report_id:
            template = self.env['odo.studio.report'].search([['view_id', '=', self.id], ['report_id', '=', report_id]], limit=1)
            if len(template):
                for view in res:
                    view['arch'] = template.xml
        return res

    def _pop_view_branding(self, element):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            movable_branding = ['data-oe-model', 'data-oe-id', 'data-oe-field', 'data-oe-xpath', 'data-oe-source-id']
            distributed_branding = dict(
                    (attribute, element.get(attribute)) for attribute in movable_branding if element.get(attribute))
            return distributed_branding
        else:
            return super(IrUiView, self)._pop_view_branding(element)


IrUiView()


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    model_id = fields.Many2one(string="Model", comodel_name="ir.model")

    @api.model
    def create_new_app(self, values):
        app_name = values.get("app_name", False)
        menu_root = values.get("root_name", False)
        if app_name:
            parent_menu = self.create({'name': app_name, 'parent_id': False, 'sequence': 100})
            if menu_root:
                parent_menu = self.create({'name': menu_root, 'parent_id': parent_menu.id, 'sequence': 1})
            values['parent_id'] = parent_menu.id
            values['sequence'] = 1
            if values.get("model_name", False):
                self.create_new_model(values)
            else:
                self.create(values)


    @api.model
    def create_new_model(self, values):
        model_description = values.get("model_description", False)
        model_name = values.get("model_name", False)
        menu_name = values.get("name", False)
        menu_parent = values.get("parent_id", False)
        if model_name:
            # create new model
            model_values = {'name': model_description, 'model': model_name, 'state': 'manual',
                            'is_mail_thread': True, 'is_mail_activity': True,
                            'access_ids': [(0, 0, {'name': 'Group No One', 'group_id':
                                self.env.ref('base.group_no_one').id, "perm_read": True, "perm_write": True, "perm_create": True, "perm_unlink": True})]}
            self.env['ir.model'].create(model_values)
            # create action window
            action_window_values = {'name': 'New Model', 'res_model': model_name,
                                    'view_mode': "tree,form", 'target': 'current', 'view_id': False}
            action_id = self.env['ir.actions.act_window'].create(action_window_values)
            # create tree view
            view_data = {"arch": "<tree><field name='id' /></tree>", "model": model_name,
                         "name": "{model}.tree ".format(model=model_name)}
            view_id = self.env['odo.studio'].create_new_view(
                {'view_mode': 'tree', 'action_id': action_id.id, "data": view_data})
            # create form view
            view_data = {"arch": "<form><header></header><sheet><field name='id' invisible='True' /></sheet></form>", "model": model_name,
                         "name": "{model}.form ".format(model=model_name)}
            self.env['odo.studio'].create_new_view({'view_mode': 'form', 'action_id': action_id.id, "data": view_data})
            # create menu
            self.create({'name': menu_name, 'parent_id': menu_parent, 'action': '%s,%s' % ('ir.actions.act_window', action_id.id)})
            # create model data
            self.env['ir.model.data'].create({
                'module': 'ye_studio',
                'name': view_data['name'],
                'model': 'ir.ui.view',
                'res_id': view_id.id,
            })

    @api.model_create_multi
    def create(self, values):
        for value in values:
            if 'new_view' in value:
                del value['new_view']
        res = super(IrUiMenu, self).create(values)
        if res.model_id and not res.action:
            model_action = self.env['ir.actions.act_window'].search([('res_model', '=', res.model_id.model)])
            # , ('view_id', '!=', False)])
            if len(model_action):
                has_view = model_action.filtered(lambda x: x.view_id != False)
                if len(has_view):
                    have_tree = has_view.filtered(lambda x: (x.view_mode or "").find("tree") >= 0)
                    model_action = have_tree if len(have_tree) else has_view
                res.write({'action': '%s,%s' % ('ir.actions.act_window', model_action[0].id)})

        return res

    @api.model
    def get_form_view_id(self, view_type=None):
        if view_type == 'edit':
            return self.env.ref('ye_dynamic_odoo.edit_menu_form_view').id
        if view_type == "create":
            return self.env.ref('ye_dynamic_odoo.create_menu_form_view').id

    @api.model
    def prepare_data(self, menu):
        parent_id = menu['parent_id']
        return {
            'name': menu['name'],
            'sequence': menu['sequence'],
            'parent_id': parent_id[0] if parent_id else parent_id,
        }

    @api.model
    def update_menu(self, data):
        data_delete = data.get('_delete', False)
        if data_delete:
            self.browse(data_delete).unlink()
        new_ids = {}
        for menu in data['_new']:
            new_ids[menu['id']] = self.create(self.prepare_data(menu)).id
        while len(data['_newAll']) > 0:
            list_create = []
            list_wait = []
            for menu in data['_newAll']:
                list_create.append(menu) if menu['parent_id'][0] in new_ids else list_wait.append(menu)
            data['_newAll'] = list_wait
            for menu in list_create:
                values = self.prepare_data(menu)
                values['parent_id'] = new_ids[menu['parent_id'][0]]
                new_ids[menu['id']] = self.create(values).id
        for menu in data['_parent']:
            values = self.prepare_data(menu)
            values['parent_id'] = new_ids[menu["parent_id"][0]]
            self.browse(menu["id"]).write(values)
        for menu in data['_old']:
            values = self.prepare_data(menu)
            self.browse(menu["id"]).write(values)
        return True



IrUiMenu()
