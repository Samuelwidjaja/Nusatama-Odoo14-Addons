# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import fields, models,_,api
from odoo.tools.misc import get_lang
from datetime import timedelta
from odoo.exceptions import UserError,ValidationError,Warning
import json
class AccountBalanceReport(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = 'account.balance.report'
    _description = 'Trial Balance Report'

    journal_ids = fields.Many2many('account.journal',
                                'account_balance_report_journal_rel',
                                'account_id', 'journal_id',
                                string='Journals', required=True,
                                default=[])
    # Filter for comparison
    filter_selection = fields.Selection([
        ('quarter','Quarter'),
        ('monthly','Monthly'),
        ('yearly','Yearly'),
    ],string="Filter By", default='monthly',required=True)
    from_id = fields.Many2one('config.filter',string="From",required=True)
    to_id = fields.Many2one('config.filter',string='Compare To')
    from_year = fields.Many2one('config.filter',string="From Year",domain=[('type','=','yearly')])
    to_year = fields.Many2one('config.filter',string="Compare To Year",domain=[('type','=','yearly')])
    enable_filter = fields.Boolean(
        string='Enable Comparison',
        default=False)
    multi_period = fields.Boolean(
        string='Multi Period',
        default=False)

    # using field text for get all data and avoid long query url
    datas = fields.Text(string="datas")
    # using this field for mapping account name 
    account_name_json = fields.Text()
    _mapping_name = []
    # map_res = fields.Text()

    @api.onchange('filter_selection')
    def onchange_filter_selection(self):
        self.from_id = False
        self.to_id = False
        self.from_year = False
        self.to_year = False

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref(
                'base_accounting_kit.action_report_trial_balance').report_action(
                records, data=data)

    def run_printout_excel(self,data):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        model = data.get('model')
        docs = self.env[model].browse(
            self.env.context.get('ids', []))
        accounts = docs if model == 'account.account' else self.env[
            'account.account'].search([])
        # Get all account comparison
        if self.enable_filter:
            get_date_comparison = self.with_context(comparison=True)._get_dates_from_filter(data)
            comparison_result = self.get_filter_result(data,get_date_comparison,accounts)
            data['filters'] = comparison_result
        
        # get initial_balance
        get_dates_initial_balance = self.with_context(initial_balance=True)._get_dates_from_filter(data)
        dates = get_dates_initial_balance[0][1]
        get_dates_initial_balance[0][1].update({
                'from_month':False,
                    'to_month':dates['from_month'] - timedelta(days=1)
                })
        
        initial_balance_result = self.get_filter_result(data,get_dates_initial_balance,accounts)

        #get current item
        get_current_date = self.with_context(comparison=False)._get_dates_from_filter(data)
        account_res = self.with_context(comparison=False).get_filter_result(data,get_current_date,accounts)
        # data['accounts'] = [{f"{self.from_id.name} {'- '+ self.from_year.name}":account_res}]
        data['accounts'] = account_res
        data['initial_balance'] = initial_balance_result
        
        del data['get_dates']
        data['form'].update({'date_from':str(data['form']['date_from']), 'date_to':str(data['form']['date_to'])})
        data['form']['used_context'].update({'date_from':str(data['form']['date_from']), 'date_to':str(data['form']['date_to'])})
        data.update({'form':[data['form']]})
        self.datas = json.dumps(data)
        self.account_name_json = json.dumps(getattr(self,'_mapping_name'))
        getattr(self,'_mapping_name').clear()

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env[
            'account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            # res['code'] = account.code
            res['name'] = (account.code +' '+account.name)
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
                #mapping account name
                if res['name'] not in getattr(self,'_mapping_name'):
                    getattr(self,'_mapping_name').append((account.code+" "+account.name))
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(res['debit']) or not currency.is_zero(
                    res['credit'])):
                account_res.append(res)
        return account_res

    def get_filter_result(self,data,filter_result,accounts):
        result = []
        data_copy = data['form'].copy()
        filter_result.sort(key=lambda x:x[1].get('from_month') if x[1].get('from_month') != False else fields.Date.today())
        for line in filter_result:
            data_copy = self._update_date(data_copy,line[1])
            res = self.with_context(
                data_copy.get('used_context'))._get_accounts(accounts,self.display_account)
            result.append((line[0],res))
        return result
    
    def _get_dates_from_filter(self,data):
        filter_method = self.env['config.filter']
        data_copy = data['form'].copy()
        result = []
        if data_copy.get('enable_filter') and self._context.get('comparison'):
            # get amount from filter
            if data_copy.get('multi_period'):
                result = filter_method.range_comparison(data_copy,self.from_year,self.to_year,self.from_id,self.to_id)
            else:
                result.append((f"{self.to_id.name} {self.to_year.name if self.to_year else ''}",filter_method.set_filter_data(data_copy,self.to_id,self.to_year)))

        elif data_copy.get('enable_filter') and self._context.get('initial_balance'):
            result.append((f"{self.to_id.name} {self.to_year.name if self.to_year else ''}",filter_method.set_filter_data(data_copy,self.to_id,self.to_year)))
        else:
            result.append((f"{self.from_id.name} {self.from_year.name}",filter_method.set_filter_data(data_copy,self.from_id,self.from_year)))
        return result

    def _update_date(self,data,filter_date):
        data.get('used_context').update({
                'date_from':filter_date.get('from_month',False),
                'date_to':filter_date.get('to_month',False)
        })
        # data.update({
        #         'date_from':filter_date.get('from_month',False),
        #         'date_to':filter_date.get('to_month',False)
        #     })
        return data

    def check_report(self):
        self.ensure_one()
        #cek jika tipe filter tidak sama dengan type filter yang dipilih
        if self.from_id.type != self.filter_selection or (self.to_id and self.to_id.type != self.filter_selection):
            self._test()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id','filter_selection','enable_filter','multi_period'])[0]
        # get dates for date_from and date_to
        data['get_dates'] = list(self.with_context(comparison=False)._get_dates_from_filter(data))
        data['form'].update({'date_from':data['get_dates'][0][1].get('from_month'), 'date_to':data['get_dates'][0][1].get('to_month')})
        #end get dates
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        if self._context.get('is_excel'):
            self.run_printout_excel(data)
            return self.env.ref('base_accounting_kit.action_report_trial_balance_excel').report_action(self)
        return self.with_context(discard_logo_check=True)._print_report(data)

    @api.onchange('filter_selection')
    def _onchange_filter_selection(self):
        self.from_id = False
        self.to_id = False

    @api.onchange('enable_filter')
    def _onchange_filter_selection(self):
        if not self.enable_filter:
            self.to_id = False
            self.multi_period = False
            self.to_year = False