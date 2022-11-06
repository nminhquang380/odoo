import logging
from odoo import fields, models
import tempfile
import os
import base64
import pandas as pd
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

_logger = logging.getLogger(__name__)


class DotDangKyNhuCau(models.Model):
    _name = "dot_dang_ky_nhu_cau"
    _description = "Đợt đăng ký nhu cầu"
    _rec_name = "ten_dot_dang_ky_nhu_cau"

    ten_dot_dang_ky_nhu_cau = fields.Char(string="Tên đợt đăng ký nhu cầu")
    ky_hoc_id = fields.Many2one(comodel_name="ky_nam_hoc",
                                ondelete="cascade",
                                string="Kỳ năm học",
                                required=True)
    ky_ctk = fields.Integer(string="Số thứ tự kỳ trong chương trình khung")
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                           string="Hình thức đào tạo")
    so_tin_chi_toi_thieu = fields.Integer(string="Số tín chỉ tối thiểu",
                                          default=14)
    so_tin_chi_toi_da = fields.Integer(string="Số tín chỉ tối đa", default=21)
    khoi_lop_ids = fields.Many2many(
        comodel_name="khoi_lop",
        relation="dot_dang_ky_nhu_cau_khoi_lop",
        # column1='dot_dang_ky_nhu_cau_id',
        string="Danh sách khối lớp",
    )
    # ket_thuc = fields.Boolean(
    #     default=False,
    #     # compute='_compute_tu_dong``_ket_thuc_dot_dang_ky_nhu_cau',
    #     # store=True,
    #     string="Đã kết thúc?",
    # )
    ngay_bat_dau_nhu_cau = fields.Date("Ngày bắt đầu đăng ký nhu cầu")
    ngay_ket_thuc_nhu_cau = fields.Date("Ngày kết thúc đăng ký nhu cầu")
    trang_thai = fields.Char("Trạng thái",
                            compute="_compute_trang_thai")
    phieu_dang_ky_hoc_phan_id = fields.One2many(
        "phieu_dang_ky_hoc_phan",
        "dot_dang_ky_id",
        string="Danh sách phiếu đăng ký nhu cầu",
    )
    nv_hoc_phan_id = fields.One2many(
        "nv_hoc_phan",
        "dot_dk_nhu_cau_id",
        string="Danh sách nv đăng ký nhu cầu",
    )

    @api.onchange("ngay_bat_dau_nhu_cau", "ngay_ket_thuc_nhu_cau")
    def _compute_trang_thai(self):
        for record in self:
            if record.ngay_bat_dau_nhu_cau and record.ngay_ket_thuc_nhu_cau:
                today = date.today()
                if today < record.ngay_bat_dau_nhu_cau:
                    record.trang_thai = "Chưa bắt đầu"
                elif today >= record.ngay_bat_dau_nhu_cau and today <= record.ngay_ket_thuc_nhu_cau:
                    record.trang_thai = "Đang diễn ra"
                elif today > record.ngay_ket_thuc_nhu_cau:
                    record.trang_thai = "Đã kết thúc"
            else:
                record.trang_thai = "Chưa xác định"

    @api.constrains("ngay_bat_dau_nhu_cau", "ngay_ket_thuc_nhu_cau")
    def validate_thoi_gian(self):
        if self.ngay_bat_dau_nhu_cau and self.ngay_ket_thuc_nhu_cau:
            if self.ngay_bat_dau_nhu_cau > self.ngay_ket_thuc_nhu_cau:
                raise ValidationError(
                    "Thời gian kết thúc đợt đăng ký nhu cầu không được sớm hơn thời gian bắt đầu!"
                )

    # hàm này check xem khối lớp được chọn có nằm trong kỳ năm học hay không để tránh bị lỗi.
    @api.constrains("ky_hoc_id", "khoi_lop_ids")
    def check_xem_khoi_lop_co_thuoc_ky_nam_hoc_khong(self):
        if self.khoi_lop_ids and self.ky_hoc_id:
            for khoi_lop in self.khoi_lop_ids:
                if khoi_lop not in self.ky_hoc_id.khoi_lop_ids:
                    raise ValidationError(
                        ("Khối lớp %s không nằm trong kỳ năm học %s !") %
                        (khoi_lop.ten_khoi_lop, self.ky_hoc_id.ma_ky_nam_hoc))

    @api.constrains("khoi_lop_ids")
    def check_khoi_lop_ton_tai(self):
        if not self.khoi_lop_ids:
            raise ValidationError(
                "Danh sách khối lớp không được bỏ trống!"
            )

    # @api.depends('ngay_ket_thuc_nhu_cau')
    # def _compute_tu_dong_ket_thuc_dot_dang_ky_nhu_cau(self):
    #       '''
    #           TODO:tư động tính ngày kết thúc cho đợt đăng ký nhu cầu
    #
    #        '''
    #     for record in self:
    #         record.ket_thuc = False

    # @api.onchange('khoi_lop_ids')
    # def cap_nhat_dot_dang_ky_nhu_cau_vao_bang_khoi_lop(self):
    #     for record in self:
    #         for each_khoi_lop in record.khoi_lop_ids:
    #             khoi_lop = self.env['khoi_lop'].search(
    #                 [('id','=',each_khoi_lop.id)]
    #             )
    #             khoi_lop.write({
    #                 'dot_dang_ky_nhu_cau_ids','=',
    #             })

    def action_view_thong_ke_dang_ky_nhu_cau(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.action_nv_hoc_phan")
        action["context"] = {
            "default_dot_dk_nhu_cau_id": self.id,
            "group_by": ["hoc_phan_id"],
        }
        action["domain"] = [("dot_dk_nhu_cau_id", "=", self.id)]
        return action

    def action_export_thong_ke_dang_ky_nhu_cau(self):
        export_data = {}
        danh_sach_nhu_cau_theo_dot = self.env["nv_hoc_phan"].search([
            ("dot_dk_nhu_cau_id", "=", self.id)
        ])
        for record in danh_sach_nhu_cau_theo_dot:
            key_hoc_phan = (record.ten_hoc_phan,
                            record.hoc_phan_id.ma_hoc_phan_moi)
            if key_hoc_phan not in export_data:
                export_data[key_hoc_phan] = {
                    "tongSoSinhVien": 1,
                    "tongHocPhi": record.hoc_phi,
                }
            else:
                export_data[key_hoc_phan]["tongSoSinhVien"] += 1
                export_data[key_hoc_phan]["tongHocPhi"] += record.hoc_phi
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        df1 = pd.DataFrame(columns=[
            "tenHocPhan", "maHocPhan", "tongSoSinhVien", "tongHocPhi"
        ])
        phieu_dk_nhu_cau = self.env["phieu_dang_ky_hoc_phan"].search([
            ("dot_dang_ky_id", "=", self.id),
            ("nv_hoc_phan_id", "!=", False),
        ])
        tongSinhVienDangKy = len(phieu_dk_nhu_cau)
        tongSinhVienToanKhoa = 0
        for khoi_lop in self.khoi_lop_ids:
            for lop_hanh_chinh in khoi_lop.lop_hanh_chinh_ids:
                tongSinhVienToanKhoa += len(lop_hanh_chinh.sinh_vien_ids)
        for hp in export_data:
            tongSoSinhVien = export_data[hp]["tongSoSinhVien"]
            tongHocPhi = export_data[hp]["tongHocPhi"]
            df1 = df1.append(
                {
                    "tenHocPhan": hp[0],
                    "maHocPhan": hp[1],
                    "tongSoSinhVien": tongSoSinhVien,
                    "tongHocPhi": tongHocPhi,
                },
                ignore_index=True)
        df1 = df1.append(
            {
                "tenHocPhan":
                f"Tổng số sinh viên đã đăng ký: {tongSinhVienDangKy}",
                "maHocPhan": "",
                "tongSoSinhVien": "",
                "tongHocPhi": "",
            },
            ignore_index=True)
        df1 = df1.append(
            {
                "tenHocPhan":
                f"Tổng số sinh viên toàn đợt đăng ký: {tongSinhVienToanKhoa}",
                "maHocPhan": "",
                "tongSoSinhVien": "",
                "tongHocPhi": "",
            },
            ignore_index=True)

        df2 = pd.DataFrame(columns=[
            "Tên sinh viên", "Mã sinh viên", "Tên môn học", "Mã môn học",
            "Số tín chỉ", "Học phí môn học"
        ])

        danh_sach_svc_mh_dang_ky_nhu_cau = self.env["nv_hoc_phan"].search([
            ("dot_dk_nhu_cau_id", "=", self.id)
        ])
        for vl in danh_sach_svc_mh_dang_ky_nhu_cau:
            df2 = df2.append(
                {
                    "Tên sinh viên": vl.sinh_vien_id.name,
                    "Mã sinh viên": vl.sinh_vien_id.ma_dinh_danh,
                    "Tên môn học": vl.hoc_phan_id.ten_hoc_phan,
                    "Mã môn học": vl.hoc_phan_id.ma_hoc_phan_moi,
                    "Số tín chỉ": vl.so_tin_chi,
                    "Học phí môn học": vl.hoc_phi,
                },
                ignore_index=True)
        with pd.ExcelWriter(path) as writer:
            df1.to_excel(writer,
                         sheet_name='Tổng hợp số liệu chung',
                         index=False)
            df2.to_excel(writer,
                         sheet_name='Danh sách sinh viên-môn học',
                         index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "tong_hop_so_lieu_nhu_cau.xlsx",
            'store_fname': 'thsl.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }
