// /** @odoo-module **/

// import publicWidget from "@web/legacy/js/public/public_widget";
// import { rpc } from "@web/core/network/rpc";

// publicWidget.registry.AddressFormExtend = publicWidget.Widget.extend({
//     selector: 'form[action*="/shop/address"]',
//     events: {
//         'change #complex_id': '_onComplexChange',
//     },

//     _onComplexChange: function(ev) {
//         var complexId = $(ev.currentTarget).val();
//         if (complexId) {
//             var self = this;

//             rpc("/get_wings", { complex_id: complexId }).then(function (wings) {
//                 var $wingSelect = $('#wing_id');
//                 $wingSelect.empty().append('<option value="">Select Wing</option>');
//                 wings.forEach(function (wing) {
//                     $wingSelect.append('<option value="' + wing.id + '">' + wing.name + '</option>');
//                 });
//             });

//             rpc("/get_region", { complex_id: complexId }).then(function (data) {
//                 $('#region_id').val(data.region_name || '');
//             });
//         }
//     },
// });

// export default publicWidget.registry.AddressFormExtend;

/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.AddressFormExtend = publicWidget.Widget.extend({
    selector: 'form[action*="/shop/address"]',
    events: {
        'change #complex_id': '_onComplexChange',
    },

    _onComplexChange: function(ev) {
        var complexId = $(ev.currentTarget).val();
        if (complexId) {
            var self = this;

            rpc("/get_wings", { complex_id: complexId }).then(function (wings) {
                var $wingSelect = $('#wing_id');
                $wingSelect.empty().append('<option value="">Select Wing</option>');
                wings.forEach(function (wing) {
                    $wingSelect.append('<option value="' + wing.id + '">' + wing.name + '</option>');
                });
            });

            rpc("/get_region", { complex_id: complexId }).then(function (data) {
                $('#region_id').val(data.region_name || '');
            });
        }
    },
});

export default publicWidget.registry.AddressFormExtend;

