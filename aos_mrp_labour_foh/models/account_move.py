from odoo import models,fields,api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    labour_cost_foh_id = fields.Many2one('mrp.labour.foh.line',string="Labour Cost & FOH Line")