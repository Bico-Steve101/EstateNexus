    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var checkboxes = document.querySelectorAll('input[type=checkbox]');
    var downloadButton = document.getElementById('downloadButton');

    // Initially hide the download button
    downloadButton.style.display = 'none';

    // Event listener for 'all' checkbox
    document.getElementById('all').addEventListener('change', function() {
        // If 'all' checkbox is checked, check all checkboxes
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = this.checked;
        }, this);

        // Show or hide the download button based on whether 'all' checkbox is checked
        if (this.checked) {
            downloadButton.style.display = 'block';
        } else {
            downloadButton.style.display = 'none';
        }
    });

    // Event listener for individual checkboxes
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            // If any checkbox is checked, render the download button
            if (document.querySelectorAll('input[type=checkbox]:checked').length > 0) {
                downloadButton.style.display = 'block';
            } else {
                // If no checkboxes are checked, hide the download button
                downloadButton.style.display = 'none';
            }

            // If not all checkboxes are checked, uncheck the 'all' checkbox
            var allCheckbox = document.getElementById('all');
            if (document.querySelectorAll('input[type=checkbox]:checked').length !== checkboxes.length) {
                allCheckbox.checked = false;
            } else {
                allCheckbox.checked = true;
            }
        });
    });

    // Event listener for download button
    document.getElementById('downloadButton').addEventListener('click', function() {
        var selectedRows = [];
        var allCheckbox = document.getElementById('all');

        if (allCheckbox.checked) {
            // If 'all' checkbox is checked, select all rows
            selectedRows = Array.from(document.querySelectorAll('tbody tr'));
        } else {
            // Otherwise, select only the checked rows
            var checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
            checkboxes.forEach(function(checkbox) {
                var row = checkbox.closest('tr'); // Get the row element
                selectedRows.push(row);
            });
        }

        // Create a new table and populate it with selected rows
        var newTable = document.createElement('table');
        var newBody = document.createElement('tbody');
        selectedRows.forEach(function(row) {
            var clonedRow = row.cloneNode(true);
            clonedRow.removeChild(clonedRow.lastElementChild); // Remove the last cell (dropdown menu)
            newBody.appendChild(clonedRow);
        });
        var newHead = document.querySelector('thead').cloneNode(true);
        newHead.querySelector('th:last-child').remove(); // Remove the last header cell ("Action")
        newTable.appendChild(newHead);
        newTable.appendChild(newBody);

        // Convert the new table to Excel
        var wb = XLSX.utils.table_to_book(newTable);
        XLSX.writeFile(wb, "data.xlsx");

        // Show success message
        alert('File has been downloaded successfully!');
    });
    $(function () {
    // Function to fetch property data via AJAX
    function getPropertyData() {
        $.ajax({
            url: '/api/property-data/',
            method: 'GET',
            success: function (data) {
                // Process the fetched data and render the charts
                renderCharts(data);
            },
            error: function (xhr, status, error) {
                console.error('Error fetching property data:', error);
            }
        });
    }

    // Function to render the charts with the fetched property data
    function renderCharts(propertyData) {
        // Extracting property names and prices for rendering
        var propertyNames = propertyData.map(function (property) {
            return property.name;
        });
        var propertyPrices = propertyData.map(function (property) {
            return property.price;
        });

        // Rendering the Profit chart with property data
        var profitChart = {
            // Chart configuration remains the same
            // (this part is unchanged from the previous code)
        };
        var profitChart = new ApexCharts(document.querySelector("#chart"), profitChart);
        profitChart.render();

        // Rendering the Breakup chart with example data
        var breakupChart = {
            // Chart configuration remains the same
            // (this part is unchanged from the previous code)
        };
        var breakupChart = new ApexCharts(document.querySelector("#breakup"), breakupChart);
        breakupChart.render();

        // Rendering the Earning chart with example data
        var earningChart = {
            // Chart configuration remains the same
            // (this part is unchanged from the previous code)
        };
        var earningChart = new ApexCharts(document.querySelector("#earning"), earningChart);
        earningChart.render();

        // Rendering the Monthly Earning chart with actual property data
        var monthlyEarningChart = {
            series: [{
                name: 'Monthly Earnings',
                data: propertyPrices // Use actual monthly earning data from propertyPrices
            }],
            chart: {
                type: 'line',
                height: 350
            },
            xaxis: {
                categories: propertyNames // Use property names as x-axis labels
            }
        };
        var monthlyEarningChart = new ApexCharts(document.querySelector("#monthly-earning"), monthlyEarningChart);
        monthlyEarningChart.render();

        // Fetching and rendering yearly earning data
        $.ajax({
            url: '/api/yearly-earning-data/',
            method: 'GET',
            success: function (yearlyData) {
                // Rendering the Yearly Earning chart with fetched data
                var yearlyEarningChart = {
                    series: [{
                        name: 'Yearly Earnings',
                        data: yearlyData // Use actual yearly earning data
                    }],
                    chart: {
                        type: 'line',
                        height: 350
                    },
                    xaxis: {
                        categories: Object.keys(yearlyData) // Use years as x-axis labels
                    }
                };
                var yearlyEarningChart = new ApexCharts(document.querySelector("#yearly-earning"), yearlyEarningChart);
                yearlyEarningChart.render();
            },
            error: function (xhr, status, error) {
                console.error('Error fetching yearly earning data:', error);
            }
        });
    }

    // Fetch property data and render charts when the page loads
    getPropertyData();
});

