from odoo import api, fields, models, SUPERUSER_ID , _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools.misc import format_date

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

class MrpBomLines(models.Model):
    _inherit = "mrp.bom"
     
    def write(self, params):
        res = super(MrpBomLines, self).write(params)
        if params:
            log = " " 
            body_log = ""
            time = datetime.now() 
            product_qty = "product_qty"
            for rec in params['bom_line_ids'] :
                if rec[2] != False :
                    if rec[0] == 0 :
                        product = self.env['product.product'].browse(rec[2]['product_id'])
                        body_log = "Nama Produk %s Jumlah Quantity %s Berhasil Ditambahakan" % (product.name ,rec[2]['product_qty'] )
                    else :
                        if product_qty in rec[2] :
                            product = self.env['mrp.bom.line'].browse(rec[1])
                            body_log = "Nama Produk %s Jumlah Quantity Menjadi %s Berhasil Diubah" % (product.display_name ,rec[2]['product_qty'] )         
            if body_log != '':
                log += " ,"+"".join(body_log)
                log += " Pada "+"".join(time.strftime("%Y-%m-%d %H:%M:%S%z"))
                self.message_post(body=log)
            return res
class Products(models.Model):
    _inherit ="product.product"
    
    add_component = fields.One2many('add.product', 'product_id', 'Add Component')
    

                    
                
        
        
        
        