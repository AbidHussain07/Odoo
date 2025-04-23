# -*- coding: utf-8 -*-
{
    'name': "desi_dabba",

    'summary': "Generate daily delivery orders for subscription-based tiffin services.",

    "license" : "LGPL-3",

    'author': "Desi Boyz",
    'website': "https://www.desidabba.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['sale_subscription', 'stock','website_sale','report_xlsx',],

    'data': [
        'security/ir.model.access.csv',
        'data/holiday_dates.xml',
        "wizard/cancel_delivery.xml",
        "wizard/delivery_record.xml",
        'views/views.xml',
        # 'views/checkout.xml',
        'views/desi_dabba_address.xml',
        'views/desi_dabba_info.xml',
        # 'views/templates.xml',
        'views/subscription_view.xml',
        'views/technical_view.xml',
        'views/menu.xml',
        'report/daily_delivery.xml',
        'report/report_template.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'desi_dabba/static/src/js/complex_address.js',
            'desi_dabba/static/src/js/custom_validation.js',
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
