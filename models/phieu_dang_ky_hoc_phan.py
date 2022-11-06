import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .env_thanh_toan import base_url_hoc_phi
import re
import requests
import datetime
import random
import uuid

_logger = logging.getLogger(__name__)


class PhieuDangKyHocPhan(models.Model):
    _name = "phieu_dang_ky_hoc_phan"
    _description = "Phiếu đăng ký học phần"

    dot_dang_ky_id = fields.Many2one(
        "dot_dang_ky_nhu_cau", string="Đợt đăng ký nhu cầu"
    )
    ky_hoc_id = fields.Many2one(
        "ky_nam_hoc",
        related="dot_dang_ky_id.ky_hoc_id",
        store=True,
        string="Kỳ năm học",
    )
    sinh_vien_id = fields.Many2one("sinh_vien", string="Sinh viên")
    nv_hoc_phan_id = fields.One2many(
        "nv_hoc_phan",
        "phieu_dang_ky_hoc_phan_id",
        string="Danh sách nguyện vọng học phần",
    )
    tong_so_tin_chi = fields.Integer(
        "Tổng số tín chỉ", compute="_compute_tong_so_tin_chi", store=True
    )
    tong_hoc_phi = fields.Integer(
        compute="_compute_tong_hoc_phi", store=True, string="Tổng học phí"
    )
    name = fields.Char(
        "Họ và tên", size=100, related="sinh_vien_id.name", store=True
    )
    ma_sinh_vien = fields.Char(
        "Mã sinh viên", size=20, related="sinh_vien_id.ma_dinh_danh", store=True
    )
    lop_hanh_chinh_id = fields.Many2one(
        comodel_name='lop_hanh_chinh',
        related='sinh_vien_id.lop_hanh_chinh_id',
        ondelete='set null',
        string="Mã lớp hành chính"
    )
    ten_lop_hanh_chinh = fields.Char(
        related="lop_hanh_chinh_id.ten_lop_hanh_chinh",
        store=True,
        string="Tên lớp hành chính")
    so_dien_thoai = fields.Char("Số điện thoại", size=20)
    giang_vien_id = fields.Many2one(
        comodel_name="nhan_vien",
        # ondelete='set null',
        string="Giảng viên phụ trách",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        related="dot_dang_ky_id.hinh_thuc_dao_tao_id",
        store=True,
        string="Hình thức đào tạo"
    )
    hoc_phi_ap_dung = fields.Many2one(
        string="Học phí 1 tín chỉ áp dụng", size=100, related="sinh_vien_id.khoa_nganh_id.hoc_phi_ids", store=True
    )
    don_vi_thu_huong = fields.Many2one(
        comodel_name='danh_muc.don_vi_thu_huong',
        ondelete='set null',
        string="Đơn vị thụ hưởng"
    )
    don_vi_thu_huong_stk = fields.Char(
        related="don_vi_thu_huong.so_tai_khoan",
        store=True,
        string="Số tài khoản"
    )
    don_vi_thu_huong_ten_ngan_hang = fields.Char(
        related="don_vi_thu_huong.ten_ngan_hang",
        store=True,
        string="Tên ngân hàng"
    )
    don_vi_thu_huong_chi_nhanh = fields.Char(
        related="don_vi_thu_huong.chi_nhanh",
        store=True,
        string="Chi nhánh"
    )
    ghi_chu = fields.Char(
        related="don_vi_thu_huong.ghi_chu",
        store=True,
        string="Ghi chú"
    )

    def get_metadata_hinh_thuc_dao_tao(self,record):
        if record.lop_hanh_chinh_id.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao:
            return {"hinhThucDaoTaoId": record.lop_hanh_chinh_id.hinh_thuc_dao_tao_id.id,
                    "loai": 'Học phí theo kỳ',
                    "phamVi": 'Hình thức đào tạo', }
        else:
            return {"hinh_thuc_dao_tao":"Chưa xác định"} # đoạn này cần tổng quát hóa thành constants/enums

    @api.constrains("so_dien_thoai")
    def validate_phone(self):
        if self.so_dien_thoai:
            match = re.match("^[0-9]\d{9,10}$", self.so_dien_thoai)
            if not match:
                raise ValidationError("Số điện thoại không đúng!")

    # cần bổ sung them logic tính toognr học phí khi tạo 1 phiếu đăng ký học phần
    @api.depends("nv_hoc_phan_id")
    def _compute_tong_so_tin_chi(self):
        for record in self:
            tong_so_tin_chi = 0
            if record.nv_hoc_phan_id:
                for nv_hoc_phan in record.nv_hoc_phan_id:
                    tong_so_tin_chi += nv_hoc_phan.so_tin_chi
            record.tong_so_tin_chi = tong_so_tin_chi

    @api.depends(
        "nv_hoc_phan_id.hoc_phi",
    )
    def _compute_tong_hoc_phi(self):
        for record in self:
            try:
                danh_sach_nguyen_vong_hoc_phan = self.env["nv_hoc_phan"].search(
                    [("phieu_dang_ky_hoc_phan_id", "=", record.id)]
                )
                record.tong_hoc_phi = 0
                for each_record in danh_sach_nguyen_vong_hoc_phan: # tính tổng số học phí theo tín chỉ
                    record.tong_hoc_phi += each_record.hoc_phi

            except Exception as e:
                _logger.error(e)
