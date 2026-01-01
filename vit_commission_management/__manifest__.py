{
    'name': 'Commission Management',
    'author': 'VarietyIT, Youssef Ahmed',
    'version': '18.0.0.1.0',
    'depends': ['base', 'account', 'stock', 'vit_contract_management'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/create_comm_product.xml',

        # Inherited Views
        'views/account_move_view.xml',
        'views/account_installation_view.xml',

        'views/medical_policy_view.xml',
        'views/life_policy_view.xml',
        'views/motor_policy_view.xml',
        'views/fire_policy_view.xml',
        'views/eng_policy_view.xml',
        'views/misc_policy_view.xml',
        'views/marine_policy_view.xml',

        # Views
        'views/commission_management_view.xml',

        # Basic Menu
        'views/menu_view.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'vit_commission_management/static/src/js/handel_commission_form.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
