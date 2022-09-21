from odoo import api, fields, models, SUPERUSER_ID , _
from odoo.exceptions import UserError, ValidationError


class MrpBom(models.Model):
    _inherit = "mrp.production"
    
       
    def add_material(self):
            view = self.env.ref('aos_mrp_bom.add_component_wizard_form')
            return {
                'name': _("Add Component"),
                'view_mode': 'form',
                'view_id': view.id,
                'res_model': 'add.component',
                'type': 'ir.actions.act_window',
                'target': 'new',
                    }

     
class Products(models.Model):
    _inherit ="product.product"
    
    add_component = fields.One2many('add.product', 'product_id', 'Add Component')
    
        
            
                
        
        
        
        