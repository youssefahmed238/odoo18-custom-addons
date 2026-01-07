{
    'name': 'Invoice Thermal Report',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'category': 'Accounting',
    'depends': ['account', 'vit_html_thermal_base'],
    'data': [
        'views/account_move_view.xml',

        'reports/invoice_report_views.xml',
        'reports/report_invoice_thermal.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
