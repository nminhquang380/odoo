from odoo import fields, models, api


class TongHopSoLieuNhuCau(models.Model):

    _name = "tong_hop_so_lieu_nhu_cau"
    _description = "Tổng hợp số liệu nhu cầu"

    dot_dang_ky_nhu_cau_id = fields.Many2one(
        "dot_dang_ky_nhu_cau",
        "Đợt đăng ký nhu cầu"
    )
    hoc_phan_id = fields.Many2one(
        "slide.channel",
        "Học phần"
    )
    ma_hoc_phan = fields.Char(
        "Mã học phần",
        related="hoc_phan_id.ma_hoc_phan_moi"
    )
    khoa_id = fields.Many2one(
        "danh_muc.khoa",
        string="Khoa phụ trách",
        related="hoc_phan_id.khoa_id",
    )
    hoc_phi = fields.Integer(
        "Học phí dự kiến",
        compute="_compute_hoc_phi_du_kien",
    )
    tong_so_dk = fields.Integer(
        "Tổng số sinh viên đăng ký",
        compute="_compute_tong_so_dk",
    )
    tong_so_sinh_vien_duoc_phep_hoc = fields.Integer(
        compute="_compute_tong_so_sinh_vien_duoc_phep_hoc"
    )
    nv_hoc_phan_ids = fields.One2many(
        "nv_hoc_phan",
        "tong_hop_so_lieu_id",
        "Danh sách nguyện vọng học phần"
    )

    @api.depends("nv_hoc_phan_ids")
    def _compute_tong_so_dk(self):
        for record in self:
            record.tong_so_dk = len(record.nv_hoc_phan_ids)

    @api.depends("nv_hoc_phan_ids.hoc_phi")
    def _compute_hoc_phi_du_kien(self):
        for record in self:
            if record.nv_hoc_phan_ids:
                record.hoc_phi = sum(
                    hehe.hoc_phi for hehe in record.nv_hoc_phan_ids)
            else:
                record.hoc_phi = 0
