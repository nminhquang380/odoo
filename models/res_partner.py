# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date

class ResPartner(models.Model):
    _inherit = "res.partner"

    slide_channel_ids = fields.Many2many(
        "slide.channel",
        "slide_channel_partner",
        "partner_id",
        "channel_id",
        string="eLearning Courses",
    )
    subjects = fields.One2many(
        "slide.channel.partner",
        "partner_id",
        string="Danh sách môn học",
        domain=[("completion", "!=", -1)],
    )
    slide_channel_count = fields.Integer(
        "Course Count", compute="_compute_slide_channel_count")
    slide_channel_company_count = fields.Integer(
        "Company Course Count", compute="_compute_slide_channel_company_count")
    user_id = fields.Many2one("res.users", ondelete="cascade")

    sinh_vien_id = fields.Many2one("sinh_vien", ondelete="cascade")
    nhan_vien_id = fields.Many2one("nhan_vien", ondelete="cascade")
    don_vi_id = fields.Many2one("danh_muc.don_vi", string="Đơn vị")

    quan_tri_id = fields.Many2one("quan_tri", ondelete="cascade")
    tro_giang_id = fields.Many2one("tro_giang", ondelete="cascade")
    quan_tri_bd_id = fields.Many2one("qldt.quan_tri_vien_bd",
                                     ondelete="cascade")
    ke_toan_id = fields.Many2one("ke_toan", ondelete="cascade")

    can_bo_qlkh_id = fields.Many2one("can_bo_qlkh", ondelete="cascade")
    lanh_dao_id = fields.Many2one("lanh_dao", ondelete="cascade")
    # thông tin cơ bản chung
    dia_chi_hien_nay = fields.Char("Địa chỉ hiện nay")
    ma_dinh_danh = fields.Char("Mã định danh", required=True)

    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique (ma_dinh_danh)',
        'Mã định danh phải là duy nhất!')
    ]

    # THONG TIN CA NHAN
    ho_dem = fields.Char("Họ đệm", size=255)
    ten = fields.Char("Tên trước", size=255)
    name = fields.Char("Họ và tên")
    ten_goi_khac = fields.Char("Tên gọi khác", size=255)
    ngay_sinh = fields.Date("Ngày sinh")
    gioi_tinh = fields.Selection([("0", "Nam"), ("1", "Nữ"), ("2", "Khác")],
                                 string="Giới tính")
    avatar_path = fields.Char("Duong dan avatar online")

    # thông tin hiển thị rec_name
    ma_dinh_danh_ten = fields.Char(compute="_compute_ma_dinh_danh_ten",
                                   store=True,
                                   string="Mã định danh - tên")

    # Nơi sinh
    loaiNoiSinh = fields.Selection([
        ("0", "Trong nước"),
        ("1", "Nước ngoài")
    ],string="Loại nơi sinh",
    default="0")
    noiSinhNuocNgoai = fields.Char("Nơi sinh nước ngoài")
    tinh_tp_id = fields.Many2one("co_so_hanh_chinh",
                                string="Tỉnh, thành phố",
                                domain="[('cap_don_vi', '=', 1)]")
    tinh_tp_ns = fields.Char("Tỉnh/thành phố",
                             related="tinh_tp_id.ten_don_vi")
    quan_huyen_id = fields.Many2one("co_so_hanh_chinh",
                                string="Quận, huyện",
                                domain="[('cap_don_vi', '=', 2)]")
    quan_huyen_ns = fields.Char("Quận/huyện", 
                                related="quan_huyen_id.ten_don_vi",
                                )
    phuong_xa_id = fields.Many2one("co_so_hanh_chinh",
                                string="Phường, xã",
                                domain="[('cap_don_vi', '=', 3)]")
    phuong_xa_ns = fields.Char("Phường/xã",
                                related="phuong_xa_id.ten_don_vi",
                                )
    so_nha_ten_duong_ns = fields.Char("Số nhà/tên đường", size=255)

    # Quê quán trên sổ hộ khẩu
    tinh_tp_hk = fields.Char("Tỉnh/thành phố", size=255)
    quan_huyen_hk = fields.Char("Quận/huyện", size=255)
    phuong_xa_hk = fields.Char("Phường/xã", size=255)
    so_nha_ten_duong_hk = fields.Char("Số nhà/tên đường", size=255)

    dan_toc = fields.Char("Dân tộc", size=255)
    ton_giao = fields.Char("Tôn giáo", size=255)

    # Nơi ở hiện nay
    tinh_tp_no = fields.Char("Tỉnh/thành phố", size=255)
    quan_huyen_no = fields.Char("Quận/huyện", size=255)
    phuong_xa_no = fields.Char("Phường/xã", size=255)
    so_nha_ten_duong_no = fields.Char("Số nhà/tên đường", size=255)
    dia_chi_hien_nay = fields.Char("Địa chỉ hiện nay", size=255)

    so_dien_thoai = fields.Char("Số điện thoại")
    so_dien_thoai_thay_the = fields.Char("Số điện thoại thay thế")
    so_cmnd = fields.Char("Chứng minh nhân dân/căn cước công dân", size=12)
    noi_cap = fields.Char("Nơi cấp")
    ngay_cap = fields.Date("Ngày cấp")
    so_so_bhxh = fields.Char("Số sổ BHXH", size=50)

    # QUA TRINH CONG TAC
    ngay_bat_dau = fields.Date("Ngày bắt đầu")
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
    email_to_chuc = fields.Char("Email tổ chức")


    @api.constrains("ngay_bat_dau", "ngay_ket_thuc")
    def constraint_qua_trinh_cong_tac(self):
        for record in self:
            if record.ngay_bat_dau and record.ngay_bat_dau > date.today():
                raise ValidationError("Ngày bắt đầu không hợp lệ!")
            if record.ngay_ket_thuc and record.ngay_ket_thuc > date.today():
                raise ValidationError("Ngày kết thúc không hơp lệ!")
            if record.ngay_bat_dau and record.ngay_ket_thuc:
                if record.ngay_bat_dau > record.ngay_ket_thuc:
                    raise ValidationError("Ngày bắt đầu không được sau ngày kết thúc!")
           
    @api.depends("name", "ma_dinh_danh")
    def _compute_ma_dinh_danh_ten(self):
        for record in self:
            if record.name and record.ma_dinh_danh:
                record.ma_dinh_danh_ten = record.ma_dinh_danh + '-' + record.name

    @api.depends("is_company")
    def _compute_slide_channel_count(self):
        read_group_res = (self.env["slide.channel.partner"].sudo().read_group(
            [("partner_id", "in", self.ids)], ["partner_id"], "partner_id"))
        data = dict((res["partner_id"][0], res["partner_id_count"])
                    for res in read_group_res)
        for partner in self:
            partner.slide_channel_count = data.get(partner.id, 0)

    @api.depends("is_company", "child_ids.slide_channel_count")
    def _compute_slide_channel_company_count(self):
        for partner in self:
            if partner.is_company:
                partner.slide_channel_company_count = (
                    self.env["slide.channel"].sudo().search_count([
                        ("partner_ids", "in", partner.child_ids.ids)
                    ]))
            else:
                partner.slide_channel_company_count = 0

    def action_view_courses(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.slide_channel_action_overview")
        action["name"] = _("Followed Courses")
        action["domain"] = [
            "|",
            ("partner_ids", "in", self.ids),
            ("partner_ids", "in", self.child_ids.ids),
        ]
        return action
