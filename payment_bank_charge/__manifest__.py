{
    'name': 'Payment Bank Charge',
    'author': 'Youssef',
    'version': '18.0.0.1.0',
    'category': 'Accounting',
    'depends': ['account', 'payment_internal_transfer'],
    'data': [
        'views/account_journal_view.xml',
        'views/account_payment_register_wizard_view.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
