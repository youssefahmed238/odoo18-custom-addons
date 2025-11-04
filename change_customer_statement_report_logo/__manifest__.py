{
    'name': 'Change Customer Statement Report Logo',
    'author': 'Youssef',
    'version': '18.0.0.1.0',
    'category': 'Accounting',
    'depends': ['account_reports'],
    'data': [
        'reports/bank_statement_report.xml',
    ],
    'assets': {
        'web.assets_common': [
            'change_customer_statement_report_logo/static/src/img/bank_logo.png',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
