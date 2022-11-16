from odoo import api, fields, models, tools


class MrpAutomation(models.Model):
    _inherit = "mrp.production"
        
    confirm =fields.Boolean()
    def action_confirm(self):
        for production in self :
            if production['origin'] != False:
                if production['state'] == 'draft' and production['confirm'] == False :
                    production['state'] = 'draft'
                    production['confirm'] = True
                else :
                  return super(MrpAutomation,self).action_confirm()
            else :
                    return super(MrpAutomation,self).action_confirm()

                    


                    
                
    

        
        
                

        
    
            
    
    