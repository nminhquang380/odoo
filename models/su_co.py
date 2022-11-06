
from odoo import models, fields

import logging

_logger = logging.getLogger(__name__)

class SuCo(models.Model):
    _name = "qldt.su_co"
    _description = "Quản lý danh sách sự cố"

    ten_su_co = fields.Char(string="Tên sự cố")
    mo_ta_ngan = fields.Char(string="Mô tả ngắn")
    mo_ta_chi_tiet = fields.Html(string="Mô tả chi tiết")
    link_anh_dinh_kem = fields.Char(string="Link ảnh chụp màn hình")
    # huong_dan = fields.Char(string="Hướng dẫn",default="")