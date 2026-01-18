/** @odoo-module */
import { registry } from '@web/core/registry';
const { Component, onWillStart, onMounted, useState, useRef } = owl
import { useService } from "@web/core/utils/hooks";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

export class loanDashboard extends Component {
     setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.rpc = this.env.services.rpc
        this.state = useState({
            rowsPerPage: 5,
            currentPage:1,
            totalrows: 0
        })
        onMounted(this.onMounted);
        onWillStart(this.onWillStart)
    }

     async onWillStart() {
        await this.getCardData()
        await this.getGreetings()
        await loadJS("https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js")
    }

     _downloadChart(e) {
        console.log("download called !!!!", e.target.offsetParent.children[1].children[0]);
        const chart = e.target.offsetParent.children[1].children[0]; // Get the chart canvas element
        const imageDataURL = chart.toDataURL('image/png'); // Generate image data URL
        const filename = chart.id+'.png'; // Set your preferred filename
        const link = document.createElement('a');
        link.href = imageDataURL;
        link.download = filename;
        link.click();
    }

     async getGreetings() {
        var self = this;
        const now = new Date();
        const hours = now.getHours();
        if (hours >= 5 && hours < 12) {
            self.greetings = "Good Morning";
        }
        else if (hours >= 12 && hours < 18) {
            self.greetings = "Good Afternoon";
        }
        else {
            self.greetings = "Good Evening";
        }
    }

     async onMounted() {

        this.render_loan_chart_data();
        this._onchangeLoanTypeChart();
        this.Hr_loan_Chart();
        this.render_loan_list_data(this.state.rowsPerPage, this.state.currentPage);
        this.render_filter();
    }

     downloadReport(e) {
        e.stopPropagation();
        e.preventDefault();

        var opt = {
            margin: 1,
            filename: 'LoanDashboard.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'px', format: [1920, 1080], orientation: 'landscape' }
        };
        html2pdf().set(opt).from(document.getElementById("dashboard")).save()
    }

     render_filter() {
        jsonrpc('/hr/loan/all_filter').then(function (data) {
            var users = data[0]
            var employees=data[1]
            var loan_types=data[2]
            $(users).each(function (user) {
                $('#loan_users_selection').append("<option value=" + users[user].id + ">" + users[user].name + "</option>");
            });
            $(employees).each(function (hr) {
                $('#hr_selection').append("<option value=" + employees[hr].id + ">" + employees[hr].name + "</option>");
            });
            $(loan_types).each(function (loan_type) {
                $('#loan_type_selection').append("<option value=" + loan_types[loan_type].id + ">" + loan_types[loan_type].name + "</option>");
            });
        })
    }

     _onchangeFilter(ev) {
        this.flag = 1
        var users_selection = $('#loan_users_selection').val();
        var hr_selection = $('#hr_selection').val();
        var loan_type_selection = $('#loan_type_selection').val();
        var duration_selection = $('#duration_selection').val();
        this.render_loan_chart_data();
        this._onchangeLoanTypeChart();
        this.Hr_loan_Chart();
        this.render_loan_list_data(this.state.rowsPerPage, this.state.currentPage);
        var self = this;
        jsonrpc('/loan/filter-apply', {
            'data': {
                'user': users_selection,
                'hr':hr_selection,
                'type':loan_type_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            //		    count box click that time pass data
            self.draft_lst = data['draft_lst']
            self.submit_request_lst=data['submit_request_lst']
            self.department_approve_lst=data['department_approve_lst']
            self.paid_loan_lst=data['paid_loan_lst']
            self.done_lst=data['done_lst']
            self.close_lst=data['close_lst']
            //			after change value display on xml side count
            $('#draft_lst')[0].innerHTML = data['draft_lst'].length
            $('#submit_request_lst')[0].innerHTML = data['submit_request_lst'].length
            $('#department_approve_lst')[0].innerHTML = data['department_approve_lst'].length
            $('#paid_loan_lst')[0].innerHTML = data['paid_loan_lst'].length
            $('#done_lst')[0].innerHTML = data['done_lst'].length
            $('#close_lst')[0].innerHTML = data['close_lst'].length
        })
    }

     async render_loan_chart_data(){
        var users_selection = $('#loan_users_selection').val();
        var hr_selection = $('#hr_selection').val();
        var loan_type_selection = $('#loan_type_selection').val();
        var duration_selection = $('#duration_selection').val();
		var self = this;
		await jsonrpc("/paid/loan/chart/data", {
        'data':
            {
                'user': users_selection,
                'hr':hr_selection,
                'type':loan_type_selection,
                'duration': duration_selection
            }
        }).then(function(data)
        {
			 var ctx = $("#loan_by_hr");
             new Chart(ctx, {
			 	type: "bar",
			 	data: data.hr_loan_installment,
			 	options: {
                     maintainAspectRatio: false,
                       onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.hr_loan_installment.labels[clickedIndex];
                            var clickedValue = null
                            if (element.datasetIndex == 0){
                                clickedValue = data.hr_loan_installment.datasets[0].detail[clickedIndex]
                            } else {
                                clickedValue = data.hr_loan_installment.datasets[1].detail[clickedIndex]
                            }
                            var options = {};
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'installment.line',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'tree,form',
                                views: [
                                    [false, 'tree'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options)
                        }
                        else {
                            console.log("Click outside chart area");
                        }
                    },
                     barThickness : 30,
                     responsive : true,
                     scales: {
                         x:{
                                stacked : true,
                         },
                          y: {
                          beginAtZero: true,
                        }
                    },
                }
			 });
        });

    }

     async _onchangeLoanTypeChart(){
        var users_selection = $('#loan_users_selection').val();
        var hr_selection = $('#hr_selection').val();
        var loan_type_selection = $('#loan_type_selection').val();
        var duration_selection = $('#duration_selection').val();
//        var loan_type_chart_selection=$('#loan_type_chart_selection').val();
        var self = this;
        await jsonrpc("/loan/type/chart/data",{
        'data':
            {
                'user': users_selection,
                'hr':hr_selection,
                'type':loan_type_selection,
                'duration': duration_selection
            }
        }
        ).then(function (data)
        {
            var ctx = $("#loan_amount_chart_data");
            console.log(data.loan_type_chart_data)
            console.log(ctx)
            new Chart(ctx, {
                type:'pie',
                data: data.loan_type_chart_data,
                options:
                {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.loan_type_chart_data.labels[clickedIndex];
                            const clickedValue = data.loan_type_chart_data.datasets[0].detail[clickedIndex]
                             console.log("Clicked label:", clickedLabel, "Clicked value:", clickedValue);
                            var options = {
                            };
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'employee.loan',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'tree,form',
                                views: [
                                    [false, 'tree'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options)
                        } else {
                            console.log("Click outside chart area");
                        }
                    }
                }
            });
       });
    }

     async Hr_loan_Chart(){
        var users_selection = $('#loan_users_selection').val();
        var hr_selection = $('#hr_selection').val();
        var loan_type_selection = $('#loan_type_selection').val();
        var duration_selection = $('#duration_selection').val();
//        var loan_type_chart_selection=$('#loan_type_chart_selection').val();
        var self = this;
        await jsonrpc("/hr/loan/chart/data",{
        'data':
            {
                'user': users_selection,
                'hr':hr_selection,
                'type':loan_type_selection,
                'duration': duration_selection
            }
        }).then(function (data)
        {
            var ctx = $("#hr_loan_chart_data");
            console.log(ctx)
            new Chart(ctx, {
                type:'doughnut',
                data: data.hr_loan_chart_data,
                options:
                {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.hr_loan_chart_data.labels[clickedIndex];
                            const clickedValue = data.hr_loan_chart_data.datasets[0].detail[clickedIndex]
                             console.log("Clicked label:", clickedLabel, "Clicked value:", clickedValue);
                            var options = {
                            };
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'employee.loan',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'tree,form',
                                views: [
                                    [false, 'tree'],
                                    [false, 'form']
                                ],
                                target: 'current'
                            }, options)
                        } else {
                            console.log("Click outside chart area");
                        }
                    }
                }
            });
       });
    }

     async render_loan_list_data(rowsPerPage,page) {
        var users_selection = $('#loan_users_selection').val();
        var hr_selection = $('#hr_selection').val();
        var loan_type_selection = $('#loan_type_selection').val();
        var duration_selection = $('#duration_selection').val();
        var self = this;
        var def2 = await jsonrpc("/loan/list/data",{
        'data':
            {
                'user': users_selection,
                'hr':hr_selection,
                'type':loan_type_selection,
                'duration': duration_selection
            }
        }).then(function (data) {
            //list
            var hr_loan_list = data['hr_loan_list'];
            self.state.totalrows = hr_loan_list.length;
            var tbody = document.querySelector("#employee_loan_list tbody");
            tbody.innerHTML = '';

             const start = (page - 1) * rowsPerPage;
             const end = start + rowsPerPage;
             const paginatedData = hr_loan_list.slice(start, end)

            for (var i = 0; i < paginatedData.length; i++) {
                var row = document.createElement("tr");
                const newButton = document.createElement('button');
                newButton.textContent = 'View';
                newButton.style = "background-color: #71639e; color: white;";
                newButton.className = "btn btn-primary p-2 ";

                for (var key in paginatedData[i]) {
                    if (key === 'id') {
                        newButton.value = paginatedData[i][key];
                        var btnCell = document.createElement("td");
                    }
                     else if(key==='date')
                    {
                        var cell = document.createElement("td");
                        var date=paginatedData[i]['date']
                        if(date)
                        {
                             var arr1 = date.split('-');
                             cell.textContent = arr1[2] + '-' + arr1[1] + '-' + arr1[0];
                         }
                         else
                         {
                            cell.textContent='-'
                         }
                         row.appendChild(cell);
                    }
                    else {
                        var cell = document.createElement("td");
                        if (paginatedData[i][key].length == 2) {
                            cell.textContent = paginatedData[i][key][1];
                            row.appendChild(cell);
                        } else if (paginatedData[i][key] == false) {
                            cell.textContent = '-';
                            row.appendChild(cell);
                        } else {
                            cell.textContent = paginatedData[i][key];
                            row.appendChild(cell);
                        }
                    }
                    if (key === 'date') {
                        row.appendChild(btnCell.textContent = newButton);
                    }
                    tbody.appendChild(row);
                    newButton.addEventListener('click', function () {
                        hr_loan_btn_tree_function(newButton.value);
                    });
                }
        }
            function hr_loan_btn_tree_function(id) {
                var options = {
                };
                self.action.doAction({
                    name: _t("Loan"),
                    type: 'ir.actions.act_window',
                    res_model: 'employee.loan',
                    domain: [["id", "=", id]],
                    view_mode: 'tree,form',
                    views: [
                        [false, 'tree'],
                        [false, 'form']
                    ],
                    target: 'current'
                }, options)
            }
        });
    }

     prevPage(e) {

    if (this.state.currentPage > 1) {
        this.state.currentPage--;
        this.render_loan_list_data(this.state.rowsPerPage, this.state.currentPage);
        document.getElementById("next_button").disabled = false;
    }
    if (this.state.currentPage == 1)
    {
        document.getElementById("prev_button").disabled = true;
    } else {
        document.getElementById("prev_button").disabled = false;
    }
}

     nextPage() {
    if ((this.state.currentPage * this.state.rowsPerPage) < this.state.totalrows) {
        this.state.currentPage++;
        this.render_loan_list_data(this.state.rowsPerPage, this.state.currentPage);
        document.getElementById("prev_button").disabled = false;
    }
    if (Math.ceil(this.state.totalrows / this.state.rowsPerPage) == this.state.currentPage)
    {
        document.getElementById("next_button").disabled = true;
    } else {
        document.getElementById("next_button").disabled = false;
    }
}

     action_all_loan(e) {
    e.stopPropagation();
    e.preventDefault();
    var options = {
        on_reverse_breadcrumb: this.on_reverse_breadcrumb,
    };
    var rec_id = $(e.currentTarget).children().children().attr('rec-id')
    var action = $(e.currentTarget).children().children()[0] ? $(e.currentTarget).children().children()[0].id : false;
    var domain = false;
    if (action == 'draft_lst') {
        domain = [["id", "in", this.draft_lst]];
    }
    else if (action == 'submit_request_lst') {
        domain = [["id", "in", this.submit_request_lst]]
    }
    else if (action == 'department_approve_lst') {
        domain = [["id", "in", this.department_approve_lst]]
    }
    else if (action == 'paid_loan_lst') {
        domain = [["id", "in", this.paid_loan_lst]]
    }
    else if (action == 'done_lst') {
        domain = [["id", "in", this.done_lst]]
    } else if (action == 'close_lst') {
        domain = [["id", "in", this.close_lst]]
    }

    else if (rec_id != 'undefined') {
        domain = [["id", "=", rec_id]]
    }
    this.action.doAction({
        name: _t("Loan"),
        type: 'ir.actions.act_window',
        res_model: 'employee.loan',
        domain: domain,
        view_mode: 'tree,form',
        views: [
            [false, 'tree'],
            [false, 'form']
        ],
        target: 'current'
    }, options)
}

     async getCardData(){
            var self = this;
            var def1 = jsonrpc('/get/hr/loan/data').then(function (data) {
                self.draft_lst = data['draft_lst'],
                    self.submit_request_lst = data['submit_request_lst'],
                    self.department_approve_lst = data['department_approve_lst'],
                    self.paid_loan_lst = data['paid_loan_lst'],
                    self.done_lst = data['done_lst'],
                    self.close_lst = data['close_lst'],
                    self.user_name = data['user_name']
                self.user_img = data['user_img']
            });
            return $.when(def1);
     }
}

loanDashboard.template = "loanDashboard"
registry.category("actions").add("open_loan_dashboard", loanDashboard)