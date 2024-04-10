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
            series: [
                { name: "Earnings this month:", data: propertyPrices },
                { name: "Expense this month:", data: propertyPrices }, // Example data for expense (replace with actual expense data)
            ],
            chart: {
                type: "bar",
                height: 345,
                offsetX: -15,
                toolbar: { show: true },
                foreColor: "#adb0bb",
                fontFamily: 'inherit',
                sparkline: { enabled: false },
            },
            colors: ["#5D87FF", "#49BEFF"],
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: "35%",
                    borderRadius: [6],
                    borderRadiusApplication: 'end',
                    borderRadiusWhenStacked: 'all'
                },
            },
            markers: { size: 0 },
            dataLabels: {
                enabled: false,
            },
            legend: {
                show: false,
            },
            grid: {
                borderColor: "rgba(0,0,0,0.1)",
                strokeDashArray: 3,
                xaxis: {
                    lines: {
                        show: false,
                    },
                },
            },
            xaxis: {
                type: "category",
                categories: propertyNames,
                labels: {
                    style: { cssClass: "grey--text lighten-2--text fill-color" },
                },
            },
            yaxis: {
                show: true,
                min: 0,
                tickAmount: 4,
                labels: {
                    style: {
                        cssClass: "grey--text lighten-2--text fill-color",
                    },
                },
            },
            stroke: {
                show: true,
                width: 3,
                lineCap: "butt",
                colors: ["transparent"],
            },
            tooltip: { theme: "light" },
            responsive: [
                {
                    breakpoint: 600,
                    options: {
                        plotOptions: {
                            bar: {
                                borderRadius: 3,
                            }
                        },
                    }
                }
            ]
        };

        var profitChart = new ApexCharts(document.querySelector("#chart"), profitChart);
        profitChart.render();

        // Rendering the Breakup chart with example data
        var breakupChart = {
            color: "#adb5bd",
            series: [38, 40, 25],
            labels: ["2022", "2021", "2020"],
            chart: {
                width: 180,
                type: "donut",
                fontFamily: "Plus Jakarta Sans', sans-serif",
                foreColor: "#adb0bb",
            },
            plotOptions: {
                pie: {
                    startAngle: 0,
                    endAngle: 360,
                    donut: {
                        size: '75%',
                    },
                },
            },
            stroke: {
                show: false,
            },
            dataLabels: {
                enabled: false,
            },
            legend: {
                show: false,
            },
            colors: ["#5D87FF", "#ecf2ff", "#F9F9FD"],
            responsive: [
                {
                    breakpoint: 991,
                    options: {
                        chart: {
                            width: 150,
                        },
                    },
                },
            ],
            tooltip: {
                theme: "dark",
                fillSeriesColor: false,
            },
        };

        var breakupChart = new ApexCharts(document.querySelector("#breakup"), breakupChart);
        breakupChart.render();

        // Rendering the Earning chart with example data
        var earningChart = {
            chart: {
                id: "sparkline3",
                type: "area",
                height: 60,
                sparkline: {
                    enabled: true,
                },
                group: "sparklines",
                fontFamily: "Plus Jakarta Sans', sans-serif",
                foreColor: "#adb0bb",
            },
            series: [
                {
                    name: "Earnings",
                    color: "#49BEFF",
                    data: [25, 66, 20, 40, 12, 58, 20],
                },
            ],
            stroke: {
                curve: "smooth",
                width: 2,
            },
            fill: {
                colors: ["#f3feff"],
                type: "solid",
                opacity: 0.05,
            },
            markers: {
                size: 0,
            },
            tooltip: {
                theme: "dark",
                fixed: {
                    enabled: true,
                    position: "right",
                },
                x: {
                    show: false,
                },
            },
        };

        var earningChart = new ApexCharts(document.querySelector("#earning"), earningChart);
        earningChart.render();
    }

    // Fetch property data and render charts when the page loads
    getPropertyData();
});
