from odoo import fields, models, api
from .constants_of_selection_fields import vai_tro_don_vi_selection, hoc_ham_hoc_vi
from .constants_user_groups import portal_user
import re


class NhanVien(models.Model):
    _name = "nhan_vien"
    _description = "Nhân viên"
    _inherit = ["tac_nhan"]
    _rec_name = "ma_dinh_danh"

    vai_tro_string = "nhan_vien"
    user_group_string = portal_user

    # lop_tin_chi_ids = fields.One2many(comodel_name="lop_tin_chi",
    #                                   inverse_name="giang_vien_id",
    #                                   string="Danh sách lớp tín chỉ")
    # lop_tin_chi_phu_ids = fields.One2many(comodel_name="lop_tin_chi",
    #                                       inverse_name="giang_vien_phu_id",
    #                                       string="Lớp tín chỉ trợ giảng")
    lop_tin_chi_ids = fields.Many2many(comodel_name="lop_tin_chi",
                                       string="Danh sách lớp tín chỉ")
    ma_dinh_danh_ten_nv = fields.Char(compute="_compute_ma_dinh_danh_ten_nv",
                                      store=True,
                                      string="Mã định danh - tên nhân viên")
    vai_tro_goc = fields.Selection(selection=vai_tro_don_vi_selection,
                                   string='Vai trò gốc')
    vai_tro_kiem_nhiem = fields.One2many(comodel_name='vai_tro_kiem_nhiem',
                                         inverse_name='nhan_vien_id',
                                         string='Vai trò kiêm nhiệm')
    hoc_ham_hoc_vi = fields.Selection(selection=hoc_ham_hoc_vi,
                                      string='Học hàm - học vị')
    lop_hanh_chinh_ids = fields.One2many(comodel_name="lop_hanh_chinh",
                                         inverse_name="can_bo_id",
                                         string="Lớp hành chính phụ trách")
    chuc_danh = fields.Char("Chức danh")
    loaiNoiSinh = fields.Selection([
        ("0", "Trong nước"),
        ("1", "Nước ngoài")
        ], string="Loại nơi sinh")
    noiSinhNuocNgoai = fields.Char("Nơi sinh nước ngoài")

    @api.model
    def create(self, values):
        res = super(NhanVien, self).create(values)
        res.partner_id.nhan_vien_id = res.id
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
                login = str(record.ma_dinh_danh)
                match = re.match(
                    "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                    login,
                )
                if match is None:
                    login = login.upper()
                user_id = users_res.create({
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'login': login,
                    'password': password,
                    'groups_id': user_group,
                    'tz': self._context.get('tz'),
                    'vai_tro': self.vai_tro_string,
                })
                record.user_id = user_id
