import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

_logger = logging.getLogger(__name__)


class DotDangKyTinChi(models.Model):
    _name = "dot_dang_ky_tin_chi"
    _description = "Đợt đăng ký tín chỉ"
    _rec_name = "ten_dot_dang_ky_tin_chi"

    ten_dot_dang_ky_tin_chi = fields.Char(
        "Tên đợt đăng ký tín chỉ",
        compute="_compute_ten_dot_dang_ky_tin_chi",
        store=True)
    so_thu_tu_dot = fields.Integer(
        "Số thứ tự đợt",
        required=True,
    )
    ky_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        ondelete="cascade",
        string="Kỳ năm học",
        required=True,
    )
    dot_dang_ky_hoc_phan_id = fields.Many2one(
        comodel_name="dot_dang_ky_nhu_cau",
        compute="_compute_dot_dang_ky_nhu_cau",
        string="Đợt đăng ký nhu cầu",
        store=True,
        readonly=False)
    khoi_lop_ids = fields.Many2many("khoi_lop",
                                    "dot_dk_tc_khoi_lop",
                                    string="Danh sách khối lớp",
                                    domain="[('dot_dang_ky_nhu_cau_ids', 'in', dot_dang_ky_hoc_phan_id)]")
    ma_ky_hoc = fields.Char("Mã kỳ năm học",
                            related="ky_hoc_id.ma_ky_nam_hoc",
                            store=True)
    is_nhu_cau = fields.Boolean("Có đợt đăng ký nhu cầu?")
    is_tin_chi = fields.Boolean("Có đợt đăng ký tín chỉ?")
    is_hoc_ghep = fields.Boolean("Có đợt đăng ký học ghép?")
    ngay_bat_dau_tin_chi = fields.Datetime("Ngày bắt đầu đăng ký tín chỉ", required=True)
    ngay_ket_thuc_tin_chi = fields.Datetime("Ngày kết thúc đăng ký tín chỉ", required=True)
    trang_thai = fields.Char("Trạng thái",
                            compute="_compute_trang_thai")
    lop_tin_chi_ids = fields.One2many("lop_tin_chi",
                                      "dot_dk_tin_chi_id",
                                      string="Danh sách lớp tín chỉ")
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        string="Hình thức đào tạo",
        related="ky_hoc_id.hinh_thuc_dao_tao_id")
    so_tin_chi_toi_thieu = fields.Integer(
        string="Số tín chỉ tối thiểu",
        related="dot_dang_ky_hoc_phan_id.so_tin_chi_toi_thieu",
        default=14)
    so_tin_chi_toi_da = fields.Integer(
        string="Số tín chỉ tối đa",
        related="dot_dang_ky_hoc_phan_id.so_tin_chi_toi_da",
        default=21)
    so_phan_tram_cho_phep_trung_lich_hoc = fields.Float(
        string="Tỉ lệ lịch học trùng tối đa (%)", default=20.0)
    phieu_dang_ky_tin_chi = fields.One2many(
        "phieu_dang_ky_tin_chi",
        "dot_dang_ky_tin_chi_id",
        string="Danh sách phiếu đăng ký tín chỉ",
    )
    ap_dung_thanh_toan_truc_tuyen = fields.Boolean(
        string="Áp dụng thanh toán trực tuyến", default=True)
    state = fields.Selection(selection=[
        ('-1', 'Chưa diễn ra'),
        ('0', 'Đang diễn ra'),
        ('1', 'Đã kết thúc'),
    ],
                             string="Trạng thái đợt đăng ký",
                             compute="dong_bo_status",
                             store=True)
    status = fields.Selection(selection=[
        ('-1', 'Chưa diễn ra'),
        ('0', 'Đang diễn ra'),
        ('1', 'Đã kết thúc'),
    ],
                              required=True,
                              string="Trạng thái đợt đăng ký",
                              default='0')

    @api.depends("status")
    def dong_bo_status(self):
        for record in self:
            record.state = record.status

    @api.depends("ky_hoc_id", "so_thu_tu_dot")
    def _compute_ten_dot_dang_ky_tin_chi(self):
        for record in self:
            if record.ky_hoc_id and record.so_thu_tu_dot:
                record.ten_dot_dang_ky_tin_chi = (
                    record.ky_hoc_id.ma_ky_nam_hoc + " - " +
                    str(record.so_thu_tu_dot))
                if record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat != "CQ":
                    record.ten_dot_dang_ky_tin_chi += (
                        " - " + record.hinh_thuc_dao_tao_id.
                        ten_hinh_thuc_dao_tao_viet_tat)
            else:
                record.ten_dot_dang_ky_tin_chi = record.ten_dot_dang_ky_tin_chi

    @api.depends("ky_hoc_id")
    def _compute_dot_dang_ky_nhu_cau(self):
        for record in self:
            if record.ky_hoc_id:
                record.dot_dang_ky_hoc_phan_id = self.env[
                    "dot_dang_ky_nhu_cau"].search(
                        [("ky_hoc_id", "=", record.ky_hoc_id.id)], limit=1)
            else:
                record.dot_dang_ky_hoc_phan_id = record.dot_dang_ky_hoc_phan_id
    
    @api.onchange("ngay_bat_dau_tin_chi", "ngay_ket_thuc_tin_chi")
    def _compute_trang_thai(self):
        for record in self:
            if record.ngay_bat_dau_tin_chi and record.ngay_ket_thuc_tin_chi:
                today = datetime.now()
                if today < record.ngay_bat_dau_tin_chi:
                    record.trang_thai = "Chưa bắt đầu"
                elif today >= record.ngay_bat_dau_tin_chi and today <= record.ngay_ket_thuc_tin_chi:
                    record.trang_thai = "Đang diễn ra"
                elif today > record.ngay_ket_thuc_tin_chi:
                    record.trang_thai = "Đã kết thúc"
            else:
                record.trang_thai = "Chưa xác định"

    @api.constrains("ngay_bat_dau_tin_chi", "ngay_ket_thuc_tin_chi")
    def validate_thoi_gian(self):
        if self.ngay_bat_dau_tin_chi and self.ngay_ket_thuc_tin_chi:
            if self.ngay_bat_dau_tin_chi > self.ngay_ket_thuc_tin_chi:
                raise ValidationError(
                    "Thời gian kết thúc đợt đăng ký tín chỉ không được sớm hơn thời gian bắt đầu!"
                )
    

    def action_view_thong_ke_dang_ky_tin_chi(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.action_phieu_dang_ky_tin_chi")
        action["context"] = {
            "default_dot_dang_ky_tin_chi_id": self.id,
        }
        action["domain"] = [("dot_dang_ky_tin_chi_id", "=", self.id)]
        return action

    def action_phe_duyet_tat_ca_phieu_dang_ky_tin_chi(self):
        for record in self:
            phieu_dang_ky_tin_chi = self.env["phieu_dang_ky_tin_chi"].search([
                ("dot_dang_ky_tin_chi_id", "=", record.id)
            ])
            for vl in phieu_dang_ky_tin_chi:
                if not vl.trang_thai_sinh_ma_thanh_toan:
                    vl.trang_thai_sinh_ma_thanh_toan = True

    def action_hoa_don_phieu_dang_ky_tin_chi_import_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.action_hoa_don_phieu_dang_ky_tin_chi_import_wizard"
        )
        action["domain"] = [("dot_dang_ky_tin_chi_id", "=", self.id)]
        return action
