{
    'name': 'Website Helpdesk New Fields',
    'author': 'Youssef',
    'category': 'Website',
    'version': '18.0.0.1.0',
    'depends': ['website', 'website_helpdesk'],
    'data': [
        'views/helpdesk_templates_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_helpdesk_new_fields/static/src/js/handel_website_helpdesk_new_fields.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
}
