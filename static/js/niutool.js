function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
function watchNode(event) {
    event.preventDefault();
    $.ajax({
        url: $(this).attr('href'),
        type: "post",
        data: {csrfmiddlewaretoken : getCookie('csrftoken'),
                watch : $(this).attr('data-watch')},

        success : function(json){
            if(json.code == 0) {
                var watching = json.ret.watching;
                var icon = $('#watch');

                icon.attr('data-watch', watching);
                if(watching == true) {
                    icon.attr("class","niu-link active");
                } else {
                    icon.attr("class","niu-link");
                }
            }
        },

        error: function(xhr, errmsg, err){
            console.log(xhr.status + ": " + xhr.responseText); 
        }
    });
};
function likeTopic(event) {
    event.preventDefault();
    $.ajax({
        url: $(this).attr('href'),
        type: "post",
        data: {csrfmiddlewaretoken : getCookie('csrftoken'),
                like : $(this).attr('data-like')},

        success : function(json){
            if(json.code == 0) {
                var ilike = json.ret.ilike;
                var icon = $('#like');

                icon.attr('data-like', ilike);
                if(ilike == true) {
                    icon.attr("class","niu-link active");
                } else {
                    icon.attr("class","niu-link");
                }
            }
        },

        error: function(xhr, errmsg, err){
            console.log(xhr.status + ": " + xhr.responseText); 
        }
    });
};
function renderMarkdown(markdown) {
    $.ajax({
        url: "/action/render/",
        type: "post",
        data: {csrfmiddlewaretoken : getCookie('csrftoken'),
                md : markdown},

        success : function(json){
            if(json.code == 0) {
                var rendered = json.ret.rendered;
                var preview = $('.preview-panel');
                var article = $("<article/>", {class: "markdown"});
                article.append(rendered);
                preview.empty();
                preview.append(article);
            }
        },

        error: function(xhr, errmsg, err){
            console.log(xhr.status + ": " + xhr.responseText); 
        }
    });
};
function addEditorAction() {
    $('button[data-toggle="menu"]').on("click", function () {
        var textarea = $('#write>textarea')[0];
        var action = $(this).attr('aria-controls');
    });

    $('#write>textarea').on("focus", function() {
        $('div.md-editor').attr("class", "md-editor active");
    });
    
    $('#write>textarea').on("blur", function() {
        $('div.md-editor').attr("class", "md-editor");
    });

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target);
        if (target.attr('aria-controls') == "write") {
            $('div.md-editor').attr("class", "md-editor active");
        } else {
            $('div.md-editor').attr("class", "md-editor");
            renderMarkdown($('#write>textarea').val());
        }
    });
};
function replySomeone(event) {
    event.preventDefault();
    var user = $(this).attr('data-user');
    var txtarea = event.data.txtarea;
    
    var content = txtarea.val();
    if(content) {
        txtarea.val(txtarea.val() + '\n@'+user+' ');
    } else {
        txtarea.val(txtarea.val() + '@'+user+' ');
    }
    
    txtarea.focus();
};

