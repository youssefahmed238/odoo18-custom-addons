{
    'name': 'Payment Thermal Report',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'category': 'Accounting',
    'depends': ['account', 'vit_html_thermal_base'],
    'data': [
        'views/account_payment_view.xml',

        'reports/payment_report_views.xml',
        'reports/report_payment_thermal.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
