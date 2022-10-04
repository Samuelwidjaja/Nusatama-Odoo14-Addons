from odoo import models,fields,api,SUPERUSER_ID

class StockMove(models.Model):
    _inherit="stock.move"
    
    #analytic_account_id = fields.Many2one('account.analytic.account')
    
    def _action_confirm(self, merge=True, merge_into=False ):
        for rec in self :
            rec.write(
                {"analytic_account_id" : rec.group_id.mrp_production_ids.analytic_account_id})
        return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)
    
    