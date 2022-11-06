from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CoSoHanhChinh(models.Model):
    _name = "co_so_hanh_chinh"
    _description = "Cơ sở hành chính"
    _rec_name = "ten_don_vi"

    ten_don_vi = fields.Char(string="Tên đơn vị hành chính")
    ma_don_vi = fields.Char(string="Mã đơn vị hành chính")
    ten_tieng_anh = fields.Char(string="Tên tiếng Anh")

    cap_don_vi = fields.Integer(string="Cấp đơn vị")
    ten_cap_don_vi = fields.Char(string="Tên cấp đơn vị")
    
    ma_don_vi_truc_thuoc = fields.Char(string="Mã đơn vị trực thuộc")
    ten_don_vi_truc_thuoc = fields.Char(string="Đơn vị trực thuộc",
                                        #  related="ma_don_vi_truc_thuoc.ten_don_vi"
                                         )

    # don_vi_cap_duoi = fields.One2many("co_so_hanh_chinh",
    #                                   "ma_don_vi_truc_thuoc",
    #                                   string="Các đơn vị hành chính cấp dưới")
    
    _sql_constraints = [
        ('unique_ma_don_vi', 'unique (ma_don_vi)',
        'Mã đơn vị hành chính này đã được sử dụng'),
    ]


    @api.constrains("cap_don_vi")
    def _compute_ten_cap(self):
        for record in self:
            if record.cap_don_vi == 1:
                record.ten_cap_don_vi = 'Tỉnh/Thành phố'
            elif record.cap_don_vi == 2:
                record.ten_cap_don_vi = "Quận/Huyện"
            elif record.cap_don_vi == 3:
                record.ten_cap_don_vi = "Phường/Xã"
            else:
                record.ten_cap_don_vi = ""


class TruongTHPT(models.Model):
    _name = "truong_thpt"
    _description = "Trường Trung học Phổ thông"

    ma_truong = fields.Char(string="Mã trường", required=True)
    ten_truong = fields.Char(string="Tên trường", required=True)

    ma_tinh_tp = fields.Char(string="Mã tỉnh, thành phố", required=True)
    ten_tinh_tp = fields.Char(string="Tên tỉnh, thành phố", required=True)

    ma_quan_huyen = fields.Char(string="Mã quận, huyện", required=True)
    ten_quan_huyen = fields.Char(string="Tên quận, huyện", required=True)

    dia_chi = fields.Char(string="Địa chỉ")
    khu_vuc = fields.Char(string="Khu vực", required=True)

    truong_dtnt = fields.Boolean(string="Trường dân tộc nội trú")
    truong_chuyen = fields.Boolean(string="Trường chuyên")

    _sql_constraints = [
        ('unique_ma_truong', 'unique(ma_truong)',
        'Mã trường này đã được sử dụng'),
    ]

class DanToc(models.Model):
    _name = "dan_toc"
    _description = "Dân tộc"

    ma_dan_toc = fields.Char(string="Mã dân tộc", required=True)
    ten_dan_toc = fields.Char(string="Tên dân tộc", required=True)

    _sql_constraints = [
        ('unique_ma_dan_toc', 'unique(ma_dan_toc)',
        'Mã dân tộc này đã được sử dụng')
    ]

class TonGiao(models.Model):
    _name = "ton_giao"
    _description = "Tôn giáo"

    ma_ton_giao = fields.Char(string="Mã tôn giáo", required=True)
    ten_ton_giao = fields.Char(string="Tên tôn giáo", required=True)

    _sql_constraints = [
        ('unique_ma_ton_giao', 'unique(ma_ton_giao)',
        'Mã tôn giáo này đã được sử dụng')
    ]