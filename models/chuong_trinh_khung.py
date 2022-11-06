from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ChuongTrinhKhung(models.Model):
    _name = "chuong_trinh_khung"
    _description = "Chương trình khung"
    _rec_name = "ten_chuong_trinh_khung"

    ten_chuong_trinh_khung = fields.Char("Tên chương trình khung")

    nganh_id = fields.Many2one(
        comodel_name='quan_ly_nganh_hoc.nganh',
        ondelete='cascade',
        string='Ngành học',
        required=True,
    )
    nam_bat_dau = fields.Many2one("nam_hoc", "Năm học bắt đầu")
    chuyen_nganh_id = fields.Many2one(
        comodel_name='quan_ly_nganh_hoc.chuyen_nganh',
        ondelete='cascade',
        string='Chuyên ngành học')
    khoa_sinh_vien_ids = fields.Many2many(
        comodel_name="khoa_sinh_vien",
        string="Danh sách khoá sinh viên",
    )
    khoa_nganh_ids = fields.One2many(
        comodel_name="khoa_nganh",
        inverse_name="ctk_id",
        string="Khóa-ngành áp dụng",
    )
    hoc_ky_chuong_trinh_khung_ids = fields.One2many(
        comodel_name="hoc_ky_chuong_trinh_khung",
        inverse_name="ctk_id",
        string="Danh sách học kỳ-chương trình khung")
    # khoa_chuyen_nganh_ids = fields.One2many(
    #     comodel_name="khoa_chuyen_nganh",
    #     inverse_name="ctk_id",
    #     string="Khóa-chuyên ngành áp dụng",
    # )
    is_nganh = fields.Boolean("Là chương trình khung ngành?")
    mon_hoc_dieu_kien_ids = fields.One2many(
        comodel_name="mon_hoc_dieu_kien",
        inverse_name="ctk_id",
        string="Danh sách môn học",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        ondelete='set null',  # onproduction sẽ chuyển thành cascade
        string="Hình thức đào tạo")

    # hinh_thuc_dao_tao_ids = fields.Many2many(
    #     comodel_name="hinh_thuc_dao_tao",
    #     string="Danh sách hình thức đào tạo",
    # )

    @api.constrains("chuyen_nganh_id")
    def _constraint_chuyen_nganh_id(self):
        for record in self:
            if record.chuyen_nganh_id and record.chuyen_nganh_id \
                    not in record.nganh_id.chuyen_nganh_ids:
                raise ValidationError("Chuyên ngành không thuộc ngành!")
