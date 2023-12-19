{
    "name": "Nota Penjualan",
    "version": "1.0",
    "depends": [
            "base",
            "sale",
        "account",
        "delivery",
    ],
    "author": "ugiesugiharti90@gmail.com, butirpadi",
    "category": "Penjualan",
    "description": """\

Manage
======================================================================

* this is sales system module

""",
    "data": [
        "report/report_nota.xml",
        "report/bootstrap_style.xml",
        "view/res_company.xml",
        "view/account_invoice.xml",
        "view/product_template.xml",
        "view/delivery_carrier_form.xml",
        "view/view_order_form_with_carrier.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
