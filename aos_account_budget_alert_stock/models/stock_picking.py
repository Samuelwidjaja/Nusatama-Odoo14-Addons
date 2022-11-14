# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
import json
from datetime import datetime
from odoo.tools.misc import formatLang

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_budget_alert_info(self):
        for order in self:
            budget_lines = order.move_lines.mapped('analytic_account_id').mapped('budget_line')
            budget_ilines = []
            planned_amount = committed_amount = practical_amount = 0.0
            for bline in budget_lines:
                if order.scheduled_date.date() >= bline.date_from and order.scheduled_date.date() <= bline.date_to:
                    budget_iline = {}
                    budget_iline[bline.analytic_account_id.id] = {
                        'budget_line_id': bline,
                        'planned_amount': bline.planned_amount,
                        'committed_amount': bline.committed_amount,
                        'practical_amount': bline.practical_amount,
                        'alert_type': bline.alert_type,
                    }
                    #print ('===budget_iline==',budget_iline)
                    budget_ilines.append(budget_iline)
                    planned_amount = bline.planned_amount 
                    committed_amount = bline.committed_amount
                    practical_amount = bline.practical_amount
            order.budget_alert_info = ''
            order.has_budget_alert_warn = False
            order.has_budget_alert_stop = False
            committed_amount = sum(move._get_price_unit()*move.product_uom_qty*(-1 if move.location_id.usage == 'internal' else 1) for move in order.move_lines.filtered(lambda ml: ml.analytic_account_id.budget_line))
            #print ('---',planned_amount,committed_amount,practical_amount,budget_ilines)
            if (committed_amount + practical_amount) - planned_amount < 0.0:# and order.move_type in ('in_invoice', 'out_refund'):
                budget_alert_info_warn = budget_alert_info_stop = ''
                for line in order.move_lines:
                    if line.analytic_account_id and budget_ilines[-1][line.analytic_account_id.id]['planned_amount'] == planned_amount and \
                        budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'warn':
                        budget_alert_info_warn += '* %s - %s exceed budget %s\n'%(line.analytic_account_id.name,line.name,str(formatLang(self.env, (committed_amount + practical_amount) - planned_amount, currency_obj=self.company_id.currency_id)))
                    elif line.analytic_account_id and budget_ilines[-1][line.analytic_account_id.id]['planned_amount'] == planned_amount and \
                        budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'stop':
                        budget_alert_info_stop += '* %s - %s exceed budget %s\n'%(line.analytic_account_id.name,line.name,str(formatLang(self.env, (committed_amount + practical_amount) - planned_amount, currency_obj=self.company_id.currency_id)))
                    #self.budget_alert_info = budget_alert_info
                    if line.analytic_account_id and budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'warn':
                        order.has_budget_alert_warn = True
                        order.budget_alert_info = budget_alert_info_warn
                    if line.analytic_account_id and budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'stop':
                        order.has_budget_alert_stop = True
                        order.budget_alert_info = budget_alert_info_stop
            #print ('===_get_budget_alert_info===',order.has_budget_alert_warn,order.has_budget_alert_stop,order.budget_alert_info)
 
    has_budget_alert_warn = fields.Boolean(compute='_get_budget_alert_info', store=False)
    has_budget_alert_stop = fields.Boolean(compute='_get_budget_alert_info', store=False)
    budget_alert_info = fields.Text(compute='_get_budget_alert_info', store=False)
    notify_budget_alert = fields.Boolean('Notify Budget Alert')
    approval_user_id = fields.Many2one('res.users','Budget Approval')
    approval_datetime = fields.Datetime('Budget Approval Date')
    state = fields.Selection(selection_add=[
            #('draft','Draft'),
            #('proforma', 'Pro-forma'),
            #('proforma2', 'Pro-forma'),
            ('over','Over Budget'),
            #('open', 'Open'),
            #('paid', 'Paid'),
            #('cancel', 'Cancelled'),
        ], ondelete={'over': 'cascade'})
    
    def _check_budget_alert_info(self):
        for inv in self:
            #print ('_check_budget_alert_info',inv,inv.has_budget_alert_stop,self.move_type)
            if inv.has_budget_alert_stop:# and inv.move_type in ('in_invoice', 'in_refund'):       
                raise UserError(_('Budget Exceed Alert\n%s'%inv.budget_alert_info))

    def _invoice_make_url(self,model='stock.picking'):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069')
        if base_url:
            base_url += '/web/login?db=%s&login=%s&key=%s#id=%s&model=%s' % (self._cr.dbname, '', '', self.id, model)
        return base_url

    def send_mail_approve_over_budget(self): 
        #manager_group_id = self.env['ir.model.data'].get_object_reference('sales_team', 'group_sale_manager')[1]
        manager_group_id = self.env['ir.model.data'].get_object_reference('aos_account_budget_alert', 'budget_alert_approval_config')[1]
        browse_group = self.env['res.groups'].browse(manager_group_id) 
        
        url = self._invoice_make_url('account.move')
        subject  =  self.display_name + '-' + 'Require to Over Budget Approval'
        for user in browse_group.users:
            partner = user.partner_id
            body = '''
                        <b>Dear ''' " %s</b>," % (partner.name) + '''
                        <p> An Invoice ''' "<b><i>%s</i></b>" % self.name + '''  for supplier ''' "<b><i>%s</i></b>" % self.partner_id.name +''' require your Budget Approval.</p> 
                        <p>You can access invoice from  below url <br/>
                        ''' "%s" % url +''' </p> 
                        
                        <p><b>Regards,</b> <br/>
                        ''' "<b><i>%s</i></b>" % self.user_id.name +''' </p> 
                        ''' 
            
            mail_values = {
                        'email_from': self.user_id.email,
                        'email_to': partner.email,
                        'subject': subject,
                        'body_html': body,
                        'state': 'outgoing',
                        'message_type': 'email',
                    }
            mail_id =self.env['mail.mail'].create(mail_values)
            mail_id.send(True)

    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     res_ids = super(StockPicking, self).create(vals_list)
    #     res_ids.move_lines.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
    #     return res_ids

    # def write(self, vals):
    #     res = super(StockPicking, self).write(vals)
    #     if 'move_lines' in vals or ('state' in vals and vals['state'] in ('draft','posted')):
    #         self.move_lines.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
    #     return res
    
    def _action_done(self):
        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        #res = super(StockPicking, self).action_post()
        #COMMITED INPUT
        #self.move_lines.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
        if (not self.has_budget_alert_warn and not self.has_budget_alert_stop) or self._context.get('action_budget'):
            return super(StockPicking, self.with_context(picking_id=self,move_lines=self.move_lines,picking_budget=True))._action_done()
        self._check_budget_alert_info()
        res = super(StockPicking, self.with_context(picking_id=self,move_lines=self.move_lines,picking_budget=True))._action_done()
        #print ('===WARN/STOP==',self.has_budget_alert_warn,self.has_budget_alert_stop)
        if self.has_budget_alert_warn:
            self.state = 'over'
            if not self.notify_budget_alert:
                #print "SEND EMAIL TO BUDGET MANAGER"
                self.send_mail_approve_over_budget()
        return res

    def action_over_budget(self):
        for inv in self:
            inv.approval_user_id = self.env.user.id
            inv.approval_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            inv.with_context(action_budget=True).action_post()
        

class StockMove(models.Model):
    _inherit = 'stock.move'

    committed_analytic_line_ids = fields.Many2many('account.analytic.line', 
        'account_anayltic_line_stock_move_rel',
        'analytic_line_id', 'stock_move_id', 
        string='Committed Analytic lines')
