{
    'name': "Policy Management",
    'author': 'VarietyIT, Ahmed Mohamed',
    'version': '18.2',
    'depends': [
        'base', 'web', 'board', 'product', 'hr'
    ],
    'data': [
        #  Security File
        'security/ir.model.access.csv',

        # Sequence File
        'data/sequence.xml',

        #  Basic Menu
        'views/menu_view.xml',
        # 'views/policy_management_dashboard.xml',
        'views/risks_view.xml',

        # Configuration Menu
        'views/policy_category_view.xml',
        'views/insurance_for_view.xml',

        # Medical Menu
        'views/medical_policy_view.xml',
        'views/medical_due_renewal_view.xml',
        'views/medical_risks_view.xml',

        # Life Menu
        'views/life_policy_view.xml',
        'views/life_due_renewal_view.xml',
        'views/life_risks_view.xml',

        # Motor Menu
        'views/motor_policy_view.xml',
        'views/motor_due_renewal_view.xml',
        'views/motor_risks_view.xml',

        # Fire Menu
        'views/fire_policy_view.xml',
        'views/fire_due_renewal_view.xml',
        'views/fire_risks_view.xml',

        # Engineering Menu
        'views/eng_policy_view.xml',
        'views/eng_due_renewal_view.xml',
        'views/eng_risks_view.xml',

        # MISC Menu
        'views/misc_policy_view.xml',
        'views/misc_due_renewal_view.xml',
        'views/misc_risks_view.xml',

        # Marine Menu
        'views/marine_policy_view.xml',
        'views/marine_due_renewal_view.xml',
        'views/marine_risks_view.xml',
    ],


    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
