{
    'name': 'Partner Balance Report',
    'summary': 'Partner Balance Report',
    'description': """
        show the Partner Balance,
        Partner Balance,
        Balance,
        Partner,
        Partner Ledger,
        Total Balnce,
    """,
    'version': '2.0',
    'category': 'Accounting',
    'author': 'APPSGATE FZC LLC',
    'depends': ['base', 'web','account'],

    'data': [
        'security/ir.model.access.csv',
        # 'views/external_layout_override.xml',
        'report/report_temp.xml',
        'report/partner_bal_Report.xml',
        'wizard/partner_bal.xml',

    ],

    'images': [
        'static/src/img/main-screenshot.png'
    ],

    'external_dependencies': {
        'python': ['xlsxwriter', 'xlrd']
    },

    'license': 'AGPL-3',
    'price': '10',
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': True,
}
