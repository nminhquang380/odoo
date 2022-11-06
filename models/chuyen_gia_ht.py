from odoo import models, fields, api


class ChuyenGiaHT(models.Model):
    _name = "chuyen_gia_ht"
    _description = "Chuyên gia học thuật"
    _inherit = ["tac_nhan"]

    user_group_string = "website_slides.group_website_slides_chuyen_gia_hoc_thuat"
    vai_tro_string = _name
