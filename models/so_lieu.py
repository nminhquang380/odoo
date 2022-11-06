from odoo import models, fields, api


class SoLieu(models.Model):
    _name = 'so_lieu'
    _description = 'Số liệu'
    _rec_name = 'ten_so_lieu'

    ten_so_lieu = fields.Char(string="Tên số liệu",)
    # nhóm số liệu về tài khoản
    tong_so_sinh_vien = fields.Integer(
        string="Tổng số sinh viên",
        compute="_compute_tong_so_sinh_vien",
        # default=0
    )
    tong_so_giang_vien = fields.Integer(
        string="Tổng số giảng viên", compute="_compute_tong_so_giang_vien"
    )
    tong_so_quan_tri_vien = fields.Integer(string="Tổng số quản trị viên", default=0)
    tong_so_tai_khoan_khach = fields.Integer(
        string="Tổng số tài khoản khách", default=0
    )
    hien_thi_so_lieu_tai_khoan = fields.Boolean(
        default=False, string="Hiển thị số liệu tài khoản?"
    )

    # nhóm số liệu về quản lý đào tạo
    tong_so_nganh_hoc = fields.Integer(
        string="Tổng số ngành học", compute="_compute_tong_so_nganh_hoc"
    )
    tong_so_chuyen_nganh = fields.Integer(string="Tổng số chuyên ngành", default=0)
    tong_so_hoc_lieu = fields.Integer(string="Tổng số học liệu", default=0)
    tong_so_hoc_phan = fields.Integer(
        string="Tổng số học phần", compute="_compute_tong_so_hoc_phan"
    )
    nam_hoc_hien_tai = fields.Many2one(
        comodel_name="nam_hoc", ondelete="set null", string="Năm học hiện tại"
    )
    hien_thi_so_lieu_dao_tao = fields.Boolean(
        default=False, string="Hiển thị số liệu đào tạo?"
    )

    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name='hinh_thuc_dao_tao',
        ondelete='set null',
        string='Hình thức đào tạo'
    )

    color = fields.Integer(string="Mã màu", default=9, help="Làm tí màu mè gay lọ :3")

    # @api.depends('hien_thi_so_lieu_tai_khoan')
    @api.onchange('hien_thi_so_lieu_tai_khoan')
    def _compute_tong_so_sinh_vien(self):
        tong_sv = len(self.env["sinh_vien"].search([]))
        if tong_sv != 0:
            self.tong_so_sinh_vien = tong_sv
        else:
            self.tong_so_sinh_vien = 0

    @api.onchange('hien_thi_so_lieu_tai_khoan')
    def _compute_tong_so_giang_vien(self):
        tong_gv = len(self.env["giang_vien"].search([]))
        if tong_gv != 0:
            self.tong_so_giang_vien = tong_gv
        else:
            self.tong_so_giang_vien = 0

    @api.onchange('hien_thi_so_lieu_dao_tao')
    def _compute_tong_so_nganh_hoc(self):
        tong_nganh_hoc = len(self.env["quan_ly_nganh_hoc.nganh"].search([]))
        if tong_nganh_hoc != 0:
            self.tong_so_nganh_hoc = tong_nganh_hoc
        else:
            self.tong_so_nganh_hoc = 0

    @api.onchange('hien_thi_so_lieu_dao_tao')
    def _compute_tong_so_hoc_phan(self):
        tong_hoc_phan = len(self.env["slide.channel"].search([]))
        if tong_hoc_phan != 0:
            self.tong_so_hoc_phan = tong_hoc_phan
        else:
            self.tong_so_hoc_phan = 0
