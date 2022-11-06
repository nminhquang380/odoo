import logging

from odoo import models, fields, api

from .constants_model_name import model_sinh_vien, model_ky_nam_hoc, model_chuong_trinh_khung
from .constants_of_selection_fields import trang_thai_sinh_vien_hoc_ky, quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi

_logger = logging.getLogger(__name__)


class SinhVienDiemTongKet(models.Model):
    """
        Class này mô hình hóa sinh viên - điểm tổng kết,  gồm các thông tin:
    """
    _name = "sinh_vien_diem_tong_ket"
    _description = "Quản lý thông tin sinh viên - điểm tổng kết"
    _rec_name = "sinh_vien_id"

    sinh_vien_id = fields.Many2one(comodel_name=model_sinh_vien,
                                   ondelete="cascade",
                                   string="Sinh viên")
    ma_dinh_danh = fields.Char(related="sinh_vien_id.ma_dinh_danh",
                               store=True,
                               string="Mã sinh viên")
    ten_sv = fields.Char(related="sinh_vien_id.name",
                         store=True,
                         string="Tên đầy đủ")
    ctk_nganh_id = fields.Many2one(comodel_name=model_chuong_trinh_khung,
                                   ondelete="cascade",
                                   related="sinh_vien_id.ctk_nganh_id",
                                   store=True,
                                   string="Chương trình khung ngành")
    ctk_chuyen_nganh_id = fields.Many2one(
        comodel_name=model_chuong_trinh_khung,
        ondelete="cascade",
        related="sinh_vien_id.ctk_chuyen_nganh_id",
        store=True,
        string="Chương trình khung chuyên ngành")

    tong_so_tin_chi_duoc_mien = fields.Integer(
        string="Tổng số tín chỉ được miễn"
    )  # giá trị này cần được tính theo kết quả quy đổi các học phần (nếu có) tại thời điểm đăng ký nhu cầu học tập
    tong_so_tin_chi_da_hoc = fields.Integer(
        string="Số tín chỉ sinh viên đã học")
    tong_so_tin_chi_tich_luy = fields.Integer(
        string="Số tín chỉ sinh viên tích lũy")
    tong_so_tin_chi_truot = fields.Integer("Tổng số tín chỉ trượt")
    diem_tb_tich_luy_thang_4 = fields.Float(string="Điểm TBCTL thang 4", compute="_compute_diem_tong_ket", store=True)
    xep_loai_hoc_luc = fields.Char(string="Xếp loại học lực")
    sv_hp_ds_ids = fields.One2many("sv_hp_ds", "sinh_vien_diem_tong_ket_id")

    _sql_constraints = [('unique_diem_tong_ket_sinh_vien',
                         'unique(sinh_vien_id)',
                         "Sinh viên đã có bản ghi điểm tổng kết")]

    @api.depends("sv_hp_ds_ids", "sv_hp_ds_ids.diem_thang_4")
    def _compute_diem_tong_ket(self):
        for record in self:
            diem_tich_luy = 0
            tong_diem = 0
            tc_tich_luy = 0
            tong_tc = 0
            tong_tc_duoc_mien = 0
            for vl in record.sv_hp_ds_ids:
                #TODO cần check cả môn học có ở trong ctk không
                if vl.hoc_phan_id and vl.hoc_phan_id.hoc_phan_tinh_diem:
                    if vl.trang_thai == 'Đạt' or vl.trang_thai == 'Miễn':
                        diem_tich_luy += float(vl.diem_thang_4)*float(vl.so_tin_chi)
                        tc_tich_luy += float(vl.so_tin_chi)
                        tong_tc += float(vl.so_tin_chi)
                        tong_diem += float(vl.diem_thang_4)*float(vl.so_tin_chi)
                        if vl.trang_thai == 'Miễn':
                            tong_tc_duoc_mien += float(vl.so_tin_chi)
                    else:
                        tong_diem += float(vl.diem_thang_4)*float(vl.so_tin_chi)
                        tong_tc += float(vl.so_tin_chi)
            record.tong_so_tin_chi_tich_luy = tc_tich_luy
            if diem_tich_luy and tc_tich_luy:
                record.diem_tb_tich_luy_thang_4 = float(diem_tich_luy/tc_tich_luy)

            record.tong_so_tin_chi_da_hoc = tong_tc
            record.tong_so_tin_chi_duoc_mien = tong_tc_duoc_mien
