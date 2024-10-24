// JavaScript for Employee List Table

// Variable to track the current column and order
let currentSortColumn = -1;
let isAscending = true;

// Function to sort the table
function sortTable(columnIndex) {
    let table = document.getElementById("empleadosTable");
    let rows = Array.from(table.rows).slice(2); // Ignore header and filter rows
    let shouldSwitch;
    let i;
    let x, y;

    // Toggle ascending/descending order
    if (currentSortColumn === columnIndex) {
        isAscending = !isAscending;
    } else {
        isAscending = true;
        currentSortColumn = columnIndex;
    }

    // Sort rows
    rows.sort(function (a, b) {
        x = a.getElementsByTagName("td")[columnIndex].innerText.toLowerCase();
        y = b.getElementsByTagName("td")[columnIndex].innerText.toLowerCase();

        if (!isNaN(x) && !isNaN(y)) { // Compare as numbers if applicable
            x = parseFloat(x);
            y = parseFloat(y);
        }

        if (isAscending) {
            return x > y ? 1 : -1;
        } else {
            return x < y ? 1 : -1;
        }
    });

    // Insert sorted rows back into the table
    for (i = 0; i < rows.length; i++) {
        table.tBodies[0].appendChild(rows[i]);
    }

    // Update sort icons
    updateSortIcons(columnIndex);
}

// Update sorting icons in the headers
function updateSortIcons(columnIndex) {
    let headers = document.querySelectorAll(".sort-icon");
    headers.forEach((header, index) => {
        header.classList.remove("ascending", "descending");
        if (index === columnIndex) {
            header.classList.add(isAscending ? "ascending" : "descending");
        }
    });
}

// Assign events to filter inputs
document.getElementById('filterID').addEventListener('keyup', function () { filterTable('filterID', 0); });
document.getElementById('filterName').addEventListener('keyup', function () { filterTable('filterName', 1); });
document.getElementById('filterCheckin').addEventListener('keyup', function () { filterTable('filterCheckin', 2); });
document.getElementById('filterCheckout').addEventListener('keyup', function () { filterTable('filterCheckout', 3); });
document.getElementById('filterHours').addEventListener('keyup', function () { filterTable('filterHours', 4); });

// Filtering function
function filterTable(inputId, columnIndex) {
    let input = document.getElementById(inputId);
    let filter = input.value.toUpperCase();
    let table = document.getElementById("empleadosTable");
    let tr = table.getElementsByTagName("tr");

    for (let i = 2; i < tr.length; i++) { // Ignore header and filter row
        let td = tr[i].getElementsByTagName("td")[columnIndex];
        if (td) {
            let txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
