    # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Login/Sign In With WhatsApp | Odoo Signup with WhatsApp | Two Factor Authentication (2FA) with WhatsApp | Reset Password with WhatsApp | Odoo V19 Enterprise | WhatsApp Cloud API',
    'version': '18.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'WhatsApp',
    'live_test_url': 'https://youtu.be/vuNxtezupY4',
    'website': 'www.techultrasolutions.com',
    'summary': """Odoo WhatsApp Login is a comprehensive module that integrates WhatsApp with Odoo, providing a seamless and secure authentication experience. With this module, userscan log in and sign up to Odoo using their WhatsApp account, eliminating the need for traditional usernames and passwords. Additionally, the module offers Two-Factor Authentication (2FA) using WhatsApp, ensuring an extra layer of security for Odoo users. In case of a forgotten password, users can easily reset it using WhatsApp.WhatsApp SignUp.
        Odoo WhatsApp Login is a comprehensive module that integrates WhatsApp with Odoo, providing a seamless and secure authentication experience.
        Odoo Meta WhatsApp Graph API
        Odoo V18 Enterprise Edition
        Odoo V18 Enterprise WhatsApp Integration
        V18 Community WhatsApp
        Enterprise WhatsApp
        Enterprise
        WhatsApp Enterprise
        Odoo WhatsApp Enterprise
        Odoo WhatsApp Cloud API
        WhatsApp Cloud API
        WhatsApp Enterprise Edition
        Odoo WhatsApp Login, WhatsApp Authentication, Odoo Security, WhatsApp Integration, Two-Factor Authentication, 2FA, Password Reset, Odoo Module, WhatsApp Login, Odoo Signup
    """,
    'description': """
        Odoo WhatsApp Login is a comprehensive module that integrates WhatsApp with Odoo, providing a seamless and secure authentication experience. With this module, userscan log in and sign up to Odoo using their WhatsApp account, eliminating the need for traditional usernames and passwords. Additionally, the module offers Two-Factor Authentication (2FA) using WhatsApp, ensuring an extra layer of security for Odoo users. In case of a forgotten password, users can easily reset it using WhatsApp.WhatsApp SignUp.
        Odoo WhatsApp Login is a comprehensive module that integrates WhatsApp with Odoo, providing a seamless and secure authentication experience.
        Odoo WhatsApp Integration
        Odoo Meta WhatsApp Graph API
        Odoo V18 Enterprise Edition
        Odoo V18 Enterprise WhatsApp Integration
        V18 Enterprise WhatsApp
        Enterprise WhatsApp
        Enterprise
        WhatsApp Enterprise
        Odoo WhatsApp Enterprise
        Odoo WhatsApp Cloud API
        WhatsApp Cloud API
        WhatsApp Enterprise Edition
        Odoo WhatsApp Login, WhatsApp Authentication, Odoo Security, WhatsApp Integration, Two-Factor Authentication, 2FA, Password Reset, Odoo Module, WhatsApp Login, Odoo Signup
    """,
    'depends': ['auth_signup', 'odoo_all_in_one_whatsapp_ent', 'sms', 'vit_sms_infinito_gateway'],
    'data': [
        "data/wa_template.xml",
        "security/ir.model.access.csv",
        "views/res_user_inherit.xml",
        "views/whatsapp_signup_login_templates.xml",
        "views/res_config.xml",
        "wizard/whatsapp_otp_auth_totp_views.xml",
        ],
    'assets': {
        'web.assets_frontend': [
            'odoo_whatsapp_login/static/src/lib/utils.js',
            'odoo_whatsapp_login/static/src/lib/intelinputmin.js',
        ],
    },
    "price": 79,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
    'images': ['static/description/main_screen.gif'],
}
