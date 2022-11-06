odoo.define('website_slides.import_custom', function (require) {
    "use strict";
    var ListController = require("web.ListController");
    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            var self = this;
            self.$buttons.on('click', '.import-lop-tin-chi', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_lop_tin_chi_import_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.export-lop-tin-chi', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_lop_tin_chi_export_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.export-report-dang-ky-nhu-cau', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_report_dang_ky_nhu_cau',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.import-danh-sach-sinh-vien', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_dssv_import_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.sinh-vien-import-template', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_export_template',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.nhan-vien-import-template', function () {
                self._rpc({
                    model: 'export_template',
                    method: 'export_mau_import_sv_nv',
                    args: [""],
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.import-buoi-hoc', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_tkb_import_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.export-buoi-hoc', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_tkb_export_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.import-diem-hoc-phan', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_diem_hp_import_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.import-lop-hanh-chinh', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_lop_hanh_chinh_import_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.export-lop-hanh-chinh', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_lop_hanh_chinh_export_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.export-sinh-vien', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_sinh_vien_export_wizard',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
            self.$buttons.on('click', '.export-hoa-don', function () {
                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: 'website_slides.action_export_hoa_don',
                    },
                })
                    .then(function (r) {
                        console.log(r);
                        return self.do_action(r);
                    });
            });
        }
    };
    ListController.include(includeDict);
});