# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2017 Alphasoft
#    (<http://www.alphasoft.co.id>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Budget Purchase Alert',
    'version': '14.0.0.1.0',
    'author': "Alphasoft",
    'sequence': 1,
    'website': 'http://www.alphasoft.co.id',
    'images':  ['images/main_screenshot.png'],
    'category': 'Purchasing',
    'summary': 'Budget Alert on Purchase & Invoice a module by Alphasoft.',
    'depends': ['purchase', 'base_account_budget', 'aos_account_budget_alert'],
    'description': """
Module based on Alphasoft
===================================================== 
""",
    'demo': [],
    'test': [],
    'data': [
        # 'security/account_budget_security.xml',
        # 'wizard/password_auth_view.xml',
        # 'views/account_budget_view.xml',
        'views/purchase_order_view.xml',
        'views/purchase_order_budget_alert_view.xml',
     ],
    'css': [],
    'js': [],
    'price': 85.00,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}
