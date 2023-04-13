from odoo import models,api,fields,_
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date
from odoo.exceptions import UserError
import datetime
class MRPProduction(models.Model):
    _inherit = "mrp.production"

    partner_id = fields.Many2one('res.partner',string="Customer",help="Related Customer SO",)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('on_hold','On Hold'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True,
        help=" * Draft: The MO is not confirmed yet.\n"
             " * On Hold: The MO is on hold because customer has invoice not paid.\n"
             " * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.\n"
             " * In Progress: The production has started (on the MO or on the WO).\n"
             " * To Close: The production is done, the MO has to be closed.\n"
             " * Done: The MO is closed, the stock moves are posted. \n"
             " * Cancelled: The MO has been cancelled, can't be confirmed anymore.")
    def action_confirm(self):

        if self.confirm == False:
            self.confirm = True
            return 
        #get all invoices posted and state payment is not paid
        invoices = self.env['account.move'].search([
            ('partner_id','=',self.partner_id.id),
            ('state','=','posted'),
            ('payment_state','!=','paid'),
            ('move_type', '=', 'out_invoice'), #'in_invoice'
        ])
        if invoices and not self._context.get('force_approval'):
            context = {
                'default_production_id':self[-1].id if len(self) >= 1 else False ,
                'default_invoices':invoices.ids,
                'default_invoices_text':', '.join(invoices.mapped('name'))
            }
            return self.open_warning_wizard(context)
        else:
            return super(MRPProduction,self).action_confirm()

    def open_warning_wizard(self,context):
        return {
                'name': (_("Invoices Not Paid From Customer %s" % (self.partner_id.name))),
                'view_mode': 'form',
                'res_model': 'warning.invoice',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':context
            }
            

    #  OVERRIDE METHODE RELATE TO STATE
    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity_done', 'move_finished_ids.state',
        'workorder_ids', 'workorder_ids.state', 'product_qty', 'qty_producing')
    def _compute_state(self):
        """ Compute the production state. It use the same process than stock
        picking. It exists 3 extra steps for production:
        - progress: At least one item is produced or consumed.
        - to_close: The quantity produced is greater than the quantity to
        produce and all work orders has been finished.
        """
        # Override Compute State
        # TODO: duplicated code with stock_picking.py
        for production in self:
            if not production.move_raw_ids:
                production.state = 'draft'
            elif all(move.state == 'draft' for move in production.move_raw_ids):
                production.state = 'draft'
            elif all(move.state == 'cancel' for move in production.move_raw_ids):
                production.state = 'cancel'
            elif all(move.state in ('cancel', 'done') for move in production.move_raw_ids):
                production.state = 'done'
            elif production.workorder_ids and all(wo_state in ('done', 'cancel') for wo_state in production.workorder_ids.mapped('state')):
                production.state = 'to_close'
            elif not production.workorder_ids and float_compare(production.qty_producing, production.product_qty, precision_rounding=production.product_uom_id.rounding) >= 0:
                production.state = 'to_close'
            elif any(wo_state in ('progress', 'done') for wo_state in production.workorder_ids.mapped('state')):
                production.state = 'progress'
            elif not float_is_zero(production.qty_producing, precision_rounding=production.product_uom_id.rounding):
                production.state = 'progress'
            elif any(not float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding or move.product_id.uom_id.rounding) for move in production.move_raw_ids):
                production.state = 'progress'
            else:
                production.state = 'confirmed'

            # Compute reservation state
            # State where the reservation does not matter.
            production.reservation_state = False
            # Compute reservation state according to its component's moves.
            if production.state not in ('draft', 'on_hold','done', 'cancel'):
                relevant_move_state = production.move_raw_ids._get_relevant_state_among_moves()
                if relevant_move_state == 'partially_available':
                    if production.bom_id.operation_ids and production.bom_id.ready_to_produce == 'asap':
                        production.reservation_state = production._get_ready_to_produce_state()
                    else:
                        production.reservation_state = 'confirmed'
                elif relevant_move_state not in ('draft','on_hold'):
                    production.reservation_state = relevant_move_state

    @api.depends('move_raw_ids', 'state', 'date_planned_start', 'move_raw_ids.forecast_availability', 'move_raw_ids.forecast_expected_date')
    def _compute_components_availability(self):
        self.components_availability = False
        self.components_availability_state = 'available'
        productions = self.filtered(lambda mo: mo.state not in ['cancel', 'on_hold','draft', 'done'])
        productions.components_availability = _('Available')
        for production in productions:
            forecast_date = max(production.move_raw_ids.filtered('forecast_expected_date').mapped('forecast_expected_date'), default=False)
            if any(float_compare(move.forecast_availability, move.product_qty, move.product_id.uom_id.rounding) == -1 for move in production.move_raw_ids):
                production.components_availability = _('Not Available')
                production.components_availability_state = 'late'
            elif forecast_date:
                production.components_availability = _('Exp %s', format_date(self.env, forecast_date))
                production.components_availability_state = 'late' if forecast_date > production.date_planned_start else 'expected'

    @api.depends('state','move_raw_ids')
    def _compute_show_lot_ids(self):
        for order in self:
            order.show_lot_ids = order.state not in ['draft','on_hold'] and any(m.product_id.tracking == 'serial' for m in order.move_raw_ids)
    
    def write(self, vals):
        if 'workorder_ids' in self:
            production_to_replan = self.filtered(lambda p: p.is_planned)
        res = super(MRPProduction, self).write(vals)

        for production in self:
            if 'date_planned_start' in vals and not self.env.context.get('force_date', False):
                if production.state in ['done', 'cancel']:
                    raise UserError(_('You cannot move a manufacturing order once it is cancelled or done.'))
                if production.is_planned:
                    production.button_unplan()
                    move_vals = self._get_move_finished_values(self.product_id, self.product_uom_qty, self.product_uom_id)
                    production.move_finished_ids.write({'date': move_vals['date']})
            if vals.get('date_planned_start'):
                production.move_raw_ids.write({'date': production.date_planned_start, 'date_deadline': production.date_planned_start})
            if vals.get('date_planned_finished'):
                production.move_finished_ids.write({'date': production.date_planned_finished})
            if any(field in ['move_raw_ids', 'move_finished_ids', 'workorder_ids'] for field in vals) and production.state not in ['draft','on_hold']:
                if production.state == 'done':
                    # for some reason moves added after state = 'done' won't save group_id, reference if added in
                    # "stock_move.default_get()"
                    production.move_raw_ids.filtered(lambda move: move.additional and move.date > production.date_planned_start).write({
                        'group_id': production.procurement_group_id.id,
                        'reference': production.name,
                        'date': production.date_planned_start,
                        'date_deadline': production.date_planned_start
                    })
                    production.move_finished_ids.filtered(lambda move: move.additional and move.date > production.date_planned_finished).write({
                        'reference': production.name,
                        'date': production.date_planned_finished,
                        'date_deadline': production.date_deadline
                    })
                production._autoconfirm_production()
                if production in production_to_replan:
                    production._plan_workorders(replan=True)
            if production.state == 'done' and ('lot_producing_id' in vals or 'qty_producing' in vals):
                finished_move_lines = production.move_finished_ids.filtered(
                    lambda move: move.product_id == self.product_id and move.state == 'done').mapped('move_line_ids')
                if 'lot_producing_id' in vals:
                    finished_move_lines.write({'lot_id': vals.get('lot_producing_id')})
                if 'qty_producing' in vals:
                    finished_move_lines.write({'qty_done': vals.get('qty_producing')})

            if not production.bom_id.operation_ids and vals.get('date_planned_start') and not vals.get('date_planned_finished'):
                new_date_planned_start = fields.Datetime.to_datetime(vals.get('date_planned_start'))
                if not production.date_planned_finished or new_date_planned_start >= production.date_planned_finished:
                    production.date_planned_finished = new_date_planned_start + datetime.timedelta(hours=1)
        return res