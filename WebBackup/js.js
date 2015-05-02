$(document).ready(function () {
    var table = $('#table1').dataTable({
        "columns": [
            {"data": "Image"},
            {"data": "Top1"},
            {"data": "Right1"},
            {"data": "wnid1"},
            {"data": "Top2"},
            {"data": "Right2"},
            {"data": "wnid2"},
            {"data": "Top3"},
            {"data": "Right3"},
            {"data": "wnid3"},
            {"data": "Top4"},
            {"data": "Right4"},
            {"data": "wnid4"},
            {"data": "Top5"},
            {"data": "Right5"},
            {"data": "wnid5"},
        ]
    });

    $.getJSON("logIndex.txt", function (json) {
        var yourSelect = document.getElementById("sel");
        $(json).each(function (index, o) {
            var $option = $("<option/>").text(o.name);
            $(yourSelect).append($option);
        });

    });
});

function addCell(tableID, txt) {

    // Get a reference to the tableRow
    var rowRef = document.getElementById(tableID);

    // Insert a cell in the row at cell index 0
    var newCell = rowRef.insertCell();

    // Append a text node to the cell
    var newText = document.createTextNode(txt);
    newCell.appendChild(newText);
}


$("button").click(function () {
    var yourSelect = document.getElementById("sel");

    $.getJSON("AnalizeLogs/" + yourSelect.options[yourSelect.selectedIndex].value, function (json) {
        d1 = json;
        $('#table1').dataTable().fnClearTable();
        $('#table1').dataTable().fnAddData(d1.data);
        $('#table1').dataTable().fnDraw();
    });


    $.getJSON("confusionLogs/" + yourSelect.options[yourSelect.selectedIndex].value, function (json2) {

        d2 = json2;
        addCell("row0", "-");
        for (var i = 0; i < d2.data.length; i++) {
            addCell("row0", d2.data[i]["-"]);
        }
        for (var i = 0; i < d2.data.length; i++) {

            var tableRef = tableRef = document.getElementById("table2");
            var newRow = tableRef.insertRow();
            var newCell = newRow.insertCell();
            var newText = document.createTextNode(d2.data[i]["-"]);
            newCell.appendChild(newText);
            for (var j = 0; j < d2.data.length; j++) {
                var newCell = newRow.insertCell();
                var newText = document.createTextNode(d2.data[j][d2.data[i]["-"]]);
                newCell.appendChild(newText);
            }
        }

    });

});

