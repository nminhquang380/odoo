import json
import logging
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from zoomus.client import ZoomClient

_logger = logging.getLogger(__name__)


class BuoiHoc(models.Model):
    _name = "buoi_hoc"
    _description = "Buổi học"
    # _inherits = {"calendar.event": "calendar_event_id"}
    _rec_name = "ten_buoi_hoc"
    # dummy field
    lop_tin_chi_id = fields.Many2one("lop_tin_chi", "Lớp tín chỉ")
    khoa_id = fields.Many2one("khoa_sinh_vien",
                              "Khóa sinh viên",
                              related="lop_tin_chi_id.khoa_id",
                              store=True)
    hoc_phan_id = fields.Many2one("slide.channel",
                                  "Học phần",
                                  related="lop_tin_chi_id.mon_hoc_ids",
                                  store=True)
    nhom_lop_tin_chi_id = fields.Many2one("nhom_lop_tin_chi",
                                          "Nhóm lớp tín chỉ")
    ky_nam_hoc_id = fields.Many2one(
        "ky_nam_hoc",
        related="lop_tin_chi_id.ky_nam_hoc_id",
        store=True,
    )
    hinh_thuc_dao_tao_id = fields.Many2one(string="Hình thức đào tạo",
                                  related="ky_nam_hoc_id.hinh_thuc_dao_tao_id",
                                  store=True)
    ten_buoi_hoc = fields.Char("Tên buổi học",
                               compute="_compute_ten_buoi_hoc",
                               store=True)
    ten_hoc_phan = fields.Char("Tên môn học",
                               related="hoc_phan_id.ten_hoc_phan",
                               store=True)
    thu_kieu_so = fields.Integer("Thứ",
                                 compute="_compute_thu_kieu_so",
                                 store=True,
                                 group_operator=False)
    ngay_bd = fields.Date("Ngày")
    tuan_hoc = fields.Integer("Tuần học",
                              compute="_compute_tuan_hoc",
                              store=True)
    tiet_bd = fields.Many2one(comodel_name="danh_muc.tiet_hoc",
                              string="Tiết bắt đầu (danh mục)",
                              store=True,
                              readonly=False)
    tiet_kt = fields.Many2one(comodel_name="danh_muc.tiet_hoc",
                              string="Tiết kết thúc (danh mục)",
                              store=True,
                              readonly=False)
    tiet_bd_so = fields.Integer("Tiết bắt đầu")
    tiet_kt_so = fields.Integer("Tiết kết thúc")
    so_tiet = fields.Integer("Số tiết",
                             group_operator=False,
                             compute="_compute_so_tiet",
                             store=True)
    template_tiet_hoc_id = fields.Many2one(
        comodel_name="danh_muc.template_tiet_hoc", string="Nhóm tiết học")
    giang_vien_id = fields.Many2one("nhan_vien",
                                    "Giảng viên",
                                    related="lop_tin_chi_id.giang_vien_id",
                                    store=True,
                                    readonly=False)
    ten_giang_vien = fields.Char("Tên giảng viên",
                                 related="giang_vien_id.name",
                                 store=True)
    dien_thoai = fields.Char(related="giang_vien_id.so_dien_thoai",
                             store=True,
                             string="Số điện thoại")
    email = fields.Char(related="giang_vien_id.email_to_chuc",
                        store=True,
                        string="Email")
    tai_khoan = fields.Char("Tài khoản", size=20)
    mat_khau = fields.Char("Mật khẩu", size=20)
    phong_hoc = fields.Char("Phòng học")
    id_zoom = fields.Char("ID Zoom", size=20)
    mat_khau_1 = fields.Char("Mật khẩu Zoom", size=20)
    ngay_gio_hoc = fields.Datetime("Ngày giờ học",
                                   compute="_compute_ngay_gio_hoc",
                                   store=True,
                                   readonly=False)
    ngay_gio_ket_thuc = fields.Datetime("Ngày giờ kết thúc",
                                        compute="_compute_ngay_gio_ket_thuc",
                                        store=True,
                                        readonly=False)

    calendar_event_id = fields.Many2one(
        "calendar.event",
        ondelete="cascade",
        string="Lịch",
    )
    diem_danh_buoi_hoc_ids = fields.One2many("diem_danh_buoi_hoc",
                                             "buoi_hoc_id",
                                             "Danh sách điểm danh")
    tong_so_sinh_vien = fields.Integer("Sĩ số từng nhóm",
                                       group_operator=False,
                                       compute="_compute_tong_so_sinh_vien",
                                       store=True)
    so_luong_vang = fields.Integer("Số lượng vắng",
                                   compute="_compute_so_luong_vang",
                                   store=True)
    check_diem_danh = fields.Selection([
        ("CHUA_KHOI_TAO", "Chưa có sinh viên trong danh sách"),
        ("DANG_KHOI_TAO", "Có nhưng chưa đủ sinh viên"),
        ("DA_KHOI_TAO", "Đủ sinh viên"),
    ],
                                       string="Check điểm danh",
                                       compute="_compute_check_diem_danh",
                                       store=True)
    giang_vien_da_diem_danh = fields.Boolean("Giảng viên đã điểm danh",
                                             default=False)
    noi_dung_bai_hoc = fields.Char("Nội dung bài học")
    url_bai_hoc = fields.Char("Url bài học")

    # @api.depends("tiet_bd_so", "template_tiet_hoc_id")
    # def _compute_tiet_bd_danh_muc(self):
    #     tiet_hoc = self.env["danh_muc.tiet_hoc"].search([])
    #     map_tiet_hoc = {f"{x.tiet_hoc}|{x.template_tiet_hoc_id.id}": x.id for x in tiet_hoc}
    #     for i, record in enumerate(self):
    #         if record.template_tiet_hoc_id:
    #             print("tietBD", i)
    #             # tiet_bd = self.env["danh_muc.tiet_hoc"].search([
    #             #     ("tiet_hoc", "=", record.tiet_bd_so),
    #             #     ("template_tiet_hoc_id", "=",
    #             #      record.template_tiet_hoc_id.id)
    #             # ])
    #             tiet_bd = map_tiet_hoc.get(f"{record.tiet_bd_so}|{record.template_tiet_hoc_id.id}")
    #             if tiet_bd == None:
    #                 raise ValidationError(f"Tiết bắt đầu phải nằm trong {record.template_tiet_hoc_id.tiethoc_id.mapped('tiet_hoc')}")
    #             record.tiet_bd = tiet_bd
    #         else:
    #             record.tiet_bd = False

    # @api.depends("tiet_kt_so", "template_tiet_hoc_id")
    # def _compute_tiet_kt_danh_muc(self):
    #     tiet_hoc = self.env["danh_muc.tiet_hoc"].search([])
    #     map_tiet_hoc = {f"{x.tiet_hoc}|{x.template_tiet_hoc_id.id}": x.id for x in tiet_hoc}
    #     for i, record in enumerate(self):
    #         if record.template_tiet_hoc_id:
    #             print("tietKT", i)
    #             # tiet_kt = self.env["danh_muc.tiet_hoc"].search([
    #             #     ("tiet_hoc", "=", record.tiet_kt_so),
    #             #     ("template_tiet_hoc_id", "=",
    #             #      record.template_tiet_hoc_id.id)
    #             # ])
    #             # if len(tiet_kt) == 0:
    #             tiet_kt = map_tiet_hoc.get(f"{record.tiet_bd_so}|{record.template_tiet_hoc_id.id}")
    #             if tiet_kt == None:
    #                 raise ValidationError(f"Tiết bắt đầu phải nằm trong {record.template_tiet_hoc_id.tiethoc_id.mapped('tiet_hoc')}")
    #             record.tiet_kt = tiet_kt
    #         else:
    #             record.tiet_bd = False

    @api.depends("ngay_bd", "ky_nam_hoc_id.thoi_gian_bat_dau")
    def _compute_tuan_hoc(self):
        for record in self:
            if record.ngay_bd and record.ky_nam_hoc_id.thoi_gian_bat_dau:
                monday1 = (record.ngay_bd -
                           timedelta(days=record.ngay_bd.weekday()))
                monday2 = (record.ky_nam_hoc_id.thoi_gian_bat_dau - timedelta(
                    days=record.ky_nam_hoc_id.thoi_gian_bat_dau.weekday()))
                record.tuan_hoc = int((monday1 - monday2).days / 7) + 1
            else:
                record.tuan_hoc = False

    @api.depends("ngay_bd")
    def _compute_thu_kieu_so(self):
        for record in self:
            if record.ngay_bd:
                record.thu_kieu_so = record.ngay_bd.weekday()
            else:
                record.thu_kieu_so = -1

    @api.depends("tiet_bd.gio_bat_dau", "tiet_bd.phut_bat_dau", "ngay_bd")
    def _compute_ngay_gio_hoc(self):
        for record in self:
            if record.ngay_bd:
                current_date = datetime.combine(record.ngay_bd,
                                                datetime.min.time())
                record.ngay_gio_hoc = current_date.replace(
                    hour=record.tiet_bd.gio_bat_dau,
                    minute=record.tiet_bd.phut_bat_dau,
                )
                # if record.calendar_event_id:
                #     record.calendar_event_id.start = record.ngay_gio_hoc
            else:
                record.ngay_gio_hoc = record.ngay_gio_hoc

    @api.depends("tiet_kt.gio_ket_thuc", "tiet_kt.phut_ket_thuc", "ngay_bd")
    def _compute_ngay_gio_ket_thuc(self):
        for record in self:
            if record.ngay_bd:
                current_date = datetime.combine(record.ngay_bd,
                                                datetime.min.time())
                record.ngay_gio_ket_thuc = current_date.replace(
                    hour=record.tiet_kt.gio_ket_thuc,
                    minute=record.tiet_kt.phut_ket_thuc,
                )
                # if record.calendar_event_id:
                #     record.calendar_event_id.stop = record.ngay_gio_ket_thuc
            else:
                record.ngay_gio_ket_thuc = record.ngay_gio_ket_thuc

    @api.depends("tiet_bd", "tiet_kt")
    def _compute_so_tiet(self):
        for record in self:
            if record.tiet_bd and record.tiet_kt:
                record.so_tiet = record.tiet_kt.tiet_hoc - record.tiet_bd.tiet_hoc + 1
            else:
                record.so_tiet = record.so_tiet

    @api.depends("hoc_phan_id", "nhom_lop_tin_chi_id", "ngay_bd", "tiet_bd")
    def _compute_ten_buoi_hoc(self):
        for record in self:
            mon_hoc = ''
            nhom_lop = ''
            ngay_bd = ''
            tiet_bd = ''
            if record.hoc_phan_id:
                mon_hoc = record.hoc_phan_id.ten_hoc_phan
            if record.nhom_lop_tin_chi_id:
                nhom_lop = str(record.nhom_lop_tin_chi_id.so_thu_tu_nhom)
            if record.ngay_bd:
                ngay_bd = str(record.ngay_bd)
            if record.tiet_bd:
                tiet_bd = str(record.tiet_bd.tiet_hoc)
            record.ten_buoi_hoc = f"{mon_hoc} - {nhom_lop} - {ngay_bd} - {tiet_bd}"
            # if record.calendar_event_id:
            #     record.calendar_event_id.name = record.ten_buoi_hoc

    # @api.model
    # def create(self, values):
    #     calendar = self.env["calendar.event"].create({
    #         "name": "dummy",
    #         "start": "1900-01-01",
    #         "stop": "1900-01-01",
    #     })
    #     values["calendar_event_id"] = calendar.id
    #     buoi_hoc = super(BuoiHoc, self).create(values)
    #     return buoi_hoc

    # def unlink(self):
    #     calendar = self.mapped("calendar_event_id")
    #     res = super(BuoiHoc, self).unlink()
    #     calendar.unlink()
    #     return res

    @api.depends("diem_danh_buoi_hoc_ids", "lop_tin_chi_id.sinh_vien_ids",
                 "nhom_lop_tin_chi_id.sinh_vien_ids")
    def _compute_check_diem_danh(self):
        for record in self:
            if record.diem_danh_buoi_hoc_ids:
                if record.lop_tin_chi_id:
                    lop = record.lop_tin_chi_id.sinh_vien_ids
                    if record.nhom_lop_tin_chi_id:
                        lop = record.nhom_lop_tin_chi_id.sinh_vien_ids
                    id_sv_diem_danh = [
                        lmao.id for lmao in record.diem_danh_buoi_hoc_ids
                    ]
                    id_sv_trong_lop = [wtf.sinh_vien_id.id for wtf in lop]
                    if len(id_sv_diem_danh) == 0:
                        record.check_diem_danh = "CHUA_KHOI_TAO"
                    else:
                        result = set(id_sv_diem_danh) == set(id_sv_trong_lop)
                        if result:
                            record.check_diem_danh = "DA_KHOI_TAO"
                        else:
                            record.check_diem_danh = "DANG_KHOI_TAO"
                else:
                    record.check_diem_danh = "CHUA_KHOI_TAO"
            else:
                record.check_diem_danh = "CHUA_KHOI_TAO"

    @api.depends("lop_tin_chi_id.sinh_vien_ids",
                 "nhom_lop_tin_chi_id.sinh_vien_ids")
    def _compute_tong_so_sinh_vien(self):
        for record in self:
            if record.lop_tin_chi_id.sinh_vien_ids:
                if record.nhom_lop_tin_chi_id.sinh_vien_ids:
                    record.tong_so_sinh_vien = len(
                        record.nhom_lop_tin_chi_id.sinh_vien_ids)
                else:
                    record.tong_so_sinh_vien = len(
                        record.lop_tin_chi_id.sinh_vien_ids)
            else:
                record.tong_so_sinh_vien = False

    @api.depends("diem_danh_buoi_hoc_ids.trang_thai")
    def _compute_so_luong_vang(self):
        for record in self:
            if record.diem_danh_buoi_hoc_ids:
                record.so_luong_vang = len([
                    i for i in record.diem_danh_buoi_hoc_ids
                    if i.trang_thai == "Vắng"
                ])
            else:
                record.so_luong_vang = False

    # def create_zoom_meeting(self, values):  # da gop code cua jwt_api_access
    #     if values["is_zoom_meeting"]:
    #         print("###########################################")
    #         # api_key = '786jWzadTnSMEn0NmxfdUw'
    #         # api_secret = 'd7SIiRBbB9YzfFWr6zk5URIzXh1XhfeFcGqN'
    #         client = BuoiHoc.jwt_api_access(self)
    #         user_id = self.env.user.login
    #         kwargs = {
    #             "topic": values["name"],
    #             "type": "1",
    #         }
    #         meeting_res = client.meeting.create(user_id=user_id, **kwargs)
    #         http_status = meeting_res.status_code
    #         if http_status == 400:
    #             values["is_zoom_meeting"] = "false"
    #             raise UserError(
    #                 (
    #                     "Zoom API Exception:\n Invalid/Missing Data - Validation Failed on Meeting Values,Passwords..."
    #                 )
    #             )

    #         result = json.loads(meeting_res.content.decode("utf-8"))
    #         values["start_url"] = result["start_url"]
    #         values["join_url"] = result["join_url"]
    #         values["meeting_id"] = result["id"]
    #         values["host_id"] = result["host_id"]
    #         values["meeting_pswd"] = result["password"]
    #         print(meeting_res)
    #         print(result)
    #     else:
    #         values["start_url"] = ""
    #         values["join_url"] = ""
    #         values["meeting_id"] = ""
    #         values["host_id"] = ""
    #         values["meeting_pswd"] = ""
    #     return values

    # def jwt_api_access(self):
    #     """
    #     Connection Zoom API using JWT App
    #     """
    #     company_rec = self.env.user.company_id
    #     if company_rec.api_key and company_rec.api_secret:
    #         try:
    #             client = ZoomClient(company_rec.api_key,
    #                                 company_rec.api_secret)

    #         except Exception as e:
    #             raise UserError(_("API credential invalid", e))
    #         if self.env.user.login:
    #             users = client.user.list()
    #             if users.status_code == 200:
    #                 user_response = json.loads(users.content.decode("utf-8"))
    #                 all_users = user_response["users"]
    #                 zoom_user = False
    #                 for all_user in all_users:
    #                     if all_user["email"] == self.env.user.login:
    #                         if all_user["status"] == "active":
    #                             zoom_user = True
    #                             self.env.user.zoom_login_user_id = all_user["id"]
    #                             self.env.user.zoom_user_timezone = all_user["timezone"]
    #                             if not all_user["timezone"]:
    #                                 raise UserError(
    #                                     _("Please set zoom user timezone"))
    #                             break
    #                         else:
    #                             raise UserError(_("Invalid zoom user"))

    #                 if not zoom_user:
    #                     raise UserError(_("Invalid zoom user"))
    #             else:
    #                 raise UserError(_("Zoom API Exception"))

    #         else:
    #             raise UserError(_("Invalid zoom user"))

    #         return client
    #     else:
    #         raise UserError(_("API credential invalid"))
