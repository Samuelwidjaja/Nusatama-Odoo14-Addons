from odoo import models,fields,api

class MRPProduction(models.Model):
    _inherit = "mrp.production"
    
    use_timesheet = fields.Boolean(string="Manage Timesheet", help="Manage Timesheet For This MO")
    timesheet_ids = fields.One2many('account.analytic.line','mrp_production_id',string="Timesheet")
    
    def _prepare_mo_analytic_account(self):
        for mo in self:
            analytic_account = self.sudo().env['account.analytic.account'].create({
                'name': mo.name,
                'company_id': mo.company_id.id,
                'partner_id': False,
                'active': True,
            })
            mo.write({'analytic_account_id':analytic_account.id})
            
    def action_confirm(self):
        res = super(MRPProduction,self).action_confirm()
        if not self.analytic_account_id:
            self._prepare_mo_analytic_account()
        return res