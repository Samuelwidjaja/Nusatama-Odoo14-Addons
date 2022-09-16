from odoo import api, fields, models


class MrpAutomation(models.Model):
    _inherit = "mrp.production"
        
    confirm =fields.Boolean()
    
    def action_confirm(self):
        super(MrpAutomation,self).action_confirm()
        for production in self :
            if production['origin'] != False:
                if production['state'] == 'confirmed' and production['confirm'] == False :
                    production['state'] = 'draft'
                    production['confirm'] = True
                else :
                    production['state'] = 'confirmed'

class StockMoves(models.Model):
    _inherit = "stock.move"
    
    confirm =fields.Boolean()
    
    def _action_confirm(self):
        super(StockMoves,self)._action_confirm()
        for production in self :
                if production['state'] == 'assigned' and production['confirm'] == False :
                    production['state'] = 'confirmed'
                    production['confirm'] == True
                else :
                    production['state'] = 'assigned'

        
        
                

        
    
            
    
    