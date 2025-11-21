{
    'name': 'Commission Management',
    'author': 'VarietyIT, Youssef Ahmed',
    'version': '18.0.0.1.0',
    'depends': ['base', 'vit_contract_management'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/medical_policy_view.xml',
        'views/life_policy_view.xml',
        'views/motor_policy_view.xml',
        'views/fire_policy_view.xml',
        'views/eng_policy_view.xml',
        'views/misc_policy_view.xml',
        'views/marine_policy_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
