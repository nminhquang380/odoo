from odoo import fields, models, api


class KyHoc(models.Model):
    _name = "ky_hoc"
    _description = "Kỳ chương trình khung"

    _rec_name = "ten_ky_hoc"

    ten_ky_hoc = fields.Char("Tên kỳ chương trình khung", size=500)
    # tg_bat_dau = fields.Datetime('Thời gian bắt đầu')
    # tg_ket_thuc = fields.Datetime('Thời gian kết thúc')
    # nganh = fields.Many2one(
    #     comodel_name='quan_ly_nganh_hoc.nganh',
    #     ondelete='cascade',
    #     string='Ngành')
    # chuyen_nganh = fields.Many2one(
    #     comodel_name='quan_ly_nganh_hoc.chuyen_nganh',
    #     ondelete='cascade',
    #     string='Chuyên ngành')
    # khoa_sinh_vien = fields.Many2one(
    #     comodel_name='khoa_sinh_vien',
    #     ondelete='cascade',
    #     string='Khóa sinh viên')
    danh_sach_mon_hoc = fields.Many2many(
        comodel_name="mon_hoc_dieu_kien", string="Danh sách môn học"
    )
    ctk_ids = fields.Many2many(
        "chuong_trinh_khung", string="Chương trình khung", readonly=True
    )
