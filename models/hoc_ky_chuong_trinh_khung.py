from odoo import fields, models
from .constants_of_selection_fields import hoc_ky_selection, loai_ky_selection


class HocKyChuongTrinhKhung(models.Model):
    _name = "hoc_ky_chuong_trinh_khung"
    _description = "Học kỳ-chương trình khung"

    hoc_ky = fields.Selection(
        selection=hoc_ky_selection,
        string="Học kỳ",
    )
    loai_ky = fields.Selection(
        selection=loai_ky_selection,
        string="Loại kỳ",
    )
    ctk_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        string="Chương trình khung",
    )
