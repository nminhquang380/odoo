import logging
import json
from odoo import models, fields, api


class LopTinChi(models.Model):
    _name = "lop_tin_chi"
    _description = "lop_tin_chi"
    _rec_name = "ma_lop"

    ten_lop_tin_chi = fields.Char("Tên lớp tín chỉ",
                                  compute="_compute_ten_lop_tin_chi",
                                  store=True)
    ma_lop = fields.Char("Mã lớp tín chỉ",
                         compute="_compute_ma_lop_tin_chi",
                         store=True)
    giang_vien_ids = fields.Many2many(comodel_name="nhan_vien",
                                      string="Danh sách giảng viên")
    sinh_vien_ids = fields.Many2many(comodel_name="sinh_vien",
                                     string="Danh sách sinh viên")
    giang_vien_id = fields.Many2one(comodel_name="nhan_vien",
                                    string="Giảng viên",
                                    ondelete="set null")
    ten_giang_vien = fields.Char("Tên giảng viên",
                                 related="giang_vien_id.name",
                                 store=True)
    mon_hoc_ids = fields.Many2one(comodel_name="slide.channel",
                                  ondelete="cascade",
                                  string="Môn học")
    ten_hoc_phan = fields.Char("Tên học phần",
                               related="mon_hoc_ids.ten_hoc_phan",
                               store=True)
    si_so = fields.Integer("Sĩ số tối đa")
    dot_dk_tin_chi_id = fields.Many2one(
        comodel_name="dot_dang_ky_tin_chi",
        string="Thuộc đợt đăng ký",
    )
    so_tin_chi = fields.Integer(string="Số tín chỉ", related="mon_hoc_ids.so_tin_chi", store=True)
    ky_nam_hoc_id = fields.Many2one("ky_nam_hoc",
                                    related="dot_dk_tin_chi_id.ky_hoc_id",
                                    store=True)
    hinh_thuc_dao_tao_id = fields.Many2one(
        "hinh_thuc_dao_tao",
        related="ky_nam_hoc_id.hinh_thuc_dao_tao_id",
        store=True)
    so_thu_tu_lop = fields.Integer(string="Số thứ tự lớp")
    # lam rieng cho TT1 damn it !!
    khoa_id = fields.Many2one("khoa_sinh_vien", "Mở cho khóa")
    ma_hoa_lich_hoc = fields.Char("Mã hóa lịch học",
                                  compute="_compute_ma_hoa_lich_hoc",
                                  store=True)
    tong_so_sinh_vien = fields.Integer("Tổng số sinh viên",
                                       compute="_compute_tong_so_sinh_vien",
                                       store=True)
    nhom_lop_tin_chi_id = fields.One2many(
        comodel_name="nhom_lop_tin_chi",
        inverse_name="ma_lop_tin_chi_id",
        string="Danh sách nhóm lớp tín chỉ",
    )
    sv_ltc_ds_id = fields.One2many(
        comodel_name="sv_ltc_ds",
        inverse_name="lop_tin_chi_id",
        string="Danh sách điểm",
    )
    buoi_hoc_ids = fields.One2many(comodel_name="buoi_hoc",
                                   inverse_name="lop_tin_chi_id",
                                   string="Lịch học - Danh sách các buổi học",
                                   domain=[('nhom_lop_tin_chi_id', '=', False)
                                           ])
    # Phòng học nên để many2one hay là gì?
    # phong_hoc = fields.Many2one("phong_hoc")
    thoi_gian_bat_dau = fields.Date("Thời gian bắt đầu")
    color = fields.Integer()
    # lich_hoc = fields.One2many(
    #     comodel_name='calendar.event',
    #     inverse_name='lich_hoc_ids',
    #     string="Lịch học"
    # )

    # TODO: cập nhật giá trị default của trọng số lớp tín chỉ với trọng
    # số học phần
    # trọng số điểm của lớp tín chỉ
    # 4 đầu điểm hiện tại làm giống với logic của trung tâm 1
    ts_attendance = fields.Float(
        related="mon_hoc_ids.ts_attendance",
        required=True,
        string="Trọng số chuyên cần")
    ts_trung_binh_kiem_tra_tren_lop = fields.Float(
        related="mon_hoc_ids.ts_trung_binh_kiem_tra_tren_lop",
        required=True,
        string="Trọng số trung bình các bài kiểm tra")
    ts_bai_tap = fields.Float(related="mon_hoc_ids.ts_bai_tap",
                              required=True,
                              string="Trọng số bài tập/thảo luận")
    ts_thi_nghiem = fields.Float(
        related="mon_hoc_ids.ts_thi_nghiem",
        required=True,
        string="Trọng số thí nghiệm - thực hành")
    ts_cuoi_ky = fields.Float(
                              related="mon_hoc_ids.ts_cuoi_ky",
                              required=True,
                              string="Trọng số kiểm tra cuối kỳ")

    _sql_constraints = [
        # (
        #     "check_sum_trong_so",
        #     "CHECK(ts_attendance + ts_bai_tap + ts_trung_binh_kiem_tra_tren_lop + ts_cuoi_ky+ ts_thi_nghiem = 100.0)",
        #     "Tổng các trọng số không bằng 100.",
        # ),
        ('unique_ma_lop', 'unique(ma_lop)',
         'Lớp tín chỉ đã tồn tại. Hãy kiểm tra lại: môn học, đợt đăng ký và số thứ tự lớp.'
         ),
    ]

    # Đây là logic cũ add sinh viên vào bảng slide_channel_partner hiện tại làm ở bên sv_ltc_ds
    # @api.model
    # def create(self, vals):
    #     res = super(LopTinChi, self).create(vals)
    #     print("đang LopTinChi này :V ")
    #     print(vals)
    #     print(self)
    #     print("channel: ",vals["mon_hoc_ids"])
    #
    #     svs=vals["sv_ltc_ds_ids"]
    #     for sv in svs:
    #         # print(s)
    #         print(sv[2]['sinh_vien_id'])
    #         tmp=self.env["sinh_vien"].search(
    #             [("id", "=", sv[2]['sinh_vien_id']),]
    #         )
    #         print(tmp.partner_id.id)
    #         val = {
    #             'channel_id': vals["mon_hoc_ids"],
    #             'partner_id': tmp.partner_id.id,
    #             'duoc_phep_dang_ky': True,
    #         }
    #         self.env["slide.channel.partner"].sudo().create(val)
    #     return res

    @api.depends("sinh_vien_ids")
    def _compute_tong_so_sinh_vien(self):
        for record in self:
            if record.sinh_vien_ids:
                record.tong_so_sinh_vien = len(record.sinh_vien_ids)
            else:
                record.tong_so_sinh_vien = False

    @api.depends("ma_lop", "mon_hoc_ids")
    def _compute_ten_lop_tin_chi_old(self):
        # pass
        for record in self:
            if record.ma_lop and record.mon_hoc_ids.name:
                record.ten_lop_tin_chi = record.mon_hoc_ids.name + "-" + record.ma_lop
            else:
                record.ten_lop_tin_chi = ""

    @api.depends("ma_lop")
    def _compute_ten_lop_tin_chi(self):
        for record in self:
            record.ten_lop_tin_chi = record.ma_lop

    @api.depends("mon_hoc_ids.ma_hoc_phan_moi", "ky_nam_hoc_id.ma_ky_nam_hoc",
                 "so_thu_tu_lop")
    def _compute_ma_lop_tin_chi(self):
        """
            Tự động tính mã lớp tín chỉ theo cú pháp mã học phần + mã kỳ + số thứ tự lớp
        """
        for record in self:
            if (record.mon_hoc_ids.ma_hoc_phan_moi
                    and record.ky_nam_hoc_id.ma_ky_nam_hoc
                    and record.so_thu_tu_lop):
                stt = str(record.so_thu_tu_lop)
                if len(stt) == 1:
                    stt = stt.zfill(2)
                record.ma_lop = (record.mon_hoc_ids.ma_hoc_phan_moi + "-" +
                                 record.ky_nam_hoc_id.ma_ky_nam_hoc + "-" +
                                 stt)
            else:
                record.ma_lop = ""

    @api.depends(
        "buoi_hoc_ids.ngay_bd",
        "buoi_hoc_ids.phong_hoc",
        "buoi_hoc_ids.tiet_bd",
        "buoi_hoc_ids.so_tiet",
        "ky_nam_hoc_id.thoi_gian_bat_dau",
    )
    def _compute_ma_hoa_lich_hoc(self):
        for record in self:
            if record.buoi_hoc_ids:
                mapss = {}
                for buoi_hoc in record.buoi_hoc_ids:
                    thu = buoi_hoc.thu_kieu_so
                    tuan = buoi_hoc.tuan_hoc
                    obj = f"{thu};{buoi_hoc.tiet_bd.tiet_hoc};{buoi_hoc.so_tiet}"
                    if obj in mapss:
                        mapss[obj].append(tuan)
                    else:
                        mapss[obj] = [tuan]

                res = []
                for key in mapss:
                    h = key.split(";")
                    res.append({
                        "thu": h[0],
                        "tietBatDau": h[1],
                        "soTiet": h[2],
                        "danhSachTuan": sorted(mapss[key]),
                    })
                res = sorted(res, key=lambda k: k['thu'])
                record.ma_hoa_lich_hoc = json.dumps(res, ensure_ascii=False)
            else:
                record.ma_hoa_lich_hoc = ""

    def action_view_diem_lop_tin_chi(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "website_slides.action_sv_ltc_ds_view_from_ltc"
        )
        action["context"] = {
            "default_lop_tin_chi_id": self.id,
        }
        action["domain"] = [("lop_tin_chi_id", "=", self.id),]
        return action

    #TODO cần xử lý để chỉ import được điểm của sinh viên trong lớp hiện tại
    def action_import_diem_lop_tin_chi(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "website_slides.action_diem_hp_import_wizard"
        )
        # action["context"] = {
        #     "default_ky_hoc_id": self.ky_nam_hoc_id,
        # }
        # action["domain"] = [("ky_hoc_id", "=", self.ky_nam_hoc_id), ]
        return action
    # TODO: cần 1 hàm tạo lớp tín chỉ từ danh sách nguyện vọng
    # sĩ số mỗi lớp tín chỉ bị ảnh hưởng bởi số lượng sinh viên
    # đăng ký học phần, số lượng phòng học và dung lượng phòng học

    def _tao_lop_tin_chi(self):
        pass
