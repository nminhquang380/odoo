from odoo import models, fields, api
from .constants_user_groups import portal_user, internal_user, public_user

class ChuyenGiaCN(models.Model):
    _name = "chuyen_gia_cn"
    _description = "Chuyên gia công nghệ"
    _inherit = ["tac_nhan"]

    user_group_string = "website_slides.group_website_slides_chuyen_gia_cong_nghe"
    vai_tro_string = _name
    internal_string = ""
