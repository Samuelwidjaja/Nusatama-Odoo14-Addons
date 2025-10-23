from odoo import models, fields
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'purchase_order_ir_attachments_rel',
        'purchase_order_id',
        'attachment_id',
        string="Quotation Vendor Attachments"
    )

    def button_confirm(self):
        for order in self:
            if not order.attachment_ids:
                raise UserError("Quotation Vendor attachment is required before confirming the Purchase Order.")

            pdf_attachments = order.attachment_ids.filtered(
                lambda a: a.mimetype == 'application/pdf'
            )
            if len(pdf_attachments) > 2:
                raise UserError("You can only attach a maximum of 2 PDF files for Quotation Vendor.")

        return super(PurchaseOrder, self).button_confirm()
