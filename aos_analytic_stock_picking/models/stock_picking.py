from odoo import models,fields,api,SUPERUSER_ID


class StockMove(models.Model):
    _inherit="stock.move"
    
    # analytic_account_id = fields.Many2one('account.analytic.account')
    
    def _action_confirm(self, merge=None):
        for rec in self :
                rec.write(
                    {"analytic_account_id" : rec.group_id.mrp_production_ids.analytic_account_id})
        return super(StockMove,self)._action_confirm() 
  
    
    
# class StockPicking(models.Model):
#     _inherit ="stock.picking"
    
#     analytic_account_id = fields.Many2one('account.analytic.account', related="move_lines.analytic_account_id")
    