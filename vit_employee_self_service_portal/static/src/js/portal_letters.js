/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import PortalSidebar from "@portal/js/portal_sidebar";
import {PortalHomeCounters} from '@portal/js/portal';

PortalHomeCounters.include({
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['letters_count']);
    },
});

publicWidget.registry.LettersPortalSidebar = PortalSidebar.extend({
    selector: '.o_portal_letter_sidebar',
    events: {
        'click .o_portal_letter_print': '_printLetterReport',
    },
    _printLetterReport: function (ev) {
        ev.preventDefault();
        let report_url = $(ev.currentTarget).attr('report_url');
        this.printPdf(report_url);
    }
});
publicWidget.registry.PortalLetters = publicWidget.Widget.extend({
    selector: '.salary_letter_details',
    events: {
        'change #agencies_categories': '_onChangeAgenciesTypes',
        'change #need_ratification_checkbox': '_onChangeNeedRatificationCheckbox',
        'change #letter_types': '_onChangeLetterTypes'
    },
    start: function () {
        var def = this._super.apply(this, arguments);
        this.$("#letter_types option:first").prop("selected", "selected");
        this.$agencies_names_div = this.$('div[name="agencies_names_div"]');
        this.$letters_need_ratification = this.$('input[name="letter_types_need_ratification"]');
        this.$need_ratification_checkbox = this.$('input[id="need_ratification_checkbox"]');
        this.$agencies_names_div.hide();
        this.$agencies_select = this.$('select[id="agencies_select"]');
        this.$another_agency_name = this.$("input[name='another_agency']");
        this.$another_agency_name.hide();
        this.$another_agency_name.prop('required', false);
        this.rpc = this.bindService("rpc")
        return def;
    },
    _onChangeAgenciesTypes: function (ev) {
        var selectElement = ev.target;
        var value = selectElement.value;
        console.log("Agencies Selected = ", value);
        var self = this;
        this.$agencies_names_div.hide();
        if (value) {
            self.$agencies_names_div[0].style.display = 'block';
            self.$agencies_names_div.show();
            self.$agencies_select.find("option").remove().end().append(`<option value=''>Select...</option>`);

            //Calling the server to fetch the agencies of selected category
            self.rpc("/letter_request_categories", {letter_category_id: parseInt(value)}).then(function (data) {
                if (data.category_agencies && data.category_agencies.length) {
                    data.category_agencies.forEach((agency) => {
                        self.$agencies_select.append(`<option value=${agency.id}>${agency.name}</option>`);
                    });
                    self.$agencies_select.show()
                    self.$agencies_select.prop('required', true);
                    self.$another_agency_name.hide();
                    self.$another_agency_name.prop('required', false);
                } else {
                    self.$agencies_select.hide()
                    self.$agencies_select.prop('required', false);
                    self.$another_agency_name.show();
                    self.$another_agency_name.prop('required', true);
                }
            });
        }
    },
    _onChangeLetterTypes: function(ev){
        let value = ev.target.value;
        let letters_needs_ratification = JSON.parse(this.$letters_need_ratification.val());
        if(value && letters_needs_ratification.includes(parseInt(value))){
            this.$need_ratification_checkbox.prop('checked', true);
            this.$('div[id="ratification_message"]').show();
        }else{
            this.$need_ratification_checkbox.prop('checked', false);
            this.$('div[id="ratification_message"]').hide();
        }

    },
    _onChangeNeedRatificationCheckbox: function(ev){
        if(ev.target.checked){
            this.$('div[id="ratification_message"]').show();
        }else{
            this.$('div[id="ratification_message"]').hide();
        }
    }
})