import logging
from calendar import month

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class SinhVienHocPhanDiemSo(models.Model):
    _name = "sv_hp_ds"
    _description = "Sinh viên-học phần-điểm số"

    # TODO: Làm view sv_hp_ds
    sinh_vien_id = fields.Many2one("sinh_vien",
                                   "Sinh viên",
                                   ondelete="cascade")
    ten_sv = fields.Char(related="sinh_vien_id.name",
                         store=True,
                         string="Họ và Tên")  # dùng để hiển thị
    ma_dinh_danh_ten_sv = fields.Char(
        compute="_compute_ma_dinh_danh_ten_sv",
        store=True,
        string="Mã và tên sinh viên")  # dùng để group-by + hiển thị
    ten_khoi_lop = fields.Char(
        related="sinh_vien_id.khoi_lop_id.ten_khoi_lop",
        store=True,
        string="Tên Khối lớp",
    )  # dùng để hiển thị
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop",
        related="sinh_vien_id.khoi_lop_id",
        store=True,
        string="Khối lớp",
    )  # dùng cho search panel bên tay trái
    ten_nganh = fields.Char(
        related="sinh_vien_id.khoi_lop_id.khoa_nganh_id.nganh_id.ten_nganh",
        store=True,
        string="Tên ngành",
    )  # dùng để hiển thị
    ten_lop_hanh_chinh = fields.Char(
        related="sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh",
        store=True,
        string="Lớp hành chính",
    )
    ky_ctk = fields.Char(compute="_compute_ky_ctk",
                         store=True,
                         string="Kỳ CTK")
    hoc_phan_id = fields.Many2one(comodel_name="slide.channel",
                                  ondelete="cascade",
                                  string="Học phần")
    ma_hp_ten_hp = fields.Char(
        compute="_compute_ma_hp_ten_hp",
        store=True,
        string="Mã học phần - tên học phần"
    )  # phục vụ hiển thị + group by trên list/tree view
    ma_hoc_phan_moi = fields.Char(related="hoc_phan_id.ma_hoc_phan_moi",
                                  string="Mã học phần")  # dùng để hiển thị
    so_tin_chi = fields.Integer(related="hoc_phan_id.so_tin_chi",
                                string="Số tín chỉ")  # dùng để hiển thị
    cong_nhan_ket_qua_hoc_tap_id = fields.Many2one("qldt.cong_nhan_kqht",
                                                   "Công nhận kết quả học tập",
                                                   ondelete="cascade")
    diem_hoc_phan = fields.Float(
        # compute="_compute_diem_hoc_phan",
        # store=True,
        readonly=False,
        string="Điểm học phần",
        group_operator=False,
    )
    diem_chu = fields.Char("Điểm chữ")
    diem_thang_4 = fields.Float(string="Điểm thang 4",
                                group_operator=False)
    trang_thai = fields.Selection([("Đạt", "Đạt"), ("Không đạt", "Không đạt"),
                                   ("Chưa có điểm", "Chưa có điểm"),
                                   ("Miễn", "Miễn")],
                                  compute="_compute_trang_thai",
                                  store=True,
                                  string="Trạng thái học phần")
    sv_ltc_ds_ids = fields.One2many("sv_ltc_ds",
                                    "sv_hp_ds_id",
                                    ondelete="cascade")
    # phần này dùng cho việc import điểm từ trung tâm 1 các khóa D17 trở về trước
    diem_lan_1 = fields.Float("Điểm lần 1", group_operator=False)
    diem_lan_2 = fields.Float("Điểm lần 2", group_operator=False)
    diem_lan_3 = fields.Float("Điểm lần 3", group_operator=False)
    diem_lan_4 = fields.Float("Điểm lần 4", group_operator=False)
    diem_lan_5 = fields.Float("Điểm lần 5", group_operator=False)
    diem_quy_doi = fields.Char("Điểm quy đổi")
    ghi_chu = fields.Char("Ghi chú")
    trang_thai_sv = fields.Char("Trạng thái sinh viên")
    sinh_vien_diem_tong_ket_id = fields.Many2one(comodel_name="sinh_vien_diem_tong_ket", compute="_compute_sv_diem_tong_ket", store=True)


    _sql_constraints = [("unique_sv_hp", "UNIQUE(sinh_vien_id, hoc_phan_id)",
                         "Đã tồn tại cặp sinh viên - học phần này.")]

    @api.depends("hoc_phan_id")
    def _compute_ma_hp_ten_hp(self):
        for record in self:
            if record.hoc_phan_id:
                if record.hoc_phan_id.ma_hoc_phan_moi \
                        and record.hoc_phan_id.ten_hoc_phan:
                    record.ma_hp_ten_hp = (record.hoc_phan_id.ma_hoc_phan_moi +
                                           "-" +
                                           record.hoc_phan_id.ten_hoc_phan)
                elif record.hoc_phan_id.ma_hoc_phan:
                    record.ma_hp_ten_hp = (record.hoc_phan_id.ma_hoc_phan +
                                           "-" +
                                           record.hoc_phan_id.ten_hoc_phan)

    @api.depends("hoc_phan_id")
    def _compute_ky_ctk(self):
        for record in self:
            if record.hoc_phan_id:
                list_ctk = []
                if record.sinh_vien_id.ctk_nganh_id:
                    list_ctk.append(record.sinh_vien_id.ctk_nganh_id.id)
                if record.sinh_vien_id.ctk_chuyen_nganh_id:
                    list_ctk.append(record.sinh_vien_id.ctk_chuyen_nganh_id.id)
                mon_hoc_dieu_kien = self.env["mon_hoc_dieu_kien"].search([
                    ("ctk_id", "in", list_ctk),
                    ("hoc_phan_id", "=", record.hoc_phan_id.id),
                ])
                if len(mon_hoc_dieu_kien) > 1:
                    record.ky_ctk = "Kỳ " + str(mon_hoc_dieu_kien[-1].hoc_ky)
                elif mon_hoc_dieu_kien:
                    record.ky_ctk = "Kỳ " + str(mon_hoc_dieu_kien.hoc_ky)
            else:
                record.ky_ctk = False

    @api.depends("sinh_vien_id")
    def _compute_ma_dinh_danh_ten_sv(self):
        for record in self:
            if record.sinh_vien_id.ma_dinh_danh and record.sinh_vien_id.name:
                record.ma_dinh_danh_ten_sv = (
                    record.sinh_vien_id.ma_dinh_danh + "-" +
                    record.sinh_vien_id.name)
            else:
                record.ma_dinh_danh_ten_sv = False

    @api.depends("diem_chu")
    def _compute_diem_thang_4(self):
        for record in self:
            if record.diem_chu:
                quy_tac_diem_chu_sang_diem_4 = self.env[
                    "qldt.quy_tac_danh_gia_tinh_diem_hoc_phan"].search([
                        ("gia_tri_diem", "=", record.diem_chu)
                    ])
                if quy_tac_diem_chu_sang_diem_4.gia_tri_diem_thang_4_max:
                    record.diem_thang_4 = (
                        quy_tac_diem_chu_sang_diem_4.gia_tri_diem_thang_4_max)
                else:
                    record.diem_thang_4 = record.diem_thang_4
            else:
                record.diem_thang_4 = False

    # Hàm này có chức năng cập nhật lại trạng thái của môn học khi có điểm
    @api.depends("sv_ltc_ds_ids", "sv_ltc_ds_ids.diem_tong_ket_thang_4")
    def _compute_trang_thai(self):
        for record in self:
            for vl in record.sv_ltc_ds_ids:
                if record.diem_thang_4 < float(vl.diem_tong_ket_thang_4):
                    record.diem_thang_4 = float(vl.diem_tong_ket_thang_4)
                    record.diem_chu = vl.diem_tong_ket_dang_chu
                    record.diem_hoc_phan = float(vl.diem_tong_ket)
                    print("??????????????????")
                    if record.diem_chu is False:
                        record.trang_thai = "Chưa có điểm"
                    elif not vl.da_qua:
                        record.trang_thai = "Không đạt"
                    else:
                        record.trang_thai = "Đạt"

    @api.depends("diem_thang_4")
    def _compute_sv_diem_tong_ket(self):
        for record in self:
            print(record)
            sinh_vien_diem_tong_ket = self.env["sinh_vien_diem_tong_ket"].search(
                [
                    ("sinh_vien_id", "=", record.sinh_vien_id.id),
                ]
            )
            if sinh_vien_diem_tong_ket:
                for vl in sinh_vien_diem_tong_ket:
                    record.sinh_vien_diem_tong_ket_id = vl
            else:
                if record.sinh_vien_id:
                    sinh_vien_diem_tong_ket = self.env["sinh_vien_diem_tong_ket"].create(
                        {
                            "sinh_vien_id": record.sinh_vien_id.id,
                        }
                    )
                    record.sinh_vien_diem_tong_ket_id = sinh_vien_diem_tong_ket.id