# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'


    operation_level = fields.Integer(states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    button_start_show = fields.Boolean(compute='_compute_button_show')


    def _action_confirm(self):
        workorders_by_production = defaultdict(lambda: self.env['mrp.workorder'])
        for workorder in self:
            workorders_by_production[workorder.production_id] |= workorder

        for production, workorders in workorders_by_production.items():
            workorders_by_bom = defaultdict(lambda: self.env['mrp.workorder'])
            bom = self.env['mrp.bom']
            moves = production.move_raw_ids | production.move_finished_ids

            for workorder in self:
                if workorder.operation_id.bom_id:
                    bom = workorder.operation_id.bom_id
                if not bom:
                    bom = workorder.production_id.bom_id
                previous_workorder = workorders_by_bom[bom][-1:]
                previous_workorder.next_work_order_id = workorder.id
                workorders_by_bom[bom] |= workorder

                moves.filtered(lambda m: m.operation_id == workorder.operation_id).write({
                    'workorder_id': workorder.id
                })

            exploded_boms, dummy = production.bom_id.explode(production.product_id, 1, picking_type=production.bom_id.picking_type_id)
            exploded_boms = {b[0]: b[1] for b in exploded_boms}
            for move in moves:
                if move.workorder_id:
                    continue
                bom = move.bom_line_id.bom_id
                while bom and bom not in workorders_by_bom:
                    bom_data = exploded_boms.get(bom, {})
                    bom = bom_data.get('parent_line') and bom_data['parent_line'].bom_id or False
                if bom in workorders_by_bom:
                    move.write({
                        'workorder_id': workorders_by_bom[bom][-1:].id
                    })
                else:
                    move.write({
                        'workorder_id': workorders_by_bom[production.bom_id][-1:].id
                    })

            for workorders in workorders_by_bom.values():
                if not workorders:
                    continue
                if workorders[0].state == 'pending':
                     workorders[0].state = 'ready'
                for workorder in workorders:
                    workorder._start_nextworkorder()

    def validate_to_start(self):
                if self.move_raw_ids and self.move_raw_ids.filtered(lambda r:r.state not in {'partially_available','assigned','done'}):
                    raise UserError(_('Components must be reserved !'))
                else:
                    operation_not_done = []
                    for workorder in self.production_id.workorder_ids:
                        if workorder.operation_level < self.operation_level and workorder.state != 'done':
                            operation_not_done.append(workorder)

                    if operation_not_done:
                        raise UserError(_('Operation not completed yet!'))

    def button_start(self):
        self.validate_to_start()
        return super().button_start()

    def _start_nextworkorder(self):
        if self.state == 'done':
            current_order = self.production_id.workorder_ids.filtered(lambda r: r.operation_level == self.operation_level)
            if all(current_order.mapped(lambda r: r.state == 'done')):
                next_order = self.production_id.workorder_ids.filtered(lambda r: r.operation_level == self.operation_level+1)
                for no in next_order:
                    if no.state == 'pending':
                        no.state = 'ready'
            # else:
            #     next_order = self.next_work_order_id
            #     if next_order.state == 'pending':
            #         next_order.state = 'ready'

    
    @api.depends('production_id.workorder_ids','production_id.move_raw_ids')
    def _compute_button_show(self):
        show = True
        value = 0
        for move in self.mapped('production_id').move_raw_ids:
            if move.state not in {'partially_available','assigned','done'} :
                self.button_start_show = False
            else :
                value +=1
        if value >= 1 :
            for rec in self:
                operation_not_done = []
                for workorder in self.production_id.workorder_ids:
                    if workorder.operation_level < rec.operation_level and workorder.state != 'done':
                                operation_not_done.append(workorder)
                if operation_not_done:
                    show = False
                rec.button_start_show = show
                
    #@api.depends('production_id.workorder_ids','production_id.move_raw_ids')
    #def _compute_button_show(self):
    #    show = True
    #    if not all(move.state in {'partially_available','assigned','done'} for move in self.mapped('production_id').move_raw_ids):
    #        self.button_start_show = False
    #    else:
    #        for rec in self:
    #            operation_not_done = []
    #            for workorder in self.production_id.workorder_ids:
    #                if workorder.operation_level < rec.operation_level and workorder.state != 'done':
    #                    operation_not_done.append(workorder)

    #            if operation_not_done:
    #                show = False

    #            rec.button_start_show = show
