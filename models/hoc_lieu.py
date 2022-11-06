import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


# class HocLieu(models.Model):
#     # _name = 'hoc_lieu'
#     _description = 'Học liệu'
#
#     _inherit= 'slide.slide'
#
#     ten_hoc_lieu = fields.Char("Tên học liệu")
#     hoc_phan_id = fields.Many2many(
#         comodel_name='slide.channel',
#         string='Thuộc học phần'
#     )
#     che_do_xem = fields.Selection(
#         [
#             ('1', 'Công khai'),
#             ('2', 'Cá nhân'),
#             # ('3', 'Cá nhân')
#         ],
#         string='Chế độ xem học liệu'
#     )
#     loai_hoc_lieu = fields.Selection(
#         [
#             ('1','Bắt buộc'),
#             ('2','Tham khảo')
#         ],
#
#         string="Loại học liệu"
#     )
#     tep_dinh_kem = fields.Binary(attachment=True,string="File tài liệu .zip")
#     tac_gia_id = fields.Many2one(
#         comodel_name='res.users',
#         ondelete='cascade',
#         string="Người tải lên"
#     )
# slide_id = fields.Many2one(
#     comodel_name='slide.slide',
#     ondelete='cascade',
#     string='Nội dung học liệu'
# )

# @api.model
# def create(self,values):
#     _logger.info("\n\n ddang theem hoc lieuj ne user id = %r\n"%(values))
#     _logger.info("%r %r"%(self._context.get('uid'),self.env['res.users'].browse(self._context.get('uid'))))
#     # tự động add user id
#     values['tac_gia_id'] = self._context.get('uid')
#     hoc_lieu = super(HocLieu,self).create(values)
#     return hoc_lieu
