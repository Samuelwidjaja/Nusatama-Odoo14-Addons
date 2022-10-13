from odoo import models
DEFAULT_COLUMN = {'default_header_row':6,'default_header_col':0,'default_row':7,'default_col':0}

class PartnerXlsx(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_trial_balance_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data,object):
        company = self.env.company.name
        sheet = workbook.add_worksheet("Test")
        sheet.set_column("A:BZ",20)
        sheet.set_column("B:B",34)
        formats = workbook.add_format
        sheet.merge_range("A1:C1",company,formats({'bold':True,'align':'center','valign':'vcenter','font_size':16}))
        sheet.merge_range("A2:C2",'Trial Balance',formats({'bold':True,'valign':'vcenter','align':'center','font_size':14}))
        if not object.enable_filter:
            title = f"{data['form']['date_from'] if data['form']['date_from'] else ''} {'- ' + data['form']['date_to'] if data['form']['date_to'] else ''}"
            sheet.merge_range("A3:C3",title,formats({'align':'center','valign':'vcenter'}))
        sheet.write("A5","Target Moves",formats({'align':'center'})) 
        if data['form']['target_move'] == 'all':
            sheet.write("B5",'All Accounts',formats({'valign':'vcenter','align':'center'}))
        elif data['form']['target_move'] == 'movement':
            sheet.write("B5",'With Movements',formats({'valign':'vcenter','align':'center'}))
        else:
            sheet.write("B5",'With balance not equal to zero',formats({'valign':'vcenter','align':'center'}))

    #     # sheet.merge_range("F7:G8","DATE",formats({'valign':'vcenter'}))

    #     # set variabel untuk header column dan row dimulai setelah column balance yaitu 0
        header_row = DEFAULT_COLUMN['default_header_row']
        header_col = DEFAULT_COLUMN['default_header_col']
        sheet.write(header_row,header_col,"Code")
        header_col += 1
        sheet.write(header_row,header_col,"Account")
        header_col += 1
        sheet.write(header_row,header_col,"Debit")
        header_col += 1
        sheet.write(header_row,header_col,"Credit")
        header_col += 1
        sheet.write(header_row,header_col,"Balance")
        header_col += 1
    #     if object.enable_filter:
    #         sheet.write(header_row,header_col,object.from_id.name + " " +(object.year_from.name if object.year_from else '') )
    #     else:
    #         sheet.write(header_row,header_col,"Balance")

        line_row = DEFAULT_COLUMN['default_row']
        line_col = DEFAULT_COLUMN['default_col']
        last_line_col = 0
        format_amount = formats({'align':'right','num_format':'[$Rp-421] #,###;[$Rp-421] -#,##0'})
        font_weight = formats({'bold':True})
        for line in data['accounts']:
            sheet.write(line_row,line_col,line.get('code'))
            line_col += 1
            sheet.write(line_row,line_col,line.get('name'))
            line_col += 1
            sheet.write(line_row,line_col,line.get('debit') if line.get('debit') != 0 else 'Rp0',format_amount)
            line_col += 1
            sheet.write(line_row,line_col,line.get('credit') if line.get('credit') != 0 else 'Rp0',format_amount)
            line_col += 1
            sheet.write(line_row,line_col,line.get('balance') if line.get('balance') != 0 else 'Rp0',format_amount)
            line_col += 1
            
            line_row += 1
    #         last_line_col = line_col
            line_col = 0
    #         # name dan balance adalah column static yang selalu ada
    #     if data.get('filter'):
    #         keys = data['filter'].keys()
    #         line_col = last_line_col
    #         for key in keys:
    #             header_col += 1
    #             sheet.write(header_row,header_col,key)
    #             line_col += 1
    #             line_row = DEFAULT_COLUMN['default_row']
    #             for v in data['filter'][key]:
    #                 sheet.write(line_row,line_col,v['balance'] if v.get('balance') != 0 else 'Rp0',format_amount)
    #                 line_row += 1