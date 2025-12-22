# -*- coding: utf-8 -*-
# Part of Quocent. See LICENSE file for full copyright and licensing details.
{
    'name': "Allow Sale Order Link On Documents",
    'version': "1.0",
    'license': 'LGPL-3',
    'summary': "Link Documents on Sale Order.",
    'description': "This module is use to link documents on sale order.",
    'category': "Documents",
    'author': "Quocent Pvt. Ltd.",
    'website': "https://www.quocent.com",
    'depends': ["base", "documents", "sale_management"],
    'data': [
        "views/qcent_sale_document_customization.xml",
        "views/qcent_documents_document_customization.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'allow_so_linkage_on_documents/static/src/views/inspector/custom_document_inspector.js',
            'allow_so_linkage_on_documents/static/src/views/inspector/custom_document_inspector.xml',
        ]
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
}
