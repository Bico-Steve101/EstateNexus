// Event listeners for dropdown menu items
document.querySelectorAll('.dropdown-item').forEach(function(item) {
    item.addEventListener('click', function(event) {
        event.preventDefault();
        var action = this.textContent;
        var row = this.closest('tr');

        switch (action) {
            case 'Mark':
            case 'Unmark':
                // Toggle the marking of the row
                if (row.style.backgroundColor === '#3898EC') {
                    row.style.backgroundColor = ''; // Unmark the row
                    this.textContent = 'Mark'; // Change the item text to 'Mark'
                } else {
                    row.style.backgroundColor = 'blue'; // Mark the row
                    this.textContent = 'Unmark'; // Change the item text to 'Unmark'
                }
                break;
            case 'Export':
                // Export the row to Excel
                var newTable = document.createElement('table');
                var newBody = document.createElement('tbody');
                var clonedRow = row.cloneNode(true);
                clonedRow.removeChild(clonedRow.lastElementChild); // Remove the last cell (dropdown menu)
                newBody.appendChild(clonedRow);
                var newHead = document.querySelector('thead').cloneNode(true);
                newHead.querySelector('th:last-child').remove(); // Remove the last header cell ("Action")
                newTable.appendChild(newHead);
                newTable.appendChild(newBody);

                // Convert the new table to Excel
                var wb = XLSX.utils.table_to_book(newTable);
                XLSX.writeFile(wb, "data.xlsx");

                // Show success message
                alert('Row has been exported successfully!');
                break;
            case 'Message':
                // Add your code for the 'Message' action here
                break;
        }
    });
});
