document.addEventListener('DOMContentLoaded', function () {
    // Dane JSON
    const monthlyData = JSON.parse('{{ monthly_data|escapejs|safe }}');

    // Dane do wykresu
    const labels = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];
    let incomeData = monthlyData.map(data => data.income);
    let expenseData = monthlyData.map(data => data.expense);
    let balanceData = monthlyData.map(data => data.balance);

    // Konfiguracja wykresu
    const ctx = document.getElementById('budgetChart').getContext('2d');
    let budgetChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Dochody',
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                data: incomeData
            }, {
                label: 'Wydatki',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                data: expenseData
            }, {
                label: 'Stan konta',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                data: balanceData
            }]
        },
        options: {
            indexAxis: 'x',
            group: {
                groupWidth: 0.8
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const yearSelect = document.getElementById('yearSelect');
    yearSelect.addEventListener('change', function() {
        const selectedYear = yearSelect.value;
        // Załaduje dane dla wybranego roku
        fetch(`/data?year=${selectedYear}`)
            .then(response => response.json())
            .then(data => {
                incomeData = data.map(data => data.income);
                expenseData = data.map(data => data.expense);
                balanceData = data.map(data => data.balance);
                // Zaktualizuje dane na wykresie
                budgetChart.data.datasets[0].data = incomeData;
                budgetChart.data.datasets[1].data = expenseData;
                budgetChart.data.datasets[2].data = balanceData;
                budgetChart.update();
            });
    });
});
