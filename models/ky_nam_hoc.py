from email.policy import default
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from .constants_of_selection_fields import trang_thai_ky_nam_hoc
import uuid


class KyNamHoc(models.Model):

    _name = "ky_nam_hoc"
    _description = "Kỳ học"
    # đổi rec_name -> đổi tên trường hiển thị trên list/form view
    _rec_name = "ma_ky_nam_hoc"

    _uuid = fields.Char(string="UUID")
    ten_ky_nam_hoc = fields.Char("Thứ tự kỳ trong năm học", size=20)
    thoi_gian_bat_dau = fields.Date(string="Thời gian bắt đầu")
    thoi_gian_ket_thuc = fields.Date(string="Thời gian kết thúc")
    nam_hoc_id = fields.Many2one(comodel_name="nam_hoc",
                                 ondelete="cascade",
                                 string="Năm học")
    ma_ky_nam_hoc = fields.Char(
        string="Mã kỳ năm học",
        compute="_compute_ma_ky_nam_hoc",
        search="_seach_ma_ky_nam_hoc",
        store=True,
        compute_sudo=True,  # xem xet co nen bo thuoc tinh nay di khong ?
    )
    # hinh_thuc_dao_tao_user = fields.Many2one('res.users',
    #                                 'Người dùng hiện tại',
    #                                 default= lambda self: self.env.user.hinh_thuc_dao_tao_id)
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                           string="Hình thức đào tạo",
                                           default= lambda self: self.env.user.hinh_thuc_dao_tao_id)
    khoi_lop_ids = fields.Many2many("khoi_lop",
                                    "ky_nam_hoc_khoi_lop",
                                    string="Danh sách khối lớp")
    is_ky_chinh = fields.Boolean("Kỳ chính?", default=True)
    dot_dang_ky_tin_chi_ids = fields.One2many(
        "dot_dang_ky_tin_chi",
        "ky_hoc_id",
        name="Danh sách đợt đăng ký tín chỉ")
    trang_thai = fields.Selection(selection=trang_thai_ky_nam_hoc,
                                  string="Trạng thái")

    _sql_constraints = [('unique_ky_nam_hoc_hinh_thuc_dao_tao',
                         'unique(ma_ky_nam_hoc, hinh_thuc_dao_tao_id)',
                         "Kỳ học đã tồn tại trong hình thức đào tạo này")]

    @api.depends("ten_ky_nam_hoc", "nam_hoc_id.nam_hoc",
                 "hinh_thuc_dao_tao_id")
    def _compute_ma_ky_nam_hoc(self):
        for record in self:
            if record.nam_hoc_id.nam_hoc and record.ten_ky_nam_hoc and record.hinh_thuc_dao_tao_id:
                record.ma_ky_nam_hoc = (str(record.nam_hoc_id.nam_hoc) +
                                        record.ten_ky_nam_hoc)
                if record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat != "CQ":
                    record.ma_ky_nam_hoc += ("-" + record.hinh_thuc_dao_tao_id.
                                             ten_hinh_thuc_dao_tao_viet_tat)
            else:
                record.ma_ky_nam_hoc = ""

    def _seach_ma_ky_nam_hoc(self):
        return self.ma_ky_nam_hoc

    @api.constrains("thoi_gian_bat_dau", "thoi_gian_ket_thuc")
    def validate_thoi_gian_nam_hoc(self):
        if self.thoi_gian_bat_dau and self.thoi_gian_ket_thuc:
            if self.thoi_gian_bat_dau > self.thoi_gian_ket_thuc:
                raise ValidationError(
                    "Thời gian kết thúc kỳ học không được sớm hơn thời gian bắt đầu!"
                )

    @api.model
    def create(self, values):
        _uuid = uuid.uuid4().hex
        values['_uuid'] = _uuid
        res = super(KyNamHoc, self).create(values)
        return res
