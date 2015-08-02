var req;
var req_send_comment;

function sendComment(post_id, new_comment, username, num_of_comments) {
    if (window.XMLHttpRequest) {
        req_send_comment = new XMLHttpRequest();
    } else {
        req_send_comment = new ActiveXObject("Microsoft.XMLHTTP");
    }
	// Update the serverside data
	// First get csrf_token...
	var csrf_token = $( "input[name='csrfmiddlewaretoken']" )
	$.ajax({
		method: "POST",
		url: "/CoDEX/design_market/add_comment",
		data: {post_id: post_id,
				comment: new_comment,
				username: username,
				csrfmiddlewaretoken: csrf_token[0].value,
				}
	}).done(function() {
		retrieveComments(post_id, num_of_comments);
	});
}

function retrieveComments(post_id, last_comment_id) {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
	// Retrive data from server, and update after data is ready

	var csrf_token = $( "input[name='csrfmiddlewaretoken']" )
	$.ajax({
		method: "POST",
		url: "/CoDEX/design_market/update_comment",
		data: {post_id: post_id,
				last_comment_id: last_comment_id,
				csrfmiddlewaretoken: csrf_token[0].value,
				},
		dataType: "json",
	}).done(function(data) {
		updateComments(data);
	});
}

// updateComments is equivalent to handleResponse... Defined as another function 
// simply because I can't call handleResponse while the setIntervel is still functioning
function updateComments(data){ 
	// Parses the response to get a list of JavaScript objects for 
	// the comments to update.
	var comments_to_update = data // JSON && JSON.parse(data) || $.parseJSON(data);

   
	// Check for new post and append new post
	for (var i = 0; i < comments_to_update.length; i++) {
		//console.log($("tr.post_text"));
		//console.log(comments_to_update.length);
		// Extracts the item id and text from the response
		var new_comment = comments_to_update[i]["text"];
		var id = comments_to_update[i]["id"];
		var user_id = comments_to_update[i]["user"];  
		var username = comments_to_update[i]["username"];
		var date_posted = comments_to_update[i]["date_posted"];
		var profile_image = comments_to_update[i]["profile_image"];

		if (new_comment) {
			// Builds a new HTML list item for the todo-list item
			var comment_row = document.createElement("div");
			var comment_text = document.createElement("div");
			comment_row.className = "row";
			comment_row.setAttribute('id', "comment"+id);
			comment_row.setAttribute('name', "comment-entry");
			comment_text.className = "col-md-10";

			comment_row.innerHTML = '<div class="col-md-1"></div>'
			var userinfo = "";
			if (profile_image != 0) {
				userinfo = '<a href="/CoDEX/profile/' + user_id +'"><img src="/CoDEX/photo/' + user_id +'" alt="140x140" class="profileimg-small">' + username + "</a>"
			}
			else {
				if (user_id) {
					userinfo = '<a href="/CoDEX/profile/' + user_id +'"><img src="/static/images/default.jpg" alt="140x140" class="profileimg-small">' + username + "</a>"
				}
				else
				{
					userinfo = '<img src="/static/images/default.jpg" alt="140x140" class="profileimg-small">' + '<p class="inline-center">' + username + '(Guest) :</p>'
				}
				
			}

			text = '<p class="comment-text">' + new_comment + '</p>' + '<p class="comment-date">@' + date_posted + '</p>'
			comment_text.innerHTML = userinfo + text;


			// Adds the todo-list item to the HTML list
			$("#comment_section").prepend(comment_row);
			$("div[id='comment"+id+"']").append(comment_text);
			manageHandle();
		}
	}
}

function manageHandle(){
$("button[name|='comment-btn']").off();
$("button[name|='comment-btn']").on( "click", function( event ) {
	event.preventDefault();
    var button = $( this );
	post_id = $("input[name='post_id']")[0].value;
    new_comment = $("textarea[id='id_text']").val();
    num_of_comments = $("div[name='comment-entry']").length;
    username = $("input[name='username']").val();
	if (new_comment.length > 300) {
		alert("The comment should not exceed 300 chars!");
	}
	else {
		sendComment(post_id, new_comment, username, num_of_comments);
	}
});
}

manageHandle()