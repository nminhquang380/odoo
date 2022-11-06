from odoo.exceptions import ValidationError
from pandas.core.construction import is_empty_data
from odoo import api, fields, models
import pandas as pd
import base64
import tempfile
import os
import logging

_logger = logging.getLogger(__name__)


class KhoiLop(models.Model):
    _name = "khoi_lop"
    _description = "Khối lớp"
    _rec_name = "ten_khoi_lop"

    ten_khoi_lop = fields.Char("Tên khối lớp",
                               compute="_compute_ten_khoi_lop",
                               store=True)
    ten_khoi_lop_import = fields.Char(string="Tên khối lớp (import)")
    khoa_nganh_id = fields.Many2one("khoa_nganh", string="Khóa-ngành")
    dot_nhap_hoc_id = fields.Many2one("dot_nhap_hoc", string="Đợt nhập học")
    ky_nam_hoc_ids = fields.Many2many("ky_nam_hoc",
                                      "ky_nam_hoc_khoi_lop",
                                      string="Danh sách kỳ năm học")
    khoa_sinh_vien_id = fields.Many2one(related="khoa_nganh_id.khoa_sinh_vien_id",
                                    store=True,
                                    string="Khóa sinh viên")
    nam_hoc_id = fields.Many2one(related="khoa_sinh_vien_id.nam_hoc",
                                store=True,
                                string="Năm học")
    ctk_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        related="khoa_nganh_id.ctk_id",
        string="Chương trình khung ngành",
    )
    # ctk_chuyen_nganh_id = fields.Many2one(
    #     comodel_name="chuong_trinh_khung",
    #     related="khoa_chuyen_nganh_id.ctk_id",
    #     string="Chương trình khung chuyên ngành",
    # )

    si_so = fields.Integer("Sĩ số")
    lop_hanh_chinh_ids = fields.One2many("lop_hanh_chinh",
                                         "khoi_lop_id",
                                         string="Danh sách lớp hành chính")

    ky_ctk_hien_tai = fields.Integer(
        default=1,
        compute="_compute_ky_ctk_khoi_lop",
        store=True,
        string="Kỳ chương trình khung hiện tại",
    )
    dot_dang_ky_nhu_cau_ids = fields.Many2many(
        comodel_name="dot_dang_ky_nhu_cau",
        relation="dot_dang_ky_nhu_cau_khoi_lop",
        # column2='khoi_lop_id',
        string="Danh sách các đợt đăng ký nhu cầu",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name='hinh_thuc_dao_tao',
        ondelete='set null',
        related='khoa_nganh_id.hinh_thuc_dao_tao_id',
        store=True,
        string='Hình thức đào tạo')

    @api.depends("khoa_nganh_id.ten_khoa_nganh", "dot_nhap_hoc_id.ten_dot")
    def _compute_ten_khoi_lop(self):
        for record in self:
            if record.ten_khoi_lop_import:
                record.ten_khoi_lop = record.ten_khoi_lop_import
            elif record.khoa_nganh_id.ten_khoa_nganh and record.dot_nhap_hoc_id.ten_dot:
                record.ten_khoi_lop = (record.khoa_nganh_id.ten_khoa_nganh +
                                       "-" + record.dot_nhap_hoc_id.ten_dot)
            else:
                record.ten_khoi_lop = record.ten_khoi_lop

    def tao_lop_hanh_chinh(self):
        if self.si_so:
            ds_sinh_vien = []
            for i, sv in enumerate(self.sinh_vien_ids):
                ds_sinh_vien.append(sv.id)
                if (i + 1) % self.si_so == 0:
                    val = {
                        # đổi convention tên lớp hành chính
                        "ten_lop_hanh_chinh":
                        f'{"Lớp-HC"}-{self.khoa_nganh_id.ten_khoa_nganh}-{int((i + self.si_so) / self.si_so)}',
                        "khoi_lop_id": self.id,
                        "sinh_vien_ids": ds_sinh_vien,
                    }
                    self.env["lop_hanh_chinh"].create(val)
                    ds_sinh_vien.clear()
            if len(ds_sinh_vien) > 0:
                val = {
                    "ten_lop_hanh_chinh":
                    f'{"Lớp-HC"}-{self.khoa_nganh_id.ten_khoa_nganh}-{int((i + self.si_so) / self.si_so)}',
                    "khoi_lop_id": self.id,
                    "sinh_vien_ids": ds_sinh_vien,
                }
                self.env["lop_hanh_chinh"].create(val)

    @api.depends("dot_dang_ky_nhu_cau_ids")
    def _compute_ky_ctk_khoi_lop(self):
        for record in self:
            dot_dang_ky_nhu_cau_da_ket_thuc = len(
                record.dot_dang_ky_nhu_cau_ids)
            record.ky_ctk_hien_tai = dot_dang_ky_nhu_cau_da_ket_thuc
            _logger.info("khóa ngành = {}".format(
                record.khoa_nganh_id.ten_khoa_nganh))

            bieu_gia_1_tin_chi = record.khoa_nganh_id.bieu_gia_id
            hoc_phi_min = bieu_gia_1_tin_chi.gia_tien * 14
            hoc_phi_max = bieu_gia_1_tin_chi.gia_tien * 21
            so_tin_chi = 0

            hoc_phi_hien_tai = so_tin_chi * bieu_gia_1_tin_chi.gia_tien
            # tìm ctk của khối lớp hiện tại, nếu có nhiều CTK -> chưa xử lý -> lấy ctk mới nhất
            if record.khoa_nganh_id:  # fix lỗi xóa đợt đki nhu cầu của các khối lớp không có CTK
                ctk_hien_tai = self.env["chuong_trinh_khung"].search([
                    ("khoa_nganh_ids", "in", [record.khoa_nganh_id.id])
                ])

                if ctk_hien_tai:
                    # lấy danh sách môn học của kỳ CTK hiện tại
                    danh_sach_mon_hoc = self.env["mon_hoc_dieu_kien"].search([
                        ("ctk_id", "=", ctk_hien_tai[-1].id),
                        ("hoc_ky", "=", record.ky_ctk_hien_tai),
                    ])
                    for hoc_phan in danh_sach_mon_hoc:
                        # nv_hoc_phan = self.env["nv_hoc_phan"].search(
                        #     [
                        #         ("hoc_phan_id", "=", hoc_phan.hoc_phan_id.id),
                        #         (
                        #             "phieu_dang_ky_hoc_phan_id.ky_hoc_id",
                        #             "=",
                        #             record.dot_dang_ky_nhu_cau_ids.ky_hoc_id.id,
                        #         ),
                        #     ]
                        # )
                        so_tin_chi += hoc_phan.hoc_phan_id.so_tin_chi
