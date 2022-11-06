from odoo import models, fields, api


class KeToan(models.Model):
    _name = "ke_toan"
    _description = "Kế toán"
    _inherit = ["tac_nhan"]
    _rec_name = "ma_dinh_danh"

    user_group_string = "website_slides.group_website_slides_ke_toan"
    vai_tro_string = "ke_toan"
    # vai_tro = ('3','giang_vien')
    # lop_tin_chi_ids = fields.One2many("lop_tin_chi", "giang_vien_id")
    # lop_hanh_chinh_ids = fields.One2many(
    #     comodel_name="lop_hanh_chinh", inverse_name="giang_vien_id"
    # )
    hinh_thuc_dao_tao_id = fields.Many2one("hinh_thuc_dao_tao",
                                            string="Hình thức đào tạo",
                                            required=True)
    ham_hoc_vi = fields.Selection([("ThS", "Thạc sĩ"),
                                   ("GVC", "Giảng viên chính"),
                                   ("TS", "Tiến sĩ"),
                                   ("PGS.TS", "Phó giáo sư tiến sĩ"),
                                   ("GS", "Giáo sư")])
    ten_id_kt = fields.Char("ID kế toán",
                            compute="_compute_ke_toan_id",
                            store=True)
    ma_gv = fields.Char("Mã kế toán")
    # chuc_vu = fields.Char("Chức vụ")

    @api.model
    def create(self, values):
        res = super(KeToan, self).create(values)
        res.partner_id.ke_toan_id = res.id
        return res

    def _create_user(self):
        user_group = self.env.ref(self.user_group_string) or False
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                if record.ngay_sinh:
                    password = record.ngay_sinh.strftime("%d%m%Y")
                else:
                    password = "ptitdu"
                user_id = users_res.create({
                    'name':
                    record.name,
                    'partner_id':
                    record.partner_id.id,
                    'login':
                    str(record.ma_dinh_danh).upper(),
                    'password':
                    password,
                    'groups_id':
                    user_group,
                    'ke_toan_id':
                    record.id,
                    'tz':
                    self._context.get('tz'),
                    'vai_tro':
                    self.vai_tro_string,
                })
                record.user_id = user_id

    @api.depends("name", "ham_hoc_vi")
    def _compute_ke_toan_id(self):
        for record in self:
            if record.name and record.ham_hoc_vi:
                record.ten_id_kt = record.ham_hoc_vi + '.' + record.name
            else:
                record.ten_id_kt = record.ten_id_kt
