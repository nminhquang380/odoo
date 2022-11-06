from email.policy import default
from odoo import fields, models, api


# class CreateUserSVWizard(models.Model):

#     _name = "create_user_sv_wizard"
#     _description = "Tạo tài khoản sinh viên"

#     def _get_students(self):
#         if self.env.context and self.env.context.get('active_ids'):
#             return self.env.context.get('active_ids')
#         return []

#     sinh_vien_ids = fields.Many2many('sinh_vien',
#                                      default=_get_students,
#                                      string='Danh sách sinh viên')

#     def create_user(self):
#         active_ids = self.env.context.get('active_ids', []) or []
#         records = self.env['sinh_vien'].browse(active_ids)
#         records._create_user()


# class CreateUserNVWizard(models.Model):

#     _name = "create_user_nv_wizard"
#     _description = "Tạo tài khoản nhân viên"

#     def _get_employees(self):
#         if self.env.context and self.env.context.get('active_ids'):
#             return self.env.context.get('active_ids')
#         return []

#     nhan_vien_ids = fields.Many2many('nhan_vien',
#                                      default=_get_employees,
#                                      string='Danh sách nhân viên')

#     def create_user(self):
#         active_ids = self.env.context.get('active_ids', []) or []
#         records = self.env['nhan_vien'].browse(active_ids)
#         records._create_user()


# class CreateUserQTWizard(models.Model):

#     _name = "create_user_qt_wizard"
#     _description = "Tạo tài khoản quản trị viên"

#     def _get_admin(self):
#         if self.env.context and self.env.context.get('active_ids'):
#             return self.env.context.get('active_ids')
#         return []

#     quan_tri_ids = fields.Many2many('quan_tri',
#                                     default=_get_admin,
#                                     string='Danh sách quản trị')

#     def create_user(self):
#         active_ids = self.env.context.get('active_ids', []) or []
#         records = self.env['quan_tri'].browse(active_ids)
#         records._create_user()

# class CreateUserKTWizard(models.Model):

#     _name = "create_user_kt_wizard"
#     _description = "Tạo tài khoản kế toán"

#     def _get_admin(self):
#         if self.env.context and self.env.context.get('active_ids'):
#             return self.env.context.get('active_ids')
#         return []

#     ke_toan_ids = fields.Many2many('ke_toan',
#                                     default=_get_admin,
#                                     string='Danh sách kế toán')

#     def create_user(self):
#         active_ids = self.env.context.get('active_ids', []) or []
#         records = self.env['ke_toan'].browse(active_ids)
#         records._create_user()

class CreateUserTNWizard(models.Model):

    _name = "create_user_tn_wizard"
    _description = "Tạo tài khoản"

    @api.model
    def _compute_num_of_rec(self):
        active_ids = self.env.context.get('active_ids', []) or []
        return len(active_ids)

    number_of_records = fields.Integer(
        "Số lượng profile", default=_compute_num_of_rec, readonly=True)

    def create_user(self):
        active_ids = self.env.context.get('active_ids', []) or []
        model = self.env.context.get('active_model')
        records = self.env[model].browse(active_ids)
        records._create_user()
