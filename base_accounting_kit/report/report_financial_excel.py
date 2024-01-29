from odoo import models,fields
import json
DEFAULT_COLUMN = {'default_header_row':6,'default_header_col':0,'default_row':7,'default_col':0}
DEFAULT_COLUMN_ALPHABET = [
    'A','B','C','D','E','F','G','H','I','J','K','L',
    'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',

    'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL',
    'AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ',

    'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL',
    'BM','BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ',

    'CA','CB','CC','CD','CE','CF','CG','CH','CI','CJ','CK','CL',
    'CM','CN','CO','CP','CQ','CR','CS','CT','CU','CV','CW','CX','CY','CZ',

    'DA','DB','DC','DD','DE','DF','DG','DH','DI','DJ','DK','DL',
    'DM','DN','DO','DP','DQ','DR','DS','DT','DU','DV','DW','DX','DY','DZ',

    'EA','EB','EC','ED','EE','EF','EG','EH','EI','EJ','EK','EL',
    'EM','EN','EO','EP','EQ','ER','ES','ET','EU','EV','EW','EX','EY','EZ',
]
class PartnerXlsx(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_financial_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data,object):
        company = self.env.company.name
        sheet = workbook.add_worksheet("Test")
        sheet.set_column("A:AZ",20)
        data = json.loads(object.datas)
        sheet.set_column("B:B",34)
        formats = workbook.add_format
        filter_obj = data.get('filter')[0] if data.get('filter') else {}
        sheet.merge_range("A1:C1",company,formats({'bold':True,'align':'center','valign':'vcenter','font_size':16}))
        sheet.merge_range("A2:C2",data['form'][0]['account_report_id'][1],formats({'bold':True,'valign':'vcenter','align':'center','font_size':14}))
        if not object.enable_filter:
            title = f"{data['form'][0]['date_from'] if data['form'][0]['date_from'] else ''} {'- ' + data['form'][0]['date_to'] if data['form'][0]['date_to'] else ''}"
            sheet.merge_range("A3:C3",title,formats({'align':'center','valign':'vcenter'}))
        sheet.write("A6","Target Moves",formats({'align':'center'})) 
        if data['form'][0]['target_move'] == 'all':
            sheet.write("B6",'All Entries',formats({'valign':'vcenter','align':'center'}))
        else:
            sheet.write("B6",'All Posted Entries',formats({'valign':'vcenter','align':'center'}))

        # sheet.merge_range("F7:G8","DATE",formats({'valign':'vcenter'}))

        # set variabel untuk header column dan row dimulai setelah column balance yaitu 0
        header_row = DEFAULT_COLUMN['default_header_row']
        header_col = DEFAULT_COLUMN['default_header_col']
        column = DEFAULT_COLUMN_ALPHABET
        sheet.write(header_row,header_col,"Name")
        header_col += 1
        if data['form'][0]['debit_credit']:
            sheet.write(header_row,header_col,"Debit")
            header_col +=1

            sheet.write(header_row,header_col,"Credit")
            header_col += 1
        if object.enable_filter:
            sheet.write(header_row,header_col,object.from_id.name + " " +(object.year_from.name if object.year_from else '') )
            header_col += 1
        else:
            sheet.write(header_row,header_col,"Balance")
            header_col += 1
        if filter_obj: 
            filter_obj.sort(key = lambda r: fields.Date.from_string(r[-1]), reverse = data['reverse_sort'])
            for line in filter_obj:
                sheet.write(header_row,header_col,line[0])
                header_col += 1
        sheet.write(header_row, header_col, 'SUM')
        line_row = DEFAULT_COLUMN['default_row']
        line_col = DEFAULT_COLUMN['default_col']
        last_line_col = 0
        format_amount = formats({'align':'right','num_format':'[$Rp-421] #,##0;[$Rp-421] -#,##0'})
        font_weight = formats({'bold':True})
        col_amount = 0
        for name in json.loads(object.account_name_json):

            first_filter = next(filter(lambda x: x if x.get('name') == name else {}, data['report_lines']), {})

            if first_filter.get('level',0) > 3:
                font_weight = formats({'bold':False})
            line_col += 1
            col_amount = line_col
            
            if data['form'][0]['debit_credit'] == 1:
                sheet.write(line_row,line_col,first_filter.get('debit') if first_filter.get('debit') != 0 else 0,format_amount)
                line_col += 1

                sheet.write(line_row,line_col,first_filter.get('credit') if first_filter.get('credit') != 0 else 0,format_amount)
                line_col += 1

            sheet.write(line_row,line_col,first_filter.get('balance') if first_filter.get('balance') != 0 else 0,format_amount)

            if data.get('filter'):
                line_col += 1
                for index in range(0,len(filter_obj)):
                    second_filter = next(filter(lambda x: x if x.get('name') == name else {}, filter_obj[index][1]), {})
                    sheet.write(line_row,line_col,second_filter.get('balance') if second_filter.get('balance') != 0 else 0,format_amount)
                    line_col += 1
                    if second_filter.get('level',0) > 3:
                        font_weight = formats({'bold':False})
            sheet.write_formula(line_row, line_col,"=SUM(%(first_col)s%(line_row)s:%(last_col)s%(line_row)s)" % {'first_col': column[col_amount], 'last_col':column[line_col - 1], 'line_row':line_row + 1}, format_amount)
            last_line_col = line_col
            line_col = 0
            spacing_indent = '  ' * first_filter.get('level',0)
            sheet.write(line_row,line_col,spacing_indent + name,font_weight)
            line_row += 1
            # name dan balance adalah column static yang selalu ada
        # if data.get('filter'):
        #     keys = data['filter'][0].keys()
        #     line_col = last_line_col
        #     for key in list(keys)[::-1]:
        #         header_col += 1
        #         sheet.write(header_row,header_col,key)
        #         line_col += 1
        #         line_row = DEFAULT_COLUMN['default_row']
        #         for v in data['filter'][0][key]:
        #             sheet.write(line_row,line_col,v['balance'] if v.get('balance') != 0 else 'Rp0',format_amount)
        #             line_row += 1