
window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

setTimeout(function() {
document.getElementById("flash").style.display = "none";
}, 3500);


$(document).ready(function() {
  $('#current_r').keyup(function() {
    if ($(this).val() == $('#current_p').val()) {
      $('#current_check').show();
    } else {
      $('#current_check').hide();
    }
  });
});

$(document).ready(function() {
  $('#new_r').keyup(function() {
    if ($(this).val() == $('#new_p').val()) {
      $('#new_check').show();
    } else {
      $('#new_check').hide();
    }
  });
});



