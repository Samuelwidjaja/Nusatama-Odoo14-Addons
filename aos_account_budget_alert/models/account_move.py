# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
import json
from datetime import datetime
from odoo.tools.misc import formatLang

class AccountMove(models.Model):
    _inherit = "account.move"

    #committed_analytic_line_ids = fields.One2many('account.analytic.line', 'invoice_id', string='Commited Analytic lines')

    def _get_budget_alert_info(self):
        for order in self:
            budget_lines = order.invoice_line_ids.mapped('analytic_account_id').mapped('budget_line')
            budget_ilines = []
            planned_amount = committed_amount = practical_amount = 0.0
            for bline in budget_lines:
                if order.date >= bline.date_from and order.date <= bline.date_to:
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
            #print ('---',planned_amount,committed_amount,practical_amount,budget_ilines)
            if (committed_amount + practical_amount) - planned_amount < 0.0 and order.move_type in ('in_invoice', 'out_refund'):
                budget_alert_info_warn = budget_alert_info_stop = ''
                for line in order.invoice_line_ids:
                    if line.analytic_account_id and budget_ilines[-1][line.analytic_account_id.id]['planned_amount'] == planned_amount and \
                        budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'warn':
                        budget_alert_info_warn += '* %s - %s exceed budget %s\n'%(line.analytic_account_id.name,line.name,str(formatLang(self.env, (committed_amount + practical_amount) - planned_amount, currency_obj=line.currency_id)))
                    elif line.analytic_account_id and budget_ilines[-1][line.analytic_account_id.id]['planned_amount'] == planned_amount and \
                        budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'stop':
                        budget_alert_info_stop += '* %s - %s exceed budget %s\n'%(line.analytic_account_id.name,line.name,str(formatLang(self.env, (committed_amount + practical_amount) - planned_amount, currency_obj=line.currency_id)))
                #self.budget_alert_info = budget_alert_info
                if budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'warn':
                    order.has_budget_alert_warn = True
                    order.budget_alert_info = budget_alert_info_warn
                if budget_ilines[-1][line.analytic_account_id.id]['alert_type'] == 'stop':
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
            if inv.has_budget_alert_stop and inv.move_type in ('in_invoice', 'in_refund'):       
                raise UserError(_('Budget Exceed Alert\n%s'%inv.budget_alert_info))

