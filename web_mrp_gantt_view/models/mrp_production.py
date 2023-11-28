from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = "mrp.production"
    
    task_type = fields.Selection([
        ('task', 'Task'),
        ('milestone', 'Milestone')
        ], string="Task Type", required=True, default='task')
    color = fields.Integer('Project color', default=4)
    production_link_ids = fields.One2many('mrp.production.link', 'mrp_production_id', string="Link Orders")
    task_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),
        ('high', 'High')
    ], string='Priority', required=True, default='normal')
    progress = fields.Integer(tracking=True)
    
    @api.model
    def search_read_links(self, domain=None):
        datas = []
        productions = self.env['mrp.production'].search(domain)
        for production in productions:
            if production.production_link_ids:                
                for link in production.production_link_ids:                    
                    link_vals = {
                        'id' : link.id,
                        'source' : production.id,
                        'target': link.target_production_id.id, 
                        'type': link.link_type,
                    }
                    datas.append(link_vals)
        return datas

class TaskLink(models.Model):
    _name = "mrp.production.link"
    _description = "MRP Production Links"

    mrp_production_id = fields.Many2one('mrp.production', string='Production')
    target_production_id = fields.Many2one('mrp.production', string='Target Production', required=True)
    link_type = fields.Selection([
        ('0', "Finish to Start"), 
        ('1', "Start to Start"), 
        ('2', "Finish to Finish"),
        ('3', "Start to Finish")
        ], string="Link Type", required=True, default='1')
    