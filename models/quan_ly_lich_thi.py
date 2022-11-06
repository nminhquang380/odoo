from odoo import fields, models


class CaThi(models.Model):
    _name = "ca_thi"
    _description = "Ca thi"

    nhom_thi = fields.Char("Nhóm thi")
    to_thi = fields.Char("Tổ thi")
    hoc_phan_id = fields.Many2one(
        comodel_name="slide.channel",
        string="Học phần",
    )
    ten_hoc_phan = fields.Char(
        related="hoc_phan_id.ten_hoc_phan",
        # store=True,
        string="Tên học phần"
    )
    ngay_thi = fields.Date("Ngày thi")
    tiet_bd = fields.Integer("Tiết bắt đầu")
    so_tiet = fields.Integer("Số tiết")
    phong_thi = fields.Char("Phòng thi")
    gio_bd = fields.Char("Giờ bắt đầu")
    so_phut = fields.Integer("Số phút")
    dot_thi_id = fields.Many2one(
        comodel_name="dot_thi",
        string="Đợt thi",
    )
    sinh_vien_ids = fields.Many2many(
        comodel_name="sinh_vien",
        string="Danh sách sinh viên",
    )
    hinh_thuc = fields.Char(
        string="Hình thức"
    )
    can_bo_coi_thi = fields.Char(
        string="Cán bộ coi thi"
    )
    ghi_chu = fields.Char(
        string="Ghi chú"
    )

    # _sql_constraints = [
    #     (
    #         "unique_nhom_thi_to_thi",
    #         "UNIQUE(nhom_thi, to_thi)",
    #         "Đã có cặp nhóm thi - tổ thi này",
    #     )
    # ]


class DotThi(models.Model):
    _name = "dot_thi"
    _description = "Đợt thi"
    _rec_name = "ten_dot_thi"

    ten_dot_thi = fields.Char("Tên đợt thi", required=True)
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        string="Kỳ năm học",
        required=True
    )
    ca_thi_ids = fields.One2many(
        comodel_name="ca_thi",
        inverse_name="dot_thi_id",
        string="Danh sách ca thi"
    )