#     @api.multi
#     def invoice_validate(self):
#         res = super(AccountMove, self).invoice_validate()
#         self.invoice_line_ids.auth_create_analytic_lines()
#         self._check_budget_alert_info()
#         return res

    def _invoice_make_url(self,model='account.move'):
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

    
    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(AccountMove, self).create(vals_list)
        #print ('---s---',not res_ids.line_ids.filtered(lambda ml: ml.analytic_account_id.budget_line),not self._context.get('picking_budget'))
        if not res_ids.line_ids.filtered(lambda ml: ml.analytic_account_id.budget_line) and not self._context.get('picking_budget'):
            #print ('===CREATE====AnalyticLine===',res_ids)
            res_ids.line_ids.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
        return res_ids

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        print ('==auth_create_analytic_lines==',self)
        if ('line_ids' in vals or ('state' in vals and vals['state'] in ('draft','posted')) and not self._context.get('picking_budget')):
            #print ('===WRITE====AnalyticLine===',res,self,self.line_ids)#.filtered(lambda ml: ml.analytic_account_id.budget_line))
            self.line_ids.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
        return res
    
    def action_post(self):
        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        #res = super(AccountMove, self).action_post()
        #COMMITED INPUT
        #self.invoice_line_ids.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
        if (not self.has_budget_alert_warn and not self.has_budget_alert_stop) or self._context.get('action_budget'):
            return super(AccountMove, self.with_context(picking_budget=True)).action_post()
        self._check_budget_alert_info()
        res = super(AccountMove, self.with_context(picking_budget=True)).action_post()
        #print ('===WARN/STOP==',self.has_budget_alert_warn,self.has_budget_alert_stop)
        if self.has_budget_alert_warn:
            self.state = 'over'
            if not self.notify_budget_alert:
                #print "SEND EMAIL TO BUDGET MANAGER"
                self.send_mail_approve_over_budget()
        return res

    # def action_invoice_open(self):
    #     result = super(AccountMove, self).action_invoice_open()
    #     self._check_budget_alert_info()
    #     if self.has_budget_alert_warn:
    #         self.state = 'over'
    #         if not self.notify_budget_alert:
    #             #print "SEND EMAIL TO BUDGET MANAGER"
    #             self.send_mail_approve_over_budget()
    #     return result
    
    def action_over_budget(self):
        for inv in self:
            inv.approval_user_id = self.env.user.id
            inv.approval_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            inv.with_context(action_budget=True).action_post()
        

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # committed_analytic_line_ids = fields.One2many('account.analytic.line', 
    #     'invoice_line_id', string='Commited Analytic lines')
    committed_analytic_line_ids = fields.Many2many('account.analytic.line',
        'account_anayltic_line_move_line_rel',
        'move_line_id', 'analytic_line_id', 
        string='Committed Analytic lines')

    # @api.model
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals_list['analytic_account_id']:
    #             analytic_id = self.env['account.analytic.account'].browse(vals_list['analytic_account_id'])
    #             print ('===analytic_id===',analytic_id)
    #             self.auth_create_analytic_lines()
    #         #     self.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
    #         # if 'code_prefix_start' in vals and not vals.get('code_prefix_end'):
    #         #     vals['code_prefix_end'] = vals['code_prefix_start']
    #     res_ids = super(AccountMoveLine, self).create(vals_list)
    #     return res_ids

    # def write(self, vals):
    #     res = super(AccountMoveLine, self).write(vals)
    #     if 'analytic_account_id' in vals:
    #         self.filtered(lambda ml: ml.analytic_account_id.budget_line).auth_create_analytic_lines()
    #     return res

    def auth_create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account. This
            method first remove any existing analytic item related to the line before creating any new one.
            aos_account_budget_alert
        """
        for obj_line in self:
            if obj_line.committed_analytic_line_ids and obj_line.analytic_account_id:
                obj_line.committed_analytic_line_ids.committed_amount = obj_line.price_subtotal if obj_line.move_id.move_type in ('out_invoice', 'in_refund') else -obj_line.price_subtotal
                obj_line.committed_analytic_line_ids.committed_account_id = obj_line.account_id.id
                obj_line.committed_analytic_line_ids.account_id = obj_line.analytic_account_id.id
                obj_line.committed_analytic_line_ids.product_id = obj_line.product_id.id
                obj_line.committed_analytic_line_ids.unit_amount = obj_line.quantity
            elif not obj_line.committed_analytic_line_ids and obj_line.analytic_account_id:
                vals_line = obj_line._auth_prepare_analytic_line()
                self.env['account.analytic.line'].create(vals_line)
 
    def _auth_prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
        """
        result = []
        for move_line in self:
            amount = 0.0
            committed_amount = move_line.price_subtotal if move_line.move_id.move_type in ('out_invoice', 'in_refund') else -move_line.price_subtotal
            #amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
            #default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
            result.append({
                'name': move_line.name,
                'date': move_line.move_id.date,
                'account_id': move_line.analytic_account_id.id,
                'tag_ids': [(6, 0, move_line.analytic_tag_ids.ids)],
                'unit_amount': 0,#move_line.quantity,
                'product_id': move_line.product_id and move_line.product_id.id or False,
                'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
                'committed_amount': move_line.company_currency_id.with_context(date=move_line.move_id.invoice_date or fields.Date.context_today(move_line)).compute(committed_amount, move_line.analytic_account_id.currency_id) if move_line.analytic_account_id.currency_id else committed_amount,
                'amount': move_line.company_currency_id.with_context(date=move_line.move_id.invoice_date or fields.Date.context_today(move_line)).compute(amount, move_line.analytic_account_id.currency_id) if move_line.analytic_account_id.currency_id else amount,
                'ref': move_line.move_id.ref or False,
                #'invoice_id': move_line.move_id.id,
                'invoice_line_ids': [(6, 0, move_line.ids)],
                'committed_account_id': move_line.account_id.id,
                'move_id': False,
                'user_id': move_line.move_id.user_id.id or move_line._uid,
            })
        return result
        
    def _auth_update_analytic_line(self, obj_line):
        print ("""UPDATE ANALYTIC LINE""")
        amount = (self.credit or 0.0) - (self.debit or 0.0)
        amount_practical = self.company_currency_id.with_context(date=self.date or fields.Date.context_today(self)).compute(amount, self.analytic_account_id.currency_id) if self.analytic_account_id.currency_id else amount
        #print ('==CMAMT==',obj_line.committed_amount,amount_practical,obj_line.committed_amount-amount_practical)
        #print ('==QTY==',obj_line.unit_amount,self.quantity)
        #print ('==AMT==',obj_line.amount,amount_practical,obj_line.amount+amount_practical)
        return {
            'committed_amount': obj_line.committed_amount - amount_practical,
            'unit_amount': obj_line.unit_amount + self.quantity,
            'amount': obj_line.amount + amount_practical,
            'move_id': self.id,
        }
    
    def create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account. This
            method first remove any existing analytic item related to the line before creating any new one.
        """
        #DON'T DELETE ANALYTIC LINE JUST UPDATE AMOUNT AND MOVE LINE ID
        #self.mapped('invoice_id').mapped('analytic_invoice_line_ids')
        #self.mapped('analytic_line_ids').unlink()
        print ('==create_analytic_lines account==',self.mapped('move_id').mapped('line_ids').mapped('committed_analytic_line_ids'))
        if self.mapped('move_id').mapped('line_ids').mapped('committed_analytic_line_ids'):
            for obj_line in self.mapped('move_id').mapped('line_ids').mapped('committed_analytic_line_ids'):
                move_line = self.filtered(lambda x: x.product_id == obj_line.product_id and x.analytic_account_id == obj_line.account_id and x.account_id == obj_line.committed_account_id)
                print ('=move_line==',move_line)
                if ((not move_line.move_id.has_budget_alert_warn and not move_line.move_id.has_budget_alert_stop) or self._context.get('action_budget')) and obj_line.account_id == move_line.analytic_account_id:# and obj_line.unit_amount == move_line.quantity:
                    vals_line = move_line._auth_update_analytic_line(obj_line)
                    obj_line.write(vals_line)
        else:
            #self.mapped('analytic_line_ids').unlink()
            for obj_line in self:
                if obj_line.analytic_account_id:
                    vals_line = obj_line._prepare_analytic_line()
                    self.env['account.analytic.line'].create(vals_line)
        
        
        

            
            