import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class LopBoiDuong(models.Model):
    _name = "qldt.lop_boi_duong"
    _description = "Lớp bồi dưỡng"
    _rec_name = "ten_lop_boi_duong"

    ten_lop_boi_duong = fields.Char("Tên lớp", required=True)
    ma_lop_boi_duong = fields.Char("Mã lớp")
    can_bo_id = fields.Many2one(comodel_name='nhan_vien',
                                ondelete='set null',
                                string='Cán bộ phụ trách')
    ten_can_bo = fields.Char(related="can_bo_id.name",
                             store=True,
                             string="Tên cán bộ")
    tro_giang_id = fields.Many2one(comodel_name="tro_giang",
                                   string="Trợ giảng")
    ten_tro_giang = fields.Char("Tên trợ giảng",
                                related="tro_giang_id.name",
                                store=True)
    sinh_vien_ids = fields.Many2many(comodel_name='sinh_vien',
                                     string='Sinh viên/học viên')
    slide_channel_id = fields.Many2one(comodel_name="slide.channel",
                                       ondelete="set null",
                                       string="Môn học")
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                           ondelete="set null",
                                           string="Hình thức đào tạo")
    si_so = fields.Integer(compute="_compute_tinh_si_so",
                           store=True,
                           string="Sĩ số")
    mailing_list = fields.Many2one(comodel_name='mailing.list',
                                   ondelete='set null',
                                   compute="_compute_tao_mailing_list",
                                   store=True,
                                   string="Danh sách mail")
    thoi_gian_bat_dau = fields.Date("Thời gian bắt đầu")
    thoi_gian_ket_thuc = fields.Date("Thời gian kết thúc")
    ghi_chu = fields.Html("Ghi chú")

    @api.depends("ten_lop_boi_duong", "sinh_vien_ids")
    def _compute_tao_mailing_list(self):
        for record in self:
            if record.ten_lop_boi_duong:
                mailing_list = self.env['mailing.list'].search([
                    ('name', '=', record.ten_lop_boi_duong)
                ])
                if not mailing_list.name:
                    mailing_list = self.env['mailing.list'].create(
                        {'name': record.ten_lop_boi_duong})
                # _logger.info("sinh_vien_ids{}".format(record.sinh_vien_ids))
                record.mailing_list = mailing_list.id
                return mailing_list.id

    def xoa_sinh_vien_khoi_mailing_list(self, sinh_vien_mon_hoc,
                                        mailing_list_id):
        masv = self.env['sinh_vien'].search([
            ('partner_id.id', '=', sinh_vien_mon_hoc.partner_id.id)
        ]).ma_dinh_danh
        ten_contact = 'BDNH_' + str(self.ma_lop_boi_duong) + '_' + str(masv)
        self.env['mailing.contact'].search([('name', '=', ten_contact)
                                            ]).unlink()
        _logger.info("XÓA sinh viên {} khỏi mailing_list".format(masv))

    @api.depends("sinh_vien_ids")
    def _compute_tinh_si_so(self):
        for record in self:
            if record.sinh_vien_ids:
                record.si_so = len(record.sinh_vien_ids)
            else:
                record.si_so = 0

    @api.constrains("sinh_vien_ids")
    def add_sinh_vien_to_slide_channel_partner(self):
        """
                Nếu có thay đổi ở trường sinh_vien_ids thì:
                 1. tự động thử add các sinh viên này vào bảng slide_channel_partner
                 2. Tự động add sinh viên vào mailing list của lớp học
                TODO:
                    1. Tối ưu hóa thuật toán để giảm số lần ghi DB
                    2. Khi sinh viên không ở trong lớp thì xóa khỏi mailing list
        """
        for record in self:
            mailing_list_id = record._compute_tao_mailing_list()
            if record.sinh_vien_ids and record.slide_channel_id:
                for each_sv in record.sinh_vien_ids:
                    try:
                        r = self.env['slide.channel.partner'].search([
                            ('channel_id', '=', record.slide_channel_id.id),
                            ('partner_id', '=', each_sv.partner_id._origin.id)
                        ])
                        if not r:
                            # thêm sinh viên vào slide_channel_partner
                            self.env['slide.channel.partner'].create({
                                'channel_id':
                                record.slide_channel_id.id,
                                'partner_id':
                                each_sv.partner_id._origin.id
                            })
                            # thêm sinh viên vào mailing list
                            ten_contact = 'BDNH_' + str(
                                record.ma_lop_boi_duong) + '_' + str(
                                    each_sv.ma_dinh_danh)
                            if each_sv.email:
                                contact = self.env['mailing.contact'].create({
                                    'name':
                                    ten_contact,
                                    'email':
                                    each_sv.email,
                                    'list_ids': [(mailing_list_id)],
                                    'login':
                                    each_sv.user_id.login,
                                    'ten':
                                    each_sv.partner_id.name
                                    # chú ý cú pháp chỗ này có thể sẽ không phù hợp về sau
                                })
                            elif each_sv.email_to_chuc:
                                contact = self.env['mailing.contact'].create({
                                    'name':
                                    ten_contact,
                                    'email':
                                    each_sv.email_to_chuc,
                                    'list_ids': [(mailing_list_id)],
                                    'login':
                                    each_sv.user_id.login,
                                    'ten':
                                    each_sv.partner_id.name
                                    # chú ý cú pháp chỗ này có thể sẽ không phù hợp về sau
                                })
                            _logger.info(
                                "Thêm sinh viên {} vào mailing_list".format(
                                    contact))
                        else:
                            _logger.info("ban ghi da ton tai : {}".format(r))

                    except Exception as e:
                        _logger.error(e)
                        continue

            sinh_vien_mon_hoc_search = self.env[
                'slide.channel.partner'].search([('channel_id', '=',
                                                  record.slide_channel_id.id)])
            for sinh_vien_mon_hoc in sinh_vien_mon_hoc_search:
                van_ton_tai = False
                if not record.sinh_vien_ids:
                    try:
                        record.xoa_sinh_vien_khoi_mailing_list(
                            sinh_vien_mon_hoc, mailing_list_id)
                        self.env['slide.channel.partner'].search([
                            ('channel_id', '=',
                             sinh_vien_mon_hoc.channel_id.id),
                            ('partner_id', '=',
                             sinh_vien_mon_hoc.partner_id._origin.id)
                        ]).unlink()
                    except Exception as e:
                        _logger.error(e)
                        continue
                else:
                    for each_sv in record.sinh_vien_ids:
                        if each_sv.partner_id.id == sinh_vien_mon_hoc.partner_id.id:
                            van_ton_tai = True
                    if van_ton_tai == False:
                        record.xoa_sinh_vien_khoi_mailing_list(
                            sinh_vien_mon_hoc, mailing_list_id)
                        self.env['slide.channel.partner'].search([
                            ('channel_id', '=',
                             sinh_vien_mon_hoc.channel_id.id),
                            ('partner_id', '=',
                             sinh_vien_mon_hoc.partner_id._origin.id)
                        ]).unlink()

    def action_sinh_vien_lop_boi_duong(self, state=None):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.slide_channel_partner_action")
        action["domain"] = [("channel_id", "=", self.slide_channel_id.id),
                            ("partner_id", "in",
                             self.sinh_vien_ids.partner_id.ids)]
        return action

    def action_thong_ke_quiz(self, state=None):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.slide_slide_partner_action")
        action["domain"] = [("channel_id", "=", self.slide_channel_id.id),
                            ("partner_id", "in",
                             self.sinh_vien_ids.partner_id.ids)]

        return action

    # @api.model
    # def create(self,vals):
    #     mailing_list = self.env['mailing.list'].search([
    #         ('name','=',vals.get("ten_lop_boi_duong"))
    #     ])
    #     if not mailing_list:
    #         if vals.get("ten_lop_boi_duong"):
    #             self.env['mailing.list'].create({
    #                 'name':vals.get("ten_lop_boi_duong")
    #             })
    #     else:
    #         _logger.info("Mailing list cho {} đã tồn tại".format(mailing_list.name))
    #     res = super(LopBoiDuong,self).create(vals)
    #     return res
