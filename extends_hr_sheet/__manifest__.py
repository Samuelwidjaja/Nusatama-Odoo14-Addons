{

'name': 'Extend Module - Extend HR expense',
'summary': 'extends module hr by handaru ap nusatama berkah',
'version': '1.0',
'author': 'Handaru A P',
'category': 'Human Resources',
'depends': ['hr_expense'],
'data' : [
    'views/extended_hr_expense_sheet_view.xml',
    'views/extended_hr_expense_report.xml',

        ],
'installable': True,
'Application': True,
'auto_install': False,



}