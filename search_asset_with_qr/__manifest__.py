{
    'name': 'Search Asset with QR Code',
    'version': '18.0.0.1.0',
    'depends': ['vit_facility_management_config', 'web'],
    'assets': {
        'web.assets_backend': [
            'search_asset_with_qr/static/lib/jsqr.min.js',  # must come first
            'search_asset_with_qr/static/src/scss/qr_scan.scss',
            'search_asset_with_qr/static/src/js/controlScanAssetButton.js',
            'search_asset_with_qr/static/src/xml/scan_asset_button.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
