# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

class BudgetLines(models.Model):
    _inherit = "budget.lines"
    _description = "Budget Line"
    
    alert_type = fields.Selection([('stop', 'Stop'),('warn', 'Warning'),('ignore', 'Ignore')], string="Alert", default='stop')
    committed_amount = fields.Float(compute='_compute_committed_amount', string='Committed Amount', digits=0)

    def _compute_committed_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            if not acc_ids:
                raise UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                query = """
                    SELECT SUM(aal.committed_amount)
                    FROM account_analytic_line aal, 
                    account_move_line aml, 
                    account_anayltic_line_move_line_rel aal_rel,
                    account_move am
                    WHERE am.id = aml.move_id
                        AND aal_rel.analytic_line_id = aal.id
                        AND aal_rel.move_line_id = aml.id
                        AND aal.account_id=%s
                        AND (aal.date >= %s AND aal.date <= %s)
                        AND aal.committed_account_id=ANY(%s)
                        AND am.state != 'cancel'"""
                self.env.cr.execute(query, (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                #print ('==result==',result)
                result = self.env.cr.fetchone()[0] or 0.0
            line.committed_amount = result