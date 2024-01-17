from odoo import models, fields

class MRPProduction(models.Model):
    _inherit = "mrp.production"
    
    
    labour_cost_line_ids = fields.One2many('mrp.labour.foh.line', 'mrp_production_id', string="Labour Cost Line", readonly=True, domain="[('mrp_labour_foh_id.state', 'in', ['done'])]")