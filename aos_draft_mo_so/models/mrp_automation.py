from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

class MrpAutomation(models.Model):
    _inherit = "mrp.production"
        
    confirm =fields.Boolean()
    def action_confirm(self):
        for production in self :
            if production['origin'] != False:
                if production['state'] == 'draft' and production['confirm'] == False :
                    production['state'] = 'draft'
                    production['confirm'] = True
            return super(MrpAutomation, self).action_confirm()
            #     else :
            #         if self.product_qty > 1:
            #             raise UserError("Quantity is greater than 1 you must split to several MO")
            #         return super(MrpAutomation,self).action_confirm()
            # else :
            #         if self.product_qty > 1:
            #             raise UserError("Quantity is greater than 1 you must split to several MO")
            #         return super(MrpAutomation,self).action_confirm()

                    


                    
                
    

        
        
                

        
    
            
    
    