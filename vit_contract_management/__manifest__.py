{
    'name': 'Contract Management',
    'author': 'VarietyIT, Youssef Ahmed',
    'version': '18.0.0.1.0',
    'depends': ['base', 'mail', 'vit_policy_management'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/ir_sequence.xml',
        'data/ir_cron.xml',

        # Views
        'views/insurance_contract_view.xml',

        #  Basic Menu
        'views/menu_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
