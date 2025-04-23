{
    'name': 'Restrict Contact Tags for Users',
    'version': '1.0',
    'depends': ['base', 'contacts','hr'],
    'license': 'LGPL-3',
    'data': [
        # 'security/partner_access_rule.xml',
        'security/customer_type_access.xml',
        'views/res_user_view.xml',
        'views/res_partner_view.xml',
             ],
    'installable': True,
    'auto_install': False,
}