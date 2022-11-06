from odoo import fields, models, api
import logging
import datetime

_logger = logging.getLogger(__name__)

thoi_gian_hoc = [
    {},
    {"gio_bat_dau": "07:30", "gio_ket_thuc": "07:45"},
    {"gio_bat_dau": "08:00", "gio_ket_thuc": "08:45"},
    {"gio_bat_dau": "09:00", "gio_ket_thuc": "09:45"},
    {"gio_bat_dau": "10:00", "gio_ket_thuc": "10:45"},
    {"gio_bat_dau": "11:00", "gio_ket_thuc": "11:45"},
    {"gio_bat_dau": "12:00", "gio_ket_thuc": "12:45"},
    {"gio_bat_dau": "13:00", "gio_ket_thuc": "13:45"},
    {"gio_bat_dau": "14:00", "gio_ket_thuc": "14:45"},
    {"gio_bat_dau": "15:00", "gio_ket_thuc": "15:45"},
    {"gio_bat_dau": "16:00", "gio_ket_thuc": "16:45"},
    {"gio_bat_dau": "17:00", "gio_ket_thuc": "17:45"},
    {"gio_bat_dau": "18:00", "gio_ket_thuc": "18:45"},
    {"gio_bat_dau": "19:00", "gio_ket_thuc": "19:45"},
]


class ThoiKhoaBieu(models.Model):
    _name = "thoi_khoa_bieu"
    _description = "Thời khóa biểu"

    mon_hoc = fields.Many2one("slide.channel", string="Môn học")
    nhom_to = fields.Integer("Nhóm tổ")
    nhom_lop = fields.Char("Mã nhóm lớp tín chỉ", size=200)
    to_th = fields.Integer("Tổ thực hành")
    ten_lop = fields.Char("Tên lớp", size=200)
    tong_so_sinh_vien = fields.Integer("Tổng số sinh viên")
    thu_kieu_so = fields.Integer("Thứ kiểu số")
    tiet_bd = fields.Integer("Tiết bắt đầu")
    so_tiet = fields.Integer("Số tiết")
    ma_ph = fields.Char("Mã phòng học", size=20)
    ds_tuan_hoc = fields.Char("Danh sách tuần học", size=20)
    tuan_bd = fields.Integer("Tuần bắt đầu")
    ma_nv = fields.Char("Mã NV", size=20)
    ten_day_du_nv = fields.Char("Tên đầy đủ nhân viên", size=500)
    ten_ph = fields.Char("Tên phòng học", size=500)
    ngay_bd = fields.Date("Ngày bắt đầu")
    ngay_kt = fields.Date("Ngày kết thúc")
    ten_to_hop = fields.Char("Tên tổ hợp", size=10)
    ds_tiet = fields.Char("Danh sách tiết", size=15)
    so_tin_chi = fields.Integer("Số tín chỉ")
    ma_lop_tkb = fields.Char("Mã lớp thời khóa biểu", size=20)
    is_online = fields.Boolean("Online?")

    # TODO: implement create logic
    @api.model
    def create(self, values):
        res = super(ThoiKhoaBieu, self).create(values)

        # đoạn này nếu import từ file excel thì cần validate xem dấu - ở file excel là dấu gạch ngắn hay dài
        # vì 2 dấu gạch này có mã ASCII khác nhau nên khi search trong db nếu không validate + replace
        # thì sẽ không ra được kết quả search lớp tín chỉ
        # chr(8211) là ký tự - nhưng dài hơn, được generate bằng auto correct của các phần mềm soạn thảo văn bản
        values["ten_lop"].replace(chr(8211), "-")
        lop_tin_chi = self.env["lop_tin_chi"].search(
            [("ten_lop_tin_chi", "=", values["ten_lop"])]
        )
        nhom_lop_tin_chi = self.env["nhom_lop_tin_chi"].search(
            [("ma_nhom_lop_tin_chi", "=", values["nhom_lop_tin_chi"])]
        )
        current_date = datetime.datetime.strptime(
            values["ngay_bd"], "%Y-%m-%d")
        while current_date.weekday() != int(values["thu_kieu_so"]):
            current_date += datetime.timedelta(days=1)

        so_thu_tu_buoi_hoc = 1
        gio_bat_dau = thoi_gian_hoc[values["tiet_bd"]]["gio_bat_dau"]
        gio_ket_thuc = thoi_gian_hoc[values["tiet_bd"] + values["so_tiet"] - 1][
            "gio_ket_thuc"
        ]
        ngay_gio_hoc = current_date.replace(
            hour=int(gio_bat_dau.split(":")[0]),
            minute=int(gio_bat_dau.split(":")[1]),
        )
        ngay_gio_ket_thuc = current_date.replace(
            hour=int(gio_ket_thuc.split(":")[0]),
            minute=int(gio_ket_thuc.split(":")[1]),
        )
        buoi_hoc_data = {
            "ngay_gio_hoc": ngay_gio_hoc,
            "ngay_gio_ket_thuc": ngay_gio_ket_thuc,
            "dia_diem": "offline",
            "loai_hinh": "offline",
            "tu_ngay": values["ngay_bd"],
            # "den_ngay": values["ngay_kt"],
            "thu_hoc": str(values["thu_kieu_so"]),
            "tiet_bat_dau": values["tiet_bd"],
            "tiet_ket_thuc": values["so_tiet"],
            "lop_tin_chi_id": lop_tin_chi.id,
            "nhom_lop_tin_chi_id": nhom_lop_tin_chi.id,
            "is_zoom_meeting": values["is_online"],
            "so_thu_tu_buoi_hoc": so_thu_tu_buoi_hoc,
        }
        try:
            self.env["buoi_hoc"].create(buoi_hoc_data)
        except Exception as e:
            _logger.error(
                "\n\n error while creating buoi_hoc from tkb {}".format(
                    e)
            )
            current_date += datetime.timedelta(days=7)
        return res
        # pass
