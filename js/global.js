$(document).ready(function(){
    DISQUS.ready(function(){
        // we need to construct one request per forum
        var requests = {};
        $('#post-list .post').each(function(){
            var forum = $(this).attr('data-forum');
            var url = $(this).attr('data-link');
            if (!requests[forum]) {
                requests[forum] = [url];
            } else {
                requests[forum].push(url);
            }
        });
        $.each(requests, function(forum, url_list){
            DISQUS.sexyapi.threads.list({
                data: {
                    forum: forum,
                    'thread:link': url_list
                },
                success: function(data){
                    $.each(data, function(_, thread){
                        $('#post-list .post[data-link=' + thread.link + '] .dsq-comment-count').text(thread.posts + ' comment' + (thread.posts != 1 ? 's' : '') + ' and ' + thread.reactions + ' reaction' + (thread.reactions != 1 ? 's' : ''));
                    });
                }
            });
        });
    });
});