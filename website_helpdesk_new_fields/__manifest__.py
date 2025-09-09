{
    'name': 'Website Helpdesk New Fields',
    'author': 'Youssef',
    'category': 'Website',
    'version': '18.0.0.1.0',
    'depends': ['website_helpdesk', 'vit_facility_management_config'],
    'data': [
        'views/website_helpdesk_template_inherit.xml',
        'views/helpdesk_ticket_view.xml',
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
