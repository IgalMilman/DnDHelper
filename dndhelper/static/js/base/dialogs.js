function confirmDial(title, message, callback, parameters) {
    // create your modal template    
    var modal = '<div class="reveal small" id="confirmation">' +
        '<h4>' + title + '</h4>' +
        '<p class="lead">' + message + '</p>' +
        '<button class="button success yes">Yes</button>' +
        '<button class="button alert float-right" data-close>No</button>' +
        '</div>';
    // appending new reveal modal to the page
    $('body').append(modal);
    // registergin this modal DOM as Foundation reveal    
    var confirmation = new Foundation.Reveal($('#confirmation'));
    // open
    confirmation.open();
    // listening for yes click

    $('#confirmation').children('.yes').on('click', function() {
        // close and REMOVE FROM DOM to avoid multiple binding
        confirmation.close();
        $('#confirmation').remove();
        // calling the function to process
        callback(parameters);
    });
    $(document).on('closed.zf.reveal', '#confirmation', function() {
        // remove from dom when closed
        $('#confirmation').remove();
    });

}

function modalTextDial(title, message, buttonClassNames = 'success') {
    // create your modal template    
    var modal = '<div class="reveal small" id="modaltext">' +
        '<h2>' + title + '</h2>' +
        '<p class="lead">' + message + '</p>' +
        '<button class="button OK ' + buttonClassNames + '">OK</button>' +
        '</div>';
    // appending new reveal modal to the page
    $('body').append(modal);
    // registergin this modal DOM as Foundation reveal    
    var modaltext = new Foundation.Reveal($('#modaltext'));
    // open
    modaltext.open();
    // listening for yes click

    $('#modaltext').children('.OK').on('click', function() {
        // close and REMOVE FROM DOM to avoid multiple binding
        modaltext.close();
        $('#modaltext').remove();
    });
    $(document).on('closed.zf.reveal', '#modaltext', function() {
        // remove from dom when closed
        $('#modaltext').remove();
    });

}