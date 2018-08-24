# -*- coding: utf-8 -*-
import base64

try:
    from reportlab.graphics.barcode import createBarcodeDrawing, \
            getCodes
except :
    print ("ERROR IMPORTING REPORT LAB")


def _get_code():
    """get availble code """
    return [(r, r) for r in getCodes()]


class BarCo(object):

    def get_image(self,value,width, hight, code='QR'):
        """ genrating image for barcode """
        options = {}
        if width: options['width'] = width
        if hight: options['hight'] = hight

        ret_val = createBarcodeDrawing(code, value=str(value), **options)
        return base64.encodestring(ret_val.asString('jpg'))

    def generate_image(self, digest_value):
        "button function for genrating image """
        image = self.get_image(value=digest_value, width=150, hight=180)
        return image
#
# a = BarCo()
# b = a.generate_image('5J8yrgmwpuyN6tSdWaN+660LSwk=')
# print (b)