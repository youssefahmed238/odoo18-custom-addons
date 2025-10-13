{
    'name': 'Add Petty Functionality',
    'author': 'Youssef',
    'version': '18.0.0.1.0',
    'category': 'Accounting',
    'depends': ['account', 'hr', 'payment_internal_transfer'],
    'data': [
        'views/account_journal_view.xml',
        'views/account_payment_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
