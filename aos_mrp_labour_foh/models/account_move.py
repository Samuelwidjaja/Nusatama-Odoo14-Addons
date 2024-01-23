from odoo import models,fields,api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    labour_cost_id = fields.Many2one('mrp.labour.foh', string="Labour Cost FOH", ondelete="cascade")
            
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    labour_cost_foh_id = fields.Many2one('mrp.labour.foh.line',string="Labour Cost & FOH Line",ondelete="cascade")