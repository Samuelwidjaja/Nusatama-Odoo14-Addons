# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Gantt View Manufacturing | Manufacturing Gantt View | Manufacturing Gantt",
    "summary": " The Planning view gives you a clear overview of what is already planned and what remains to be planned using Start Date and End Date.",
    "version": "14.0.1",
    "description": """
        Gantt View Manufacturing | Manufacturing Gantt View | Manufacturing Gantt
        ==================
        This addon allows the users to show projects stasks in  gantt view, in a
        simple and graphical way.
        - Gantt View
        - create new MRP Production
        - customize an existing Production
        - TreeView for Gantt Items
        - Deadline Indicator
        - Priority Indicator
        - Progress Indicator
        - Multiple Scales
        - Navigate to Todat, Previous and Next Day
        - Grouping
        - Filter
        - Progress bar on Production
        - Popup Informations
        - Overdue Indicator
        - Milestone in Different Shape
        - Predecessor Links
        - Todyas Marker
        - Sorting
        - Gantt View
        - MRP Gantt
        - Manufacturing Gantt View
        - Manufacturing view
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/web_mrp_gantt_view.png"],
    "category": "Manufacturing",
    "depends": [
        "base",
        "web",
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/mrp_gantt_views.xml",
    ],
    "qweb": [
        'static/src/xml/*.xml',
    ],
    "installable": True,
    "application": True,
    "price"                :  65,
    "currency"             :  "EUR",
    "uninstall_hook"       :  "uninstall_hook",
}
