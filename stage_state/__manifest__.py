{
    'name': 'Stage State',
    'version': '1.0',
    'author': 'Youssef Ahmed',
    'depends': ['base', 'web'],
    'assets': {
        'web.assets_backend': [
            'stage_state/static/src/components/custom_stage_state/custom_stage_state.js',
            'stage_state/static/src/components/custom_stage_state/custom_stage_state.xml',
            'stage_state/static/src/components/custom_stage_state/custom_stage_state.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
