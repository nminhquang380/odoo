import logging
import json
from re import M

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class NhomLopTinChi(models.Model):
    _name = "nhom_lop_tin_chi"
    _description = "Nhóm lớp tín chỉ"
    _rec_name = "ma_nhom_lop_tin_chi"

    giang_vien_ids = fields.Many2many(comodel_name="nhan_vien",
                                      string="Danh sách giảng viên")
    giang_vien_id = fields.Many2one(comodel_name="nhan_vien",
                                    string="Giảng viên")
    ten_giang_vien = fields.Char(string="Tên giảng viên",
                                 related="giang_vien_id.name",
                                 store=True)

    ma_nhom_lop_tin_chi = fields.Char(
        string="Mã nhóm lớp tín chỉ",
        compute="_compute_ma_nhom_lop_tin_chi",
        store="True",
    )
    so_thu_tu_nhom = fields.Integer(string="Số thứ tự nhóm", )
    ten_hoc_phan = fields.Char(related="ma_lop_tin_chi_id.ten_hoc_phan",
                               store=True)
    ma_lop_tin_chi_id = fields.Many2one(comodel_name="lop_tin_chi",
                                        ondelete="cascade",
                                        string="Mã lớp tín chỉ")
    dot_dk_tin_chi_id = fields.Many2one(
        comodel_name="dot_dang_ky_tin_chi",
        string="Đợt đăng ký tín chỉ",
        related="ma_lop_tin_chi_id.dot_dk_tin_chi_id",
        store=True)
    loai_nhom_lop = fields.Selection(
        [("LT", "Lý thuyết"), ("TH", "Thực hành")],
        string="Loại lớp",
    )
    si_so = fields.Integer("Sĩ số tối đa")

    sinh_vien_ids = fields.Many2many(comodel_name="sinh_vien",
                                     string="Danh sách sinh viên")
    buoi_hoc_ids = fields.One2many("buoi_hoc", "nhom_lop_tin_chi_id",
                                   "Danh sách buổi học")
    ma_hoa_lich_hoc = fields.Char("Mã hóa lịch học",
                                  compute="_compute_ma_hoa_lich_hoc",
                                  store=True)
    tong_so_sinh_vien = fields.Integer("Tổng số sinh viên",
                                       compute="_compute_tong_so_sinh_vien",
                                       store=True)

    @api.depends("sinh_vien_ids")
    def _compute_tong_so_sinh_vien(self):
        for record in self:
            if record.sinh_vien_ids:
                record.tong_so_sinh_vien = len(record.sinh_vien_ids)
            else:
                record.tong_so_sinh_vien = False

    @api.depends("so_thu_tu_nhom", "ma_lop_tin_chi_id.ma_lop", "loai_nhom_lop")
    def _compute_ma_nhom_lop_tin_chi(self):
        for record in self:
            if (record.ma_lop_tin_chi_id.ma_lop and record.loai_nhom_lop
                    and record.so_thu_tu_nhom):
                stt = str(record.so_thu_tu_nhom)
                if len(stt) == 1:
                    stt = stt.zfill(2)
                record.ma_nhom_lop_tin_chi = (record.ma_lop_tin_chi_id.ma_lop +
                                              "-" + stt + "-" +
                                              record.loai_nhom_lop)

    @api.depends("buoi_hoc_ids.ngay_bd", "buoi_hoc_ids.phong_hoc",
                 "buoi_hoc_ids.tiet_bd", "buoi_hoc_ids.so_tiet",
                 "ma_lop_tin_chi_id.ky_nam_hoc_id.thoi_gian_bat_dau")
    def _compute_ma_hoa_lich_hoc(self):
        for record in self:
            if record.buoi_hoc_ids:
                mapss = {}
                for buoi_hoc in record.buoi_hoc_ids:
                    thu = buoi_hoc.thu_kieu_so
                    tuan = buoi_hoc.ngay_bd.isocalendar(
                    )[1] - record.ma_lop_tin_chi_id.ky_nam_hoc_id.thoi_gian_bat_dau.isocalendar(
                    )[1] + 1
                    obj = f"{thu};{buoi_hoc.tiet_bd.tiet_hoc};{buoi_hoc.so_tiet}"
                    if obj in mapss:
                        mapss[obj].append(tuan)
                    else:
                        mapss[obj] = [tuan]

                res = []
                for key in mapss:
                    h = key.split(";")
                    res.append({
                        "thu": h[0],
                        "tietBatDau": h[1],
                        "soTiet": h[2],
                        "danhSachTuan": sorted(mapss[key]),
                    })
                res = sorted(res, key=lambda k: k['thu'])
                record.ma_hoa_lich_hoc = json.dumps(res, ensure_ascii=False)
            else:
                record.ma_hoa_lich_hoc = ""
