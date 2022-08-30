from odoo import models,fields,api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_contact_id = fields.Many2one('res.partner', compute="_compute_partner_contact",string='Partner Contact',store=True)

    @api.depends('partner_id')
    def _compute_partner_contact(self):
        for rec in self:
            if rec.partner_id.parent_id:
                rec.partner_contact_id = rec.partner_id.id
            else:
                rec.partner_contact_id = False
            #     if rec.partner_id.child_ids:
            #         child_contacts = rec.partner_id.child_ids.filtered(lambda x:x.type == 'contact')
            #         # get one if vendor have childs contact
            #         if child_contacts:
            #             rec.partner_contact_id = child_contacts[0].id