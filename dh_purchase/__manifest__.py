# -*- coding: utf-8 -*-
{
    'name': "dh_purchase",

    'summary': "Restrict product creation after purchase order recieved",

    'description': """
    This module restricts the creation of products after a purchase order has been received.
    It ensures that products are not created in the system unless they are part of a purchase order.
    """,

    'author': "Datahat Solutions",
    'website': "https://www.datahatsolutions.com",
    "license" : "LGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','stock','sale_management','product','account', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/epcs_security.xml',
        'views/bulk_invoice_view.xml',
        'views/invoice_button.xml',
        'views/purchase_inherit.xml',
    ],
}

