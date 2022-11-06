"""
    File này lưu các cặp key,value của các security group trong Odoo (các nhóm người dùng)
    Ví dụ: internal user sẽ thuộc nhóm base.group_user
    File này kế thừa thông tin các security groups của Odoo từ base_groups.xml
"""

"""
    3 nhóm người dùng phổ biến trong Odoo
"""
internal_user = "base.group_user"
portal_user = "base.group_portal"
public_user = "base.group_public"

"""
    nhóm internal user kèm một số quyền chỉnh sửa hệ thống
"""
technical_user = "base.group_no_one"

"""
    Nhóm người dùng sử dụng nhiều hệ thống tiền tệ
    Nhóm người dùng thuộc nhiều công ty
"""
multi_currencies_user = "base.group_multi_currency"
multi_companies_user = "base.group_multi_company"

"""
    Manager - chưa rõ vai trò lắm
"""
odoo_manager = "base.group_erp_manager"

"""
    Group system - chưa rõ vai trò
"""
odoo_system_user = "base.group_system"

"""
    Đây là các conf của slink video
"""
private_key_path = 'private_key.pem'
key_id = 'K35D4UKE1MJBC5'
cloudfront_path = 'https://d30hliyf82okbo.cloudfront.net/'
thoi_gian_het_han_link = 5
