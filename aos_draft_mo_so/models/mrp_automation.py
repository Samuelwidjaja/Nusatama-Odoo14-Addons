from odoo import api, fields, models


class MrpAutomation(models.Model):
    _inherit = "mrp.production"
    
    def action_confirm(self):
        test = 1 
        super(MrpAutomation,self).action_confirm()
        for production in self :
            if production['state'] == 'confirmed' and test == 1 :
                production['state'] = 'draft'
                test +=1
            else :
               production['state'] = 'confirmed' 
            
        
        
                

        
    
            
    
    