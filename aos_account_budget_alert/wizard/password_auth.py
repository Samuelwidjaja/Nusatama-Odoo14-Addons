# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class PasswordAuth(models.TransientModel):
    _name = "password.auth"
    _description = "Password Auth"

    password = fields.Char('Password')
    
    def action_validate(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        active_model = context.get('active_model')
        if active_ids and active_model:
            for object in self.env[active_model].browse(active_ids):
                #group = self.env.ref('aos_budget_invoice_alert.budget_password_approval_config')
                if self.user_has_groups('aos_account_budget_alert.budget_password_approval_config'):
                    if self.password == self.env.user.password_auth:
                        object.action_approval_budget()
                    else:
                        raise UserError(_("Wrong Password"))
        return {'type': 'ir.actions.act_window_close'}
    