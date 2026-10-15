{
    'name': 'Approval Request',
    'version': '2.0',
    'summary': 'Enterprise Approval Request System',
    'category': 'Tools',
    'author': 'Sahil',
    'depends': ['base', 'mail'],

    'data': [

        
        'security/security.xml',
        'security/ir.model.access.csv',

        
        'data/sequence.xml',
        'data/mail_template.xml',

        
        'views/category_views.xml',
        'views/request_views.xml',
        'views/approval_line_views.xml',
        'views/wizard_views.xml',

        
        'report/report.xml',
        'report/report_template.xml',

        
        'views/menu.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}