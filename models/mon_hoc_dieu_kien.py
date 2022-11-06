# -*- coding: utf-8 -*-
from odoo import fields, models, _
from .constants_of_selection_fields import hoc_ky_selection


class MonHocDieuKien(models.Model):
    _name = "mon_hoc_dieu_kien"
    _description = "Mô tả các môn học điều kiện"
    _rec_name = "hoc_phan_id"

    ctk_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        ondelete="cascade",
        string="Thuộc chương trình khung",
    )
    hoc_phan_id = fields.Many2one(
        comodel_name="slide.channel", ondelete="cascade", string="Học phần"
    )
    ten_hoc_phan = fields.Char(
        "Tên học phần", related="hoc_phan_id.ten_hoc_phan", store=True,
    )
    so_tin_chi = fields.Integer("Số tín chỉ", related="hoc_phan_id.so_tin_chi")
    hoc_ky = fields.Selection(
        selection=hoc_ky_selection,
        string="Học kỳ",
    )
    tinh_chat = fields.Selection(
        [
            ("1", "Bắt buộc chung"),
            ("2", "Bắt buộc chung nhóm ngành"),
            ("3", "Bổ trợ ngành"),
            ("4", "Cơ sở ngành"),
            ("5", "Chuyên ngành"),
            ("6", "Thực tập"),
            ("7", "Giáo dục chuyên nghiệp"),
            ("8", "Luận văn tốt nghiệp"),
        ],
        string="Tính chất",
    )
    hoc_phan_tien_quyet_ids = fields.Many2many(
        comodel_name="slide.channel",
        relation="mon_hoc_tien_quyet",
        column1="mon_hoc_dieu_kien_id",
        string="Học phần tiên quyết",
    )
    hoc_phan_truoc_ids = fields.Many2many(
        comodel_name="slide.channel",
        relation="mon_hoc_truoc",
        column1="mon_hoc_dieu_kien_id",
        string="Học phần trước",
    )
    hoc_phan_song_hanh_ids = fields.Many2many(
        comodel_name="slide.channel",
        relation="mon_hoc_song_hanh",
        column1="mon_hoc_dieu_kien_id",
        string="Học phần song hành",
    )
    is_tinh_diem = fields.Boolean("Học phần có tính điểm?")
    loai_hoc_phan = fields.Selection(
        [("tu_chon", "Tự chọn"), ("bat_buoc", "Bắt buộc")], string="Loại học phần"
    )
    hoc_phan_tuong_duong_id = fields.One2many(
        comodel_name="qldt.hoc_phan_tuong_duong",
        inverse_name="mon_hoc_dieu_kien_id",
        string="Học phần tương đương",
    )
    sinh_vien_tham_gia = fields.Many2many(
        comodel_name="sinh_vien",
        # column1='danh_sach_mon_hoc'
        # ondelete='set null'
    )
    duoc_phep_hoc_vuot = fields.Boolean(
        string="Được phép học vượt",
        default=True
    )

    # hoc_phan_tuong_duong_id = fields.Many2one(
    #     comodel_name='qldt.hoc_phan_tuong_duong',
    #     inverse_name = 'hoc_phan_id',
    #     string='Học phần tương đương'
    # )
