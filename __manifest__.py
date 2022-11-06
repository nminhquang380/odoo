# -*- coding: utf-8 -*-
{
    'name':
    'PTIT-DU',
    'version':
    '2.2',
    'sequence':
    125,
    'summary':
    'Manage and publish an digital university platform',
    'website':
    'https://google.com',
    'category':
    'Website/eLearning',
    'description':
    """
Create Online Coursesss
=====================

Featuring

 * Integrated course and lesson management
 * Fullscreen navigation
 * Support Youtube videos, Google documents, PDF, images, web pages
 * Test knowledge with quizzes
 * Filter and Tag
 * Statistics
""",
    'depends': [
        'calendar',
        'api_restful_odoo',
        'portal_rating',
        'mass_mailing',
        'website',
        'website_mail',
        'website_profile',
    ],
    'data': [
        'security/website_slides_security.xml',
        'security/ir.model.access.csv',
        # 'views/dang_ky_tin_chi_views.xml',
        'views/cong_no_views.xml',
        'views/cong_nhan_ket_qua_hoc_tap.xml',
        'views/danh_gia_ket_qua_hoc_tap.xml',
        'views/xu_ly_ket_qua_hoc_tap.xml',
        'views/lop_hanh_chinh_views.xml',
        'views/lop_boi_duong_views.xml',
        'views/ky_nam_hoc.xml',
        'views/nam_hoc.xml',
        'views/lop_tin_chi_views.xml',
        'views/nhom_lop_tin_chi_views.xml',
        'views/phieu_dang_ky_hoc_phan.xml',
        'views/phieu_dang_ky_tin_chi.xml',
        'views/nv_hoc_phan.xml',
        'views/sv_hp_dot_dang_ky_tin_chi.xml',
        'views/sv_ltc_ds.xml',
        'views/khoa_sinh_vien_views.xml',
        'views/hinh_thuc_dao_tao_views.xml',
        'views/trinh_hinh_dao_tao_views.xml',
        'views/dot_nhap_hoc.xml',
        'views/nganh_views.xml',
        'views/sinh_vien.xml',
        'views/tro_giang.xml',
        'views/nhan_vien.xml',
        'views/quan_tri.xml',
        'views/ke_toan.xml',
        'views/quan_tri_vien_boi_duong.xml',
        'views/can_bo_qlkh.xml',
        'views/lanh_dao.xml',
        'views/so_lieu_views.xml',
        'views/danh_muc_views.xml',
        'views/co_so_hanh_chinh_views.xml',
        'views/diem_danh_buoi_hoc.xml',
        'views/hoc_ky_chuong_trinh_khung.xml',
        'views/chuong_trinh_khung_views.xml',
        'views/buoi_hoc_views.xml',
        'views/thoi_khoa_bieu.xml',
        'views/dot_dang_ky_tin_chi_views.xml',
        'views/dot_dang_ky_nhu_cau_views.xml',
        'views/quan_ly_lich_thi.xml',
        'views/khoi_lop.xml',
        'views/khoa_nganh.xml',
        'views/assets.xml',
        'views/quy_tac_danh_gia_ket_qua_hoc_tap.xml',
        'views/quy_tac_cong_nhan_ket_qua_hoc_tap.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/rating_rating_views.xml',
        'views/ky_hoc.xml',
        'views/hoc_phan_relations_views.xml',
        'views/tin_tuc.xml',
        'views/hoc_phi.xml',
        'views/trong_so_diem_hoc_phan.xml',
        'views/mo_hoc_phan_theo_dot_nhu_cau.xml',
        'views/custom_import.xml',
        'views/custom_export.xml',
        'views/custom_report.xml',
        'views/custom_noti.xml',
        'views/create_user.xml',
        'views/slide_question_views.xml',
        'views/slide_answer_views.xml',
        'views/slide_slide_views.xml',
        'views/slide_channel_partner_views.xml',
        'views/slide_slide_partner_views.xml',
        'views/slide_channel_views.xml',
        'views/slide_channel_tag_views.xml',
        'views/sv_hp_ds.xml',
        'views/sinh_vien_diem_tong_ket.xml',
        'views/sinh_vien_hoc_ky.xml',
        'views/su_co.xml',
        'views/quy_che_dao_tao_nam_hoc.xml',
        'views/vai_tro_kiem_nhiem.xml',
        'views/website_slides_menu_views.xml',
        'views/website_slides_templates_homepage.xml',
        'views/website_slides_templates_course.xml',
        'views/website_slides_templates_lesson.xml',
        'views/website_slides_templates_lesson_fullscreen.xml',
        'views/website_slides_templates_lesson_embed.xml',
        'views/website_slides_templates_profile.xml',
        'views/website_slides_templates_utils.xml',
        'wizard/slide_channel_invite_views.xml',
        'data/gamification_data.xml',
        'data/mail_data.xml',
        'data/mail_activity_data.xml',
        'data/slide_data.xml',
        'data/website_data.xml',
    ],
    'demo': [
        'data/res_users_demo.xml',
        'data/slide_channel_tag_demo.xml',
        'data/slide_channel_demo.xml',
        'data/slide_slide_demo.xml',
        'data/slide_user_demo.xml',
    ],
    'qweb': [
        'static/src/xml/activity.xml',
        'static/src/xml/import_excel_button.xml',
    ],
    'installable':
    True,
    'application':
    True,
}
