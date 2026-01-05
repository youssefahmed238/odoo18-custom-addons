{
    'name': 'Thermal Base',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'depends': ['base'],
    'data': [
        'views/res_users_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vit_html_thermal_base/static/src/js/report_action_override.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
