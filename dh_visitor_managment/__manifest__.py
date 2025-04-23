{
    'name': 'Visitor Managment System',
    'version': '18.0.0.1',
    'summary': 'Module for managing Visitor profiles',
    'description': """A module for managing Visitor profiles.""",
    'depends': ['base','sale','hr','contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'data/visitor_sequence.xml', 
        'wizard/visitor_approval_wizard.xml',
        'views/visitor.xml',
        'views/visitor_configuration.xml',
        'data/mail_template.xml',
        'views/visitor_managment.xml',
        'reports/visitor_layout.xml',
        'reports/visitor_visit_layout.xml',
        'reports/visitor_template.xml',
        'menus/menu.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}




