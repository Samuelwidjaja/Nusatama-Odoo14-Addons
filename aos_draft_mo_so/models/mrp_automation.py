from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

class MrpAutomation(models.Model):
    _inherit = "mrp.production"
        
    confirm =fields.Boolean()

    def action_confirm(self):
        res = super(MrpAutomation, self).action_confirm()
        for production in self :
            if production['origin'] != False:
                if production['state'] != 'draft' and production['confirm'] == False :
                    production['state'] = 'draft'
                    production['confirm'] = True
            return res


    # def action_confirm(self):
        
    #     for production in self :
    #         if production['origin'] != False:
    #             if production['confirm'] == False:
    #                 production['confirm'] = True
    #                 return 
    #             else :
    #                 invoices = self.env['account.move'].search([
    #                     ('partner_id','=',self.partner_id.id),
    #                     ('state','=','posted'),
    #                     ('payment_state','!=','paid'),
    #                     ('move_type', '=', 'out_invoice'), #'in_invoice'
    #                 ])
    #                 if invoices and not self._context.get('force_approval'):
    #                     context = {
    #                         'default_production_id':self[-1].id if len(self) >= 1 else False ,
    #                         'default_invoices':invoices.ids,
    #                         'default_invoices_text':', '.join(invoices.mapped('name'))
    #                     }
    #                     return self.open_warning_wizard(context)
    #         else :
    #             return super(MrpAutomation, self).action_confirm()
            

    # def open_warning_wizard(self,context):
    #     return {
    #             'name': (_("Invoices Not Paid From Customer %s" % (self.partner_id.name))),
    #             'view_mode': 'form',
    #             'res_model': 'warning.invoice',
    #             'type': 'ir.actions.act_window',
    #             'target': 'new',
    #             'context':context
    #             }
            #     else :
            #         if self.product_qty > 1:
            #             raise UserError("Quantity is greater than 1 you must split to several MO")
            #         return super(MrpAutomation,self).action_confirm()
            # else :
            #         if self.product_qty > 1:
            #             raise UserError("Quantity is greater than 1 you must split to several MO")
            #         return super(MrpAutomation,self).action_confirm()

                    


                    
                
    

        
        
                

        
    
            
    
    