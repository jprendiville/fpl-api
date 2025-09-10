function GreenYellowRed(value) {
    var r, g, b;

    // as the function expects a value between 0 and 1, and red = 0° and green = 120°
    // we convert the input to the appropriate hue value
    var hue = value * 1.2 / 360;
    // we convert hsl to rgb (saturation 100%, lightness 50%)
    var rgb = hslToRgb(hue, 1, .5);
    // we format to css value and return
    return rgb[0] + ',' + rgb[1] + ',' + rgb[2];

}

var colorTDs = $('.valueTD');
var hidden_easiest = $('.hidden_easiest');
var hidden_hardest = $('.hidden_hardest');

$.each(colorTDs, function (index, colorTD) {

    var values = colorTD.getAttribute("value").split(',')
    var fdr_value = parseInt(values[0]) || 0
    var fdr_color = parseInt(values[1]) || 0
    var easiest = hidden_easiest.text();
    var hardest = hidden_hardest.text();

    // Is this a blank gameweek?
    if (fdr_color == 0) {
        $(colorTD).css('background-color', "rgb(0,0,0)");
        return;
    }
    // Is this a multiple gameweek?
    if (fdr_color == 999) {
        $(colorTD).css('background-color', "rgb(0,255,255)");
        colorTD.innerText += ' - ' + fdr_value;
        return;
    }

    // convert the value to 1 to 100
    var fdr_color = (1 - ((fdr_color - easiest) / (hardest - easiest))) * 100

    if (!isNaN(fdr_color)) {
        // if value is not 0 get the RBG, otherwise set it to Black (0,0,0)
        var color = GreenYellowRed(fdr_color);

        $(colorTD).css('background-color', "rgb(" + color + ")");
    }
});


function hslToRgb(h, s, l) {
    var r, g, b;

    if (s == 0) {
        r = g = b = l; // achromatic
    } else {
        var hue2rgb = function hue2rgb(p, q, t) {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1 / 6) return p + (q - p) * 6 * t;
            if (t < 1 / 2) return q;
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
            return p;
        }

        var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        var p = 2 * l - q;
        r = hue2rgb(p, q, h + 1 / 3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1 / 3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

$(function () {

    if ($("#login-btn").length) {
        $("#login-btn").modalForm({
            modalID: "#modal-auth",
            formURL: "login"
        });
    }

    // Display Player History
    function playerHistoryModalForm() {
        // Check if there are any .custom-button elements
        if ($(".custom-button").length) {
            $(".custom-button").each(function () {
                if ($(this).data("form-url")) {
                    $(this).modalForm({ formURL: $(this).data("form-url") });
                }
            });
        }
    }

    function playerPredictionHistoryModalForm() {
        if ($(".player-prediction-history").length) {
            $(".player-prediction-history").each(function () {
                if ($(this).data("form-url")) {
                    $(this).modalForm({formURL: $(this).data("form-url")});
                }
            });
        }
    }

    playerHistoryModalForm();
    playerPredictionHistoryModalForm();

    function reinstantiateModalForms() {
        playerHistoryModalForm();
        playerPredictionHistoryModalForm();
    }

    $('td').click(function () {
        $(this).toggleClass('highlight');
    });

    $('tr').click(function () {
        $(this).toggleClass('highlight');
    });

    // Hide message
    $(".alert").fadeTo(2000, 500).slideUp(500, function () {
        $(".alert").slideUp(500);
    });

});


$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

document.addEventListener('DOMContentLoaded', function () {
    // Safely get the gameweek and date input elements
    var gameweekSelect = document.getElementById('id_gameweek');
    var dateInput = document.getElementById('id_event_date');
    var hiddenField = document.getElementById('id_last_field_changed');

    // Function to update hidden field and reset other field
    function updateFieldChanged(field) {
        if (hiddenField) {  // Ensure hiddenField exists
            hiddenField.value = field;  // Update the hidden field value
        }

        if (field === 'gameweek' && dateInput) {
            dateInput.value = '';  // Clear the date input if gameweek is selected
        } else if (field === 'event_date' && gameweekSelect) {
            if (gameweekSelect.options.length > 0) {
                gameweekSelect.selectedIndex = 0;  // Reset gameweek to the first option (if it exists)
            }
        }

        document.forms['elementForm'].submit();  // Submit the form
    }

    // Bind onchange events to gameweek and event_date fields if they exist
    if (gameweekSelect) {
        gameweekSelect.onchange = function () {
            updateFieldChanged('gameweek');
        };
    }

    if (dateInput) {
        dateInput.onchange = function () {
            updateFieldChanged('event_date');
        };
    }
});


document.addEventListener('DOMContentLoaded', function () {
    var rows = document.querySelectorAll('.clickable-row');
    rows.forEach(function (row) {
        row.addEventListener('click', function () {
            // Find the icon within the same row that was clicked
            var icon = this.querySelector('.chevron-icon');

            if (icon) {
                // Toggle the icon direction based on the current state
                if (icon.classList.contains('bi-chevron-down')) {
                    icon.classList.remove('bi-chevron-down');
                    icon.classList.add('bi-chevron-up');
                } else {
                    icon.classList.remove('bi-chevron-up');
                    icon.classList.add('bi-chevron-down');
                }
            }
        });
    });
});