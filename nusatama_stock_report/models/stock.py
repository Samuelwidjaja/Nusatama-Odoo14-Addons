from odoo import fields,models,api,_

class StockPicking(models.Model):
    _inherit = "stock.picking"

    chassis_number = fields.Char(string="Chassis Number")
    engine_number = fields.Char(string="Engine Number")
    incoterm_id = fields.Many2one('account.incoterms',string="Incoterm",compute="_compute_incoterm")
    partner_contact_id = fields.Many2one('res.partner', compute="_compute_partner_contact",string='Partner Contact',store=True)

    @api.depends('partner_id')
    def _compute_partner_contact(self):
        for rec in self:
            if rec.partner_id.parent_id:
                rec.partner_contact_id = rec.partner_id.id
            else:
                rec.partner_contact_id = False
                
    @api.depends('sale_id.incoterm','purchase_id.incoterm_id')
    def _compute_incoterm(self):
        for rec in self:
            incoterm = rec.sale_id.incoterm or rec.purchase_id.incoterm_id
            if incoterm:
                rec.incoterm_id = incoterm.id
            else:
                rec.incoterm_id = False

    def print_do(self):
        return self.env.ref('nusatama_stock_report.report_stock_delivery_order').report_action(self)
    
    def print_bast(self):
        return self.env.ref('nusatama_stock_report.report_stock_picking_bast').report_action(self)