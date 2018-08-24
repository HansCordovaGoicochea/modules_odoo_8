# Point of sale merge lines

This module change behavior on Odoo point of sale for allow merge same product lines even when you add a product in between.

Limitations:
* Currently Odoo point of sale harcoded the limitation to merge only of products from unit of measure with the id 1 (https://github.com/odoo/odoo/blob/8.0/addons/point_of_sale/static/src/js/models.js#L150)