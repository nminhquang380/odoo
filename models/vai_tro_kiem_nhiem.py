from odoo import models, fields

from .constants_of_selection_fields import vai_tro_don_vi_selection


class VaiTroKiemNhiem(models.Model):
    _name = "vai_tro_kiem_nhiem"
    _description = "Vai trò kiêm nhiệm"
    _rec_name = "nhan_vien_id"

    nhan_vien_id = fields.Many2one(comodel_name="nhan_vien",
                                   ondelete='set null',
                                   string='Nhân viên')
    ma_dinh_danh = fields.Char("Mã định danh",
                               related="nhan_vien_id.ma_dinh_danh",
                               store=True)
    so_dien_thoai = fields.Char("Số điện thoại",
                                related="nhan_vien_id.so_dien_thoai",
                                store=True)
    gioi_tinh = fields.Selection([("0", "Nam"), ("1", "Nữ"), ("2", "Khác")],
                                 string="Giới tính",
                                 related="nhan_vien_id.gioi_tinh",
                                 store=True)
    vai_tro_goc = fields.Selection(selection=vai_tro_don_vi_selection,
                                   string='Vai trò gốc',
                                   related="nhan_vien_id.vai_tro_goc",
                                   store=True)
    so_cmnd = fields.Char("Chứng minh nhân dân/căn cước công dân",
                          size=12,
                          related="nhan_vien_id.so_cmnd",
                          store=True)
    email = fields.Char("Email đăng nhập",
                        size=500,
                        related="nhan_vien_id.email",
                        store=True)
    dan_toc = fields.Char("Dân tộc",
                          size=255,
                          related="nhan_vien_id.dan_toc",
                          store=True)
    ton_giao = fields.Char("Tôn giáo",
                           size=255,
                           related="nhan_vien_id.ton_giao",
                           store=True)
    tinh_tp_no = fields.Char("Tỉnh/thành phố",
                             size=255,
                             related="nhan_vien_id.tinh_tp_no",
                             store=True)
    quan_huyen_no = fields.Char("Quận/huyện",
                                size=255,
                                related="nhan_vien_id.quan_huyen_no",
                                store=True)
    phuong_xa_no = fields.Char("Phường/xã",
                               size=255,
                               related="nhan_vien_id.phuong_xa_no",
                               store=True)
    so_nha_ten_duong_no = fields.Char(
        "Số nhà/tên đường",
        size=255,
        related="nhan_vien_id.so_nha_ten_duong_no",
        store=True)
    don_vi_id = fields.Many2one(comodel_name="danh_muc.don_vi",
                                ondelete='set null',
                                string='Đơn vị')
    vai_tro = fields.Selection(selection=vai_tro_don_vi_selection,
                               string='Vai trò')
