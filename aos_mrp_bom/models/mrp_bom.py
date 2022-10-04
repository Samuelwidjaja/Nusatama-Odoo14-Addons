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
            time = datetime.now() 
            for rec in params['bom_line_ids'] :
                if rec[2] != False :
                    product = self.env['product.product'].browse(rec[2]['product_id'])
                    body_log = "Nama Produk %s Jumlah Quantity Menjadi %s Berhasil Ditambahakan" % (product.name ,rec[2]['product_qty'] )
                    log += " , "+"".join(body_log)
                log += " Pada "+"".join(time.strftime("%Y-%m-%d %H:%M:%S%z"))
            self.message_post(body=log)
            return res
     
class Products(models.Model):
    _inherit ="product.product"
    
    add_component = fields.One2many('add.product', 'product_id', 'Add Component')
    
class StockMove(models.Model):
    _inherit ="stock.move"
    
    validate = fields.Boolean()
    def _action_confirm(self, merge=True, merge_into=False ):
        total_stock = 0
        for rec in self :    
            if rec.validate == True :
                rec.raw_material_production_id.components_availability = _('Available')
                rec.raw_material_production_id.components_availability_state = 'available'
                stock_quant_obj = self.env['stock.quant'].search([('product_id' , '=' , rec.product_id.id)])
                for stock in stock_quant_obj :
                    total_stock += stock.available_quantity
                if total_stock >= 0 :
                    if rec.procure_method != 'make_to_stock'and rec.bom_line_id.id == False:
                        rec['procure_method'] = 'make_to_stock'
                        rec['validate'] == False
                    if rec.procure_method == 'make_to_stock' and rec.production_id.bom_id.id == False:
                        rec['procure_method'] = 'make_to_order'
                elif rec.forecast_expected_date and total_stock > 0 :
                    rec.raw_material_production_id.components_availability = _('Exp %s', format_date(self.env, rec.forecast_date))
                    rec.raw_material_production_id.components_availability_state = 'late' if rec.forecast_date > rec.raw_material_production_id.date_planned_start else 'expected'
                else :
                    rec.raw_material_production_id.components_availability = _('Not Available')
                    rec.raw_material_production_id.components_availability_state = 'late'
        return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)

                    
                
        
        
        
        