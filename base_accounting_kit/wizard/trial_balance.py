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

from odoo import fields, models,_
from odoo.tools.misc import get_lang

from odoo.exceptions import UserError
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
        data['form'].update({
            'filter_selection':self.filter_selection,
            'enable_filter':self.enable_filter,
        })
        data['form']['used_context'].update({
            'strict_range':True,
        })
        
        # get method set_filter_data for comparison in financial.report
        filter_method = self.env['config.filter']

        get_filter_data = filter_method.set_filter_data(data['form'],self.from_id,self.from_year)
        data['form'].get('used_context').update({
                'date_from':get_filter_data['from_month'],
                'date_to':get_filter_data['to_month']
        })
        data['form'].update({
                'date_from':get_filter_data['from_month'],
                'date_to':get_filter_data['to_month']
            })

        model = self.env.context.get('active_model')
        docs = self.env[model if model else self._name].browse(
            self.env.context.get('active_ids', []))
        accounts = docs if model == 'account.account' else self.env[
            'account.account'].search([])
        account_res = self.with_context(
            data['form'].get('used_context'))._get_accounts(accounts,
                                                            self.display_account)
        data['accounts'] = account_res
        return data

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
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
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

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        if self._context.get('is_excel'):
            data = self.run_printout_excel(data)
            return self.env.ref('base_accounting_kit.action_report_trial_balance_excel').report_action(self,data)
        return self.with_context(discard_logo_check=True)._print_report(data)