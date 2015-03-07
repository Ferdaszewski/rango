$(document).ready( function() {

  $("#about-btn").click( function(event) {
    alert("You clicked the button using JQuery!");
  });

  $(".ouch").click( function() {
    alert("You clicked me! ouch!");
  });

  // $("p").hover( function() {
  //   $(this).css('color', 'red');
  // },
  // function() {
  //   $(this).css('color', 'blue');
  // });

  $("#about-btn").addClass('btn btn-primary');

  $("#about-btn").click( function(event) {
    msgstr = $("#msg").html()
    msgstr = msgstr + 'o'
    $("#msg").html(msgstr)
  });
});