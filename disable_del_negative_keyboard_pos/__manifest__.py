# -*- coding: utf-8 -*-
{
    'name': "Disable Del and - Keyboard Pos",


    'author': "Keroles Ayed",
    'website': "www.linkedin.com/in/keroles-ayed-19788b14a",

    'depends': ['point_of_sale'],

    'assets': {
        'point_of_sale.assets': [
            ('replace', 'point_of_sale/static/src/js/Misc/NumberBuffer.js',
             'disable_del_negative_keyboard_pos/static/src/js/NumberBuffer.js',),
        ],
    },

}
