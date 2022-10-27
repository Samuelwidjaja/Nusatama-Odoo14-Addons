from odoo import fields, models, api, _
from odoo.exceptions import Warning


class wizard_split_mo(models.TransientModel):
    _name = 'wizard.split.mo'
    _description = "Wizard split Manufacturing Orders"

    split_mo_by = fields.Selection([('no_of_split', 'Number of Split'),
                                    ('no_qty', 'Number of Quantity'),
                                    ('custom', 'Manual Split')], string="Split Mo By", default="no_of_split")
    no_of_qty = fields.Integer(string="No.of Split / Qty")
    mp_id = fields.Many2one('mrp.production', string="Manufacturing Order")
    split_mo_line_ids = fields.One2many("wizard.split.mo.line", 'wizard_split_id', string="Split Quantity Lines")

    def btn_split_mo(self):
        split_qty_lst = []
        mo_qty = self.mp_id.product_qty
        if self.split_mo_by != 'custom' and mo_qty < self.no_of_qty:  # for other type of split
            raise Warning(_("You cannot enter split quantity more than manufacturing order quantity."))
        if self.split_mo_by == 'custom':
            split_qty_lst = self.split_mo_line_ids.mapped('qty')
            if not split_qty_lst:
                raise Warning(_("Please enter Split Quantity Lines."))
            if any(l <= 0 for l in split_qty_lst):
                raise Warning(_("Please enter quantity greater than 0."))
            if sum(split_qty_lst) != mo_qty:
                raise Warning(_("Please enter quantity equal to manufacturing order quantity %s." % (mo_qty)))
        elif self.split_mo_by == 'no_of_split':
            if self.no_of_qty <= 1:
                raise Warning(_("Please enter quantity greater than 1."))
            def no_of_split(x, n): 
                 if (x % n == 0): 
                     for i in range(n): 
                         split_qty_lst.append(x // n)
                 else: 
                     zp = n - (x % n) 
                     pp = x // n 
                     for i in range(n): 
                         for i in range(n): 
                             if(i >= zp):
                                 split_qty_lst.append(pp + 1)
                             else: 
                                 split_qty_lst.append(pp)
            no_of_split(mo_qty, self.no_of_qty)
        elif self.split_mo_by == 'no_qty':
            if self.no_of_qty <= 0:
                raise Warning(_("Please enter quantity greater than 0."))
            n = self.no_of_qty
            while mo_qty > n:
                mo_qty -= n
                split_qty_lst.append(n)
            split_qty_lst.append(mo_qty)

        ProdObj = self.env['mrp.production']
        for each_qty in split_qty_lst:
            self.mp_id.copy({'product_qty': each_qty,
                             'origin': self.mp_id.name})

            prod = self.mp_id
            dataprod = prod.copy_data(default={'move_raw_ids':[],'move_finished_ids':[],'workorder_ids':[],'product_qty':each_qty}) # {}
            print(dataprod)
            newprod = ProdObj.new(dataprod[0])
            newprod._onchange_move_raw()
            print(newprod)
        self.mp_id.action_cancel()


class wizard_split_mo(models.TransientModel):
    _name = 'wizard.split.mo.line'
    _description = "Wizard split Manufacturing Orders"

    qty = fields.Integer("Quantity")
    wizard_split_id = fields.Many2one("wizard.split.mo", string="wizard split mo ref")


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    def split_manufacturing_orders(self):
        if self.state in ['progress', 'done', 'cancel', 'to_close']:
            raise Warning(_('You cannot split manufacturing order which is in already in-progress / to close / done / cancel.'))
        return{
               'name': "Split Manufacturing Order",
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.split.mo',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_mp_id': self.id}
                 }
