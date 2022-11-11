# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def _create_workorder(self):
        for production in self:
            if not production.bom_id:
                continue
            workorders_values = []

            product_qty = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id)
            exploded_boms, dummy = production.bom_id.explode(production.product_id, product_qty / production.bom_id.product_qty, picking_type=production.bom_id.picking_type_id)

            for bom, bom_data in exploded_boms:
                # If the operations of the parent BoM and phantom BoM are the same, don't recreate work orders.
                if not (bom.operation_ids and (not bom_data['parent_line'] or bom_data['parent_line'].bom_id.operation_ids != bom.operation_ids)):
                    continue
                for operation in bom.operation_ids:
                    workorders_values += [{
                        'name': operation.name,
                        'operation_level': operation.operation_level,
                        'production_id': production.id,
                        'workcenter_id': operation.workcenter_id.id,
                        'product_uom_id': production.product_uom_id.id,
                        'operation_id': operation.id,
                        'state': 'pending',
                        'consumption': production.consumption,
                    }]
            production.workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder._get_duration_expected()
                
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for rec in self.move_raw_ids :
            if rec.reserved_availability < rec.product_uom_qty or rec.product_uom_qty > rec.reserved_availability :
                raise UserError(_("To Consume Harus Sama Dengan Reserved Qty Pada Product %s") % rec.product_id.name)
        return res
    
    #def write(self, vals):
    #    res = super(MrpProduction, self).write(vals)
    #    for rec in vals['move_raw_ids']:
    #        num = 0
    #        if rec[0] == 1 :
    #            num += rec[1]
    #            stockmove = self.env['stock.move'].browse(num)
    #            if stockmove.workorder_id.state == 'done' and 'product_uom_qty' in rec[2]:
    #                raise UserError(_("%s Already Finished Can't Change The Qty") % stockmove.workorder_id.name)
    #    return res 