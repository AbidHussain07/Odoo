/** @odoo-module **/

import { rpc } from '@web/core/network/rpc';
import publicWidget from '@web/legacy/js/public/public_widget';
import wSaleUtils from '@website_sale/js/website_sale_utils';  // Importing the existing utility functions

publicWidget.registry.DefaultAddToCart = publicWidget.Widget.extend({
    selector: '.oe_website_sale .oe_cart',  // Targeting Odoo default cart button
    events: {
        'click .js_add_to_cart': '_onClickAddToCart',
    },

    init() {
        this._super(...arguments);
    },

    async _onClickAddToCart(ev) {
        const form = ev.currentTarget.closest('form');
        const formData = new FormData(form);

        // Capture selected meal_type and working_days from the form
        const mealType = formData.get('meal_type');
        const workingDays = formData.get('working_days');

        // Debugging: Log the captured mealType and workingDays
        console.log("Captured meal_type: ", mealType);
        console.log("Captured working_days: ", workingDays);

        // Append the captured fields to the form data
        formData.append('meal_type', mealType);
        formData.append('working_days', workingDays);

        // Convert the form data to a query string
        const params = new URLSearchParams(formData);

        // Debugging: Log the final params to check if everything is appended
        console.log("Form Params: ", params.toString());

        // Send the data to the backend to update the cart
        await this._updateCart(params);
    },

    // Function to handle the actual update to the cart
    async _updateCart(params) {
        try {
            const data = await rpc("/shop/cart/update", params);
            // Update the cart UI if needed
            wSaleUtils.updateCartNavBar(data);
            wSaleUtils.showCartNotification(this.call.bind(this), data.notification_info);
        } catch (error) {
            console.error("Error while updating cart:", error);
        }
    }
});

export default publicWidget.registry.DefaultAddToCart;



// import publicWidget from "@web/legacy/js/public/public_widget";

// publicWidget.registry.WorkingDaysSelection = publicWidget.Widget.extend({
//     selector: 'form[action="/shop/cart/update"]',
//     events: {
//         'change .working-days-checkbox': '_updateWorkingDays',
//         'change .plan-selection': '_updatePlanId'  // If plan is selectable
//     },

//     _updateWorkingDays: function() {
//         let selectedDays = [];
//         document.querySelectorAll(".working-days-checkbox:checked").forEach(checkbox => {
//             selectedDays.push(checkbox.value);
//         });

//         document.getElementById("selected_working_days").value = selectedDays.join(",");
//     },

//     _updatePlanId: function(ev) {
//         let planId = ev.currentTarget.value;
//         document.getElementById("selected_plan_id").value = planId;
//     }
// });

// export default publicWidget.registry.WorkingDaysSelection;
