# -*- coding: utf-8 -*-

import uuid
import logging

from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HinhThucDaoTao(models.Model):
    _name = "hinh_thuc_dao_tao"
    _description = "Quản lý hình thức đào tạo"
    _rec_name = "ten_hinh_thuc_dao_tao"

    ten_hinh_thuc_dao_tao = fields.Char(required=True,
                                        size=100,
                                        string="Hình thức đào tạo")
    ten_hinh_thuc_dao_tao_viet_tat = fields.Char(
        string="Tên hình thức đào tạo viết tắt")
    thoi_gian_dao_tao = fields.Float(default=4.5,
                                     required=True,
                                     digits=(2, 1),
                                     string="Thời gian đào tạo (năm)")
    thoi_gian_dao_tao_toi_da = fields.Float(
        compute="_compute_thoi_gian_dao_tao_toi_da",
        store=True,
        default=9,
        required=True,
        digits=(2, 1),
        string="Thời gian đào tạo tối đa (năm)")

    dau_diem_id = fields.Many2many(
        comodel_name="danh_muc.dau_diem",
        string="Danh mục đầu điểm áp dụng",
    )
    danh_muc_quy_tac_tinh_diem_hoc_phan_id = fields.Many2one(
        comodel_name="qldt.danh_muc_quy_tac_danh_gia_tinh_diem_hoc_phan",
        string="Danh mục đầu điểm áp dụng",
    )
    danh_muc_quy_tac_danh_gia_xep_loai_hoc_luc = fields.Many2one("qldt.danh_muc_quy_tac_xep_loai_hoc_luc",
                                                                 string="Danh mục quy tắc xếp loại học lực")
    ma_thanh_toan_bidv = fields.Char(string="Mã thanh toán BIDV")
    url_huong_dan_thanh_toan = fields.Char(string="Url hướng dẫn thanh toán")

    mo_ta = fields.Html(string="Mô tả về hình thức đào tạo")
    nganh_id = fields.Many2many(comodel_name="quan_ly_nganh_hoc.nganh",
                                string="Danh sách ngành học")
    color = fields.Integer()
    _uuid = fields.Char(string="UUID")

    @api.constrains("thoi_gian_dao_tao")
    def validate_thoi_gian_dao_tao(self):
        if self.thoi_gian_dao_tao < 1 or self.thoi_gian_dao_tao > 10:
            raise ValidationError("Thời gian đào tạo không đúng quy định!")

    @api.depends("thoi_gian_dao_tao")
    def _compute_thoi_gian_dao_tao_toi_da(self):
        for record in self:
            if record.thoi_gian_dao_tao:
                record.thoi_gian_dao_tao_toi_da = record.thoi_gian_dao_tao * 2

    @api.model
    def create(self, values):
        _uuid = uuid.uuid4().hex
        values['_uuid'] = _uuid
        res = super(HinhThucDaoTao, self).create(values)
        return res