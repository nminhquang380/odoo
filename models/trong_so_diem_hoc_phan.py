import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class TrongSoDiemHocPhan(models.Model):
    _name = "qldt.trong_so_diem_hoc_phan"
    _description = "Quản lý trọng số điểm theo học phần"
    '''
        CLASS này hiện không sử dụng !!!!
    '''
    # TODO: xem xét có nên bổ sung trường thông tin mô tả phương pháp đánh giá / quy chế đào tạo ?
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        ondelete="set null",
        string="Hình thức đào tạo áp dụng",
    )
    phuong_phap_danh_gia_id = fields.Many2one(
        comodel_name="danh_muc.phuong_phap_danh_gia_hoc_phan",
        ondelete="cascade",
        string="Phương pháp đánh giá",
    )
    hoc_phan_ap_dung_id = fields.Many2one(
        comodel_name="slide.channel", ondelete="set null", string="Học phần áp dụng"
    )
    dau_diem_id = fields.Many2one(
        comodel_name="danh_muc.dau_diem", ondelete="set null", string="Đầu điểm"
    )
    gia_tri_trong_so = fields.Float(string="Giá trị trọng số",group_operator=False)
    dot_nhap_hoc_ids = fields.Many2many(
        comodel_name="dot_nhap_hoc", string="Đợt nhập học áp dụng"
    )
    chuong_trinh_khung_id = fields.Many2one(
        comodel_name='chuong_trinh_khung',
        ondelete='cascade',
        string='Học phần thuộc chương trình khung'
    )
