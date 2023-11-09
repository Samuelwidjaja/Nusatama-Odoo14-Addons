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
import re
from calendar import monthrange
from datetime import datetime,date
from odoo import api, models, fields
from odoo.exceptions import UserError
import base64
import json
import logging
logger = logging.getLogger(__name__)

class FinancialReport(models.TransientModel):
    _name = "financial.report"
    _inherit = "account.common.report"
    _description = "Financial Reports"

    view_format = fields.Selection([
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal')],
        default='vertical',
        string="Format")
    
    @api.model
    def _get_account_report(self):
        reports = []
        if self._context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(
                self._context.get('active_id')).name
            reports = self.env['account.financial.report'].search([
                ('name', 'ilike', menu)])
        return reports and reports[0] or False

    enable_filter = fields.Boolean(
        string='Enable Comparison',
        default=False)
    account_report_id = fields.Many2one(
        'account.financial.report',
        string='Account Reports',
        required=True)

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    debit_credit = fields.Boolean(
        string='Display Debit/Credit Columns',
        default=True,
        help="This option allows you to"
             " get more details about the "
             "way your balances are computed."
             " Because it is space consuming,"
             " we do not allow to use it "
             "while doing a comparison.")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        index=True,
        default=lambda self: self.env.company.id)

    # Filter For Comparison
    filter_selection = fields.Selection([
        ('quarter','Quarter'),
        ('monthly','Monthly'),
        ('yearly','Yearly'),
    ],string="Filter By", default='monthly')
    
    from_id = fields.Many2one('config.filter',string="From")
    to_id = fields.Many2one('config.filter',string="Compare To")
    year_from = fields.Many2one('config.filter',domain=[('type','=','yearly')],string="From Year")
    year_to = fields.Many2one('config.filter',domain=[('type','=','yearly')],string="Compare To Year")
    multi_period = fields.Boolean(string="Multi Period")
    
    # set datas to field and avoid long query url
    datas = fields.Text(string="Datas")
    account_name_json = fields.Text()
    _mapping_account_name = []
    # def view_report_pdf(self):
    #     """This function will be executed when we click the view button
    #     from the wizard. Based on the values provided in the wizard, this
    #     function will print pdf report"""
        # self.ensure_one()
        # data = dict()
        # data['ids'] = self.env.context.get('active_ids', [])
        # data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        # data['form'] = self.read(
        #     ['date_from', 'enable_filter', 'debit_credit', 'date_to',
        #      'account_report_id', 'target_move', 'view_format',
        #      'company_id'])[0]
        # used_context = self._build_contexts(data)
        # data['form']['used_context'] = dict(
        #     used_context,
        #     lang=self.env.context.get('lang') or 'en_US')

        # report_lines = self.get_account_lines(data['form'])
        # # find the journal items of these accounts
        # journal_items = self.find_journal_items(report_lines, data['form'])

        # def set_report_level(rec):
        #     """This function is used to set the level of each item.
        #     This level will be used to set the alignment in the dynamic reports."""
        #     level = 1
        #     if not rec['parent']:
        #         return level
        #     else:
        #         for line in report_lines:
        #             key = 'a_id' if line['type'] == 'account' else 'id'
        #             if line[key] == rec['parent']:
        #                 return level + set_report_level(line)

        # # finding the root
        # for item in report_lines:
        #     item['balance'] = round(item['balance'], 2)
        #     if not item['parent']:
        #         item['level'] = 1
        #         parent = item
        #         report_name = item['name']
        #         id = item['id']
        #         report_id = item['r_id']
        #     else:
        #         item['level'] = set_report_level(item)
        # currency = self._get_currency()
        # data['currency'] = currency
        # data['journal_items'] = journal_items
        # data['report_lines'] = report_lines
        # checking view type
        # return self.env.ref(
        #         'base_accounting_kit.financial_report_pdf').report_action(self,data)
    
    @api.onchange('filter_selection')
    def onchange_filter_selection(self):
        self.from_id = False
        self.to_id = False
        self.year_from = False
        self.year_to = False
        
    def clean_filter(self):
        if not self.enable_filter:
            self.multi_period = False
            self.to_id = False
            self.year_to = False
        else:
            self.debit_credit = False
        if self.filter_selection == 'yearly':
            self.year_from = False

    def view_report(self):
        """This function will be executed when we click the view button
        from the wizard. Based on the values provided in the wizard, this
        function will print Excel report"""
        self.ensure_one()
        self.clean_filter()
        data = dict()
        result = []
        # get method from model config.filter
        filter_method = self.env['config.filter']

        data['form'] = self.read(
            ['date_from', 'enable_filter', 'debit_credit', 'date_to',
             'account_report_id', 'target_move', 'view_format',
             'company_id','filter_selection'])[0]
        used_context = self._build_contexts(data)
        used_context.update({'strict_range':True})
        data['form']['used_context'] = dict(
            used_context,
            lang=self.env.context.get('lang') or 'en_US')

        if self.enable_filter:
            # get amount from filter
            data_copy = data['form'].copy()
            if self.multi_period:
                filter_result = filter_method.range_comparison(data['form'],self.year_from,self.year_to,self.from_id,self.to_id)
            else:
                filter_result = [(f"{self.to_id.name} {self.year_to.name if self.year_to.name else ''}",filter_method.set_filter_data(data['form'],self.to_id,self.year_to))]
            
            filter_result.sort(key=lambda x:x[1].get('from_month'))
            for line in filter_result:
                data_copy['used_context'].update({'date_from':line[1].get('from_month'),'date_to':line[1].get('to_month')})
                data_copy.update({'date_from':line[1].get('from_month'),'date_to':line[1].get('to_month')})
                res = self.get_account_lines(data_copy)
                res = self._get_level(res)
                result.append((line[0],res))

        filter_result = filter_method.set_filter_data(data['form'],self.from_id,self.year_from)
        data['form']['used_context'].update({'date_from':filter_result.get('from_month'),'date_to':filter_result.get('to_month')})
        data['form'].update({'date_from':filter_result.get('from_month'),'date_to':filter_result.get('to_month')})

        report_lines = self.get_account_lines(data['form'])
        report_lines = self._get_level(report_lines)
        # find the journal items of these accounts
        # journal_items = self.find_journal_items(report_lines, data['form'])

        # currency = self._get_currency()
        # data['journal_items'] = journal_items
        data['currency'] = self._get_currency()
        data['filter'] = [result]
        data['report_lines'] = report_lines
        # dictionary to string
        # dts = str(data).replace("'",'"')
        # self.datas = dts
        if self._context.get('pdf'):
            return self.env.ref(
                'base_accounting_kit.financial_report_pdf').report_action(self,data)
        else:
            data['form'].update({
                'date_from':str(data['form']['date_from']),
                'date_to':str(data['form']['date_to'])
            })
            data['form']['used_context'].update({
                'date_from':str(data['form']['used_context']['date_from']),
                'date_to':str(data['form']['used_context']['date_to']),
            })
            data.update({'form':[data['form']]})
            self.datas = json.dumps(data)
            self.account_name_json = json.dumps(getattr(self,'_mapping_account_name'))
            getattr(self,'_mapping_account_name').clear()
            return self.env.ref(
                'base_accounting_kit.financial_report_excel').report_action(self)

    def _get_level(self,data):
        def set_report_level(rec):
            """This function is used to set the level of each item.
            This level will be used to set the alignment in the dynamic reports."""
            level = 1
            if not rec['parent']:
                return level
            else:
                for line in data:
                    key = 'a_id' if line['type'] == 'account' else 'id'
                    if line[key] == rec['parent']:
                        return level + set_report_level(line)

        for item in data:
            item['balance'] = round(item['balance'], 2)
            if not item['parent']:
                item['level'] = 1
                parent = item
                report_name = item['name']
                id = item['id']
                report_id = item['r_id']
            else:
                item['level'] = set_report_level(item)
        return data
    def _compute_account_balance(self, accounts):
        """ compute the balance, debit
        and credit for the provided accounts
        """
        mapping = {
            'balance':
                "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0)"
                " as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0)
                                   for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = (
                self.env['account.move.line']._query_get())
            tables = tables.replace(
                '"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = ("SELECT account_id as id, " +
                       ', '.join(mapping.values()) +
                       " FROM " + tables +
                       " WHERE account_id IN %s " +
                       filters +
                       " GROUP BY account_id")
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, reports):
        """returns a dictionary with key=the ID of a record and
         value=the credit, debit and balance amount
        computed for this record. If the record is of type :
        'accounts' : it's the sum of the linked accounts
        'account_type' : it's the sum of leaf accounts with
         such an account_type
        'account_report' : it's the amount of the related report
        'sum' : it's the sum of the children of this record
         (aka a 'view' record)"""
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(
                    report.account_ids
                )
                for value in \
                        res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts
                #  with such an account type
                accounts = self.env['account.account'].search([
                    ('user_type_id', 'in', report.account_type_ids.ids)
                ])
                res[report.id]['account'] = self._compute_account_balance(
                    accounts)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
        return res

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([
            ('id', '=', data['account_report_id'][0])
        ])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(
            data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in \
                            comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            r_name = str(report.name)
            # r_name = r_name.replace(" ", "-") + "-"
            r_name = re.sub('[^0-9a-zA-Z]+', '', r_name)
            if report.parent_id:
                p_name = str(report.parent_id.name)
                p_name = re.sub('[^0-9a-zA-Z]+', '', p_name) + str(
                    report.parent_id.id)
                # p_name = p_name.replace(" ", "-") +
                #  "-" + str(report.parent_id.id)
            else:
                p_name = False
            vals = {
                'r_id': report.id,
                'id': r_name + str(report.id),
                'sequence': report.sequence,
                'parent': p_name,
                'name': report.name,
                'balance': res[report.id]['balance'] * int(report.sign),
                'type': 'report',
                'level': bool(
                    report.style_overwrite) and report.style_overwrite or
                         report.level,
                'account_type': report.type or False,
                # used to underline the financial report balances
            }
            if report.name not in getattr(self,'_mapping_account_name'):
                getattr(self,'_mapping_account_name').append(report.name)

            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * int(
                    report.sign)

            lines.append(vals)
            if report.display_detail == 'no_detail':
                # the rest of the loop is
                # used to display the details of the
                #  financial report, so it's not needed here.
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value \
                        in res[report.id]['account'].items():
                    # if there are accounts to display,
                    #  we add them to the lines with a level equals
                    #  to their level in
                    # the COA + 1 (to avoid having them with a too low level
                    #  that would conflicts with the level of data
                    # financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    # new_r_name = str(report.name)
                    # new_r_name = new_r_name.replace(" ", "-") + "-"
                    vals = {
                        'account': account.id,
                        'a_id': account.code + re.sub('[^0-9a-zA-Z]+', 'acnt',
                                                      account.name) + str(
                            account.id),
                        'name': account.code + '-' + account.name,
                        'balance': value['balance'] * int(report.sign) or 0.0,
                        'type': 'account',
                        'parent': r_name + str(report.id),
                        'level': (
                                report.display_detail == 'detail_with_hierarchy' and
                                4),
                        'account_type': account.internal_type,
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not account.company_id.currency_id.is_zero(
                                vals['debit']) or \
                                not account.company_id.currency_id.is_zero(
                                    vals['credit']):
                            flag = True
                    if not account.company_id.currency_id.is_zero(
                            vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * int(
                            report.sign)
                        if not account.company_id.currency_id.is_zero(
                                vals['balance_cmp']):
                            flag = True
                    if flag:
                        if vals['name'] not in getattr(self,'_mapping_account_name'):
                            getattr(self,'_mapping_account_name').append(vals['name'])
                        sub_lines.append(vals)
                lines += sorted(sub_lines,
                                key=lambda sub_line: sub_line['name'])
        return lines

    def find_journal_items(self, report_lines, form):
        cr = self.env.cr
        journal_items = []
        for i in report_lines:
            if i['type'] == 'account':
                account = i['account']
                if form['target_move'] == 'posted':
                    search_query = "select aml.id, am.id as j_id, aml.account_id, aml.date," \
                                   " aml.name as label, am.name, " \
                                   + "(aml.debit-aml.credit) as balance, aml.debit, aml.credit, aml.partner_id " \
                                   + " from account_move_line aml join account_move am " \
                                     "on (aml.move_id=am.id and am.state=%s) " \
                                   + " where aml.account_id=%s"
                    vals = [form['target_move']]
                else:
                    search_query = "select aml.id, am.id as j_id, aml.account_id, aml.date, " \
                                   "aml.name as label, am.name, " \
                                   + "(aml.debit-aml.credit) as balance, aml.debit, aml.credit, aml.partner_id " \
                                   + " from account_move_line aml join account_move am on (aml.move_id=am.id) " \
                                   + " where aml.account_id=%s"
                    vals = []
                if form['date_from'] and form['date_to']:
                    search_query += " and aml.date>=%s and aml.date<=%s"
                    vals += [account, form['date_from'], form['date_to']]
                elif form['date_from']:
                    search_query += " and aml.date>=%s"
                    vals += [account, form['date_from']]
                elif form['date_to']:
                    search_query += " and aml.date<=%s"
                    vals += [account, form['date_to']]
                else:
                    vals += [account]
                cr.execute(search_query, tuple(vals))
                items = cr.dictfetchall()

                for j in items:
                    temp = j['id']
                    j['id'] = re.sub('[^0-9a-zA-Z]+', '', i['name']) + str(
                        temp)
                    j['p_id'] = str(i['a_id'])
                    j['type'] = 'journal_item'
                    journal_items.append(j)
        return journal_items

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(
            self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.company.currency_id.symbol


class ProfitLossPdf(models.AbstractModel):
    """ Abstract model for generating PDF report value and send to template """

    _name = 'report.base_accounting_kit.report_financial'
    _description = 'Financial Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Provide report values to template """
        ctx = {
            'data': data,
            # 'journal_items': data['journal_items'],
            'report_lines': data['report_lines'],
            'account_report': data['form']['account_report_id'][1],
            'currency': data['currency'],
        }
        return ctx
