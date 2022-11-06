# -*- coding: utf-8 -*-

import uuid
import logging

from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)


class ChuyenNganh(models.Model):
    _name = "quan_ly_nganh_hoc.chuyen_nganh"
    _description = "quan_ly_nganh_hoc.chuyen_nganh"

    def _default_access_token(self):
        return str(uuid.uuid4())

    def _get_default_enroll_msg(self):
        return _("Liên hệ với người có thẩm quyền")

    # thông tin cơ bản
    second_id = fields.NewId()
    # name = fields.Char("Tên chuyên ngành", size=50, required=True)
    # ma_chuyen_nganh = fields.Char("Mã chuyên ngành", size=50, required=True)
    mo_ta = fields.Text("Mô tả chuyên ngành", help="Mô tả về ngành")
    mo_ta_ngan = fields.Text(
        "Mô tả ngắn về chuyên ngành", help="Mô tả nhanh về chuyên ngành"
    )
    mo_ta_html = fields.Html(
        "Mô tả chi tiết về chuyên ngành",
        translate=tools.html_translate,
        sanitize_attributes=False,
        sanitize_form=False,
    )
    # một chuyên ngành chỉ thuộc 1 ngành
    nganh_id = fields.Many2one(
        comodel_name="quan_ly_nganh_hoc.nganh",
        ondelete="cascade",
        # delegate=True
        string="Ngành",
    )

    # đoạn này sửa lại link với danh mục chuyên ngành
    ma_chuyen_nganh = fields.Many2one(
        comodel_name="danh_muc.chuyen_nganh",
        ondelete="cascade",
        # delegate=True
        string="Chuyên ngành",
    )
    name = fields.Char(
        "Tên chuyên ngành", related="ma_chuyen_nganh.ten_chuyen_nganh", store=True
    )
    ten_nganh = fields.Char(
        "Tên ngành", related="ma_chuyen_nganh.ma_nganh_hoc.ten_nganh_hoc", store=True
    )
    # name = fields.Char("Tên chuyên ngành", size=50, required=True)

    # một chuyên ngành gồm nhiều môn học chuyên ngành
    # hỏi lại BA xem một môn chuyên ngành chỉ thuộc 1 chuyên ngành
    # hay có thể thuộc nhiều chuyên ngành
    # hoc_phan_chuyen_nganh_id = fields.Many2many(
    #     comodel_name='slide.channel',
    #     relation = 'quan_ly_nganh_hoc_mon_hoc_chuyen_nganh',
    #     column1='id',
    #     string='Các môn thuộc chuyên ngành'
    # )

    # cán bộ / giảng viên liên quan đến chuyên ngành

    # sinh viên liên quan đến chuyên ngành
    # 1 chuyên ngành có thể có nhiều sinh viên đăng ký
    # sinh_vien_chuyen_nganh = fields.One2many(
    #     comodel_name='sinh_vien',
    #     inverse_name='MaChngNg',
    #     string="Sinh viên chuyên ngành"
    # )
    # sinh_vien_count = fields.Integer('Số lượng sinh viên', compute='_compute_sinh_vien_chuyen_nganh')
    # sinh_vien_tot_nghiep_count = fields.Integer('Số sinh viên tốt nghiệp', compute='_compute_sinh_vien_chuyen_nganh_totnghiep')
    sequence = fields.Integer(default=10, help="Thứ tự hiển thị")
    # thông tin khác
    han_dang_ky_chuyen_nganh = fields.Datetime("Hạn đăng ký chuyên ngành")
    color = fields.Integer("Chọn màu", default=0, help="")

    hinh_thuc_dao_tao_ids = fields.Many2many(
        comodel_name="hinh_thuc_dao_tao",
        string="Hình thức đào tạo"
    )

    # #quan hệ với bảng môn học điều kiện
    # mon_hoc_dieu_kien_id = fields.Many2many(
    #     comodel_name='mon_hoc_dieu_kien'
    # )
    #
    # #kỳ học của chuyên ngành - dùng để hiển thị
    # danh_sach_ky_hoc = fields.Many2many(
    #     comodel_name='ky_hoc',
    #     string='Danh sách kỳ học'
    # )

    # COMPUTE Function
    # def _compute_sinh_vien_chuyen_nganh(self):
    #     self.sinh_vien_count = 1
    #
    # def _compute_sinh_vien_chuyen_nganh_totnghiep(self):
    #     self.sinh_vien_tot_nghiep_count = 1

    _sql_constraints = [('unique_ma_chuyen_nganh',
                         'unique(ma_chuyen_nganh)', "Chuyên ngành đã tồn tại.")]

    # Override hamf write cua chuyen_nganh
    def write(self, update_values):
        _logger.info(self.nganh_id)
        _logger.info(".... updating %r" % (update_values))
        res = super(ChuyenNganh, self).write(update_values)
        _logger.info("....%r" % (res))
        _logger.info(self.nganh_id)
