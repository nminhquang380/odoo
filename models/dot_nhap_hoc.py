from odoo.exceptions import ValidationError
from odoo import fields, models, api
import pandas as pd
import tempfile, os, base64
import logging

_logger = logging.getLogger(__name__)


class DotNhapHoc(models.Model):
    _name = "dot_nhap_hoc"
    _description = "Đợt nhập học"
    _rec_name = "ten_dot"

    ten_dot = fields.Char("Tên đợt nhập học", size=200)
    thu_tu_dot = fields.Integer(string="Số thứ tự đợt nhập học (theo năm học)")
    #  ref đến khoi_lop nhưng chỉ cần thông tin khóa - ngành
    khoa_nganh_ids = fields.One2many("khoi_lop",
                                     "dot_nhap_hoc_id",
                                     required=True,
                                     string="Danh sách khối lớp")

    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        string="Hình thức đào tạo",
        related="khoa_sinh_vien_id.hinh_thuc_dao_tao_id")

    nam_hoc_id = fields.Many2one(
        comodel_name="nam_hoc",
        ondelete="cascade",
        compute="_compute_nam_hoc",
        store=True,
        string="Năm học",
    )

    khoa_sinh_vien_id = fields.Many2one(
        comodel_name="khoa_sinh_vien",
        ondelete="cascade",
        required=True,
        string="Khóa sinh viên",
    )

    tong_so_sinh_vien = fields.Integer(string="Tổng số sinh viên", )

    thoi_gian_nhap_hoc = fields.Date("Thời gian nhập học")

    @api.depends("khoa_sinh_vien_id")
    def _compute_nam_hoc(self):
        self.nam_hoc_id = (self.env["nam_hoc"].search([
            ("id", "=", self.khoa_sinh_vien_id.nam_hoc.id)
        ]).id)
