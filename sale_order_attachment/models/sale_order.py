from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field relasi attachment
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'sale_order_ir_attachments_rel',
        'sale_order_id',
        'attachment_id',
        string="Attachments"
    )

    def action_confirm(self):
        for order in self:
            # Cek apakah ada attachment
            if not order.attachment_ids:
                raise UserError("PO Customer Attachment is required before confirm.")

            # Cek maksimal 2 PDF
            pdf_attachments = order.attachment_ids.filtered(
                lambda a: a.mimetype == 'application/pdf'
            )
            if len(pdf_attachments) > 2:
                raise UserError("You can only attach a maximum of 2 PDF files.")

        # Lanjutkan confirm
        return super(SaleOrder, self).action_confirm()
