tumblr_callback = function(data) {
    $('#blog-panel .loading').remove();
    $.each(data.posts, function(_, post){
        $('<div class="tumblr_post"><div class="tumblr_title"><a href="' + post['url-with-slug'] + '#disqus_thread">' + post['regular-title'] + '</a></div>' +
            '<div class="tumblr_body">' + post['regular-body'] + '</div></div>').appendTo('#blog-panel');
    });
};
$(function(){
    $.ajax({
        dataType: 'script',
        method: 'GET',
        url: 'http://blog.disqus.com/api/read/json?tagged=dev&callback=tumblr_callback',
        error: function(){
            $('#blog-panel').text('There was an error loading the recent blog posts. Tumblr :(')
        }
    });
});