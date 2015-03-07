$(document).ready( function() {

  // Load category list when page first loads
  get_categories()
  
  // Category like button click
  $('#likes').click( function() {
    var catid = $(this).data("catid");
    $.get('/rango/like_category/', {category_id: catid}, function(data) {
      $('#likes_count').html(data);
      $('#likes').hide();
    });
  });

  // Auto update side nav category search results
  $('#suggestion').keyup( get_categories );

  function get_categories() {
    var query = $('#suggestion').val();
    $.get('/rango/suggest_category/', {suggestion: query}, function (data) {
      $('#cats').html(data);
    });   
  }

  // Auto add page from search to category
  $('.rango-add').click( function(e) {
    var cat_id = $(this).data("catid");
    var title = $(this).data("title");
    var url = $(this).data("url");
    var button = e.target
    $.get('/rango/auto_add_page/', {'cat_id': cat_id, 'title': title, 'url': url}, function (data) {
      // Factor out page display in categories, update page list with new page.
      // disable button and change it's text
      $(button).html('Added');
      $(button).attr('disabled', 'disabled');
    });
  });

});