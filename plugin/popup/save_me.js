
//console.log("pop up js called");
$("h4").html("Add new site");

console.log("Now we will send a request...");

var xhr = new XMLHttpRequest();

xhr.onreadystatechange = function(){
	if (xhr.readyState == 4) {

		var s1 = xhr.responseText;

		if (s1.indexOf("<button") < 0)
		{
			document.getElementById("content1").innerHTML = "Please visit our page and login.";
			document.getElementById("content2").innerHTML = "";
			document.getElementById("content3").innerHTML = "";
		}
		else
		{

			var s2;
			s1 = s1.substring(0, s1.indexOf("<button"));
			s2 = xhr.responseText.substring(xhr.responseText.indexOf("</button>") + "</button>".length, xhr.responseText.length);

			console.log("Received response: " + xhr.responseText);

			console.log("We got: " + s1);
			console.log("We got: " + s2);

			document.getElementById("content1").innerHTML = s1;
			document.getElementById("content3").innerHTML = s2;

			browser.tabs.query({'active': true, 'currentWindow': true}, function (tabs) {
				document.getElementById("id_url").value = tabs[0].url;
				document.getElementById("id_url_title").value = tabs[0].title;
			});


		}
	}
	else {
		console.log("Received response, readyState: " + xhr.readyState);
	}
}
xhr.withCredentials = true;
xhr.open("GET", "http://127.0.0.1:8000/url/add/");
xhr.send();


document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('formSubmit');
    
	btn.addEventListener('click', function() {
        sendPost();
    });
});

function sendPost(){
	console.log("CLICK!!!");
	var xhr2 = new XMLHttpRequest();

	xhr2.open("POST", "http://127.0.0.1:8000/url/add/", true);
	//Send the proper header information along with the request
	xhr2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	
	xhr2.onreadystatechange = function(){
		if (xhr2.readyState == 4) {
			
			var s1 = xhr2.responseText;

			if (s1.indexOf("<button") < 0)
			{
				document.getElementById("content1").innerHTML = xhr2.responseText;
				document.getElementById("content2").innerHTML = "";
				document.getElementById("content3").innerHTML = "";
			}
			else
			{
				document.getElementById("content1").innerHTML = "Site could not be added.";
				document.getElementById("content2").innerHTML = "";
				document.getElementById("content3").innerHTML = "";
			}

		}
		else {
			console.log("Received response, readyState: " + xhr2.readyState);
		}
	}

	xhr2.send($("#form").serialize());
}

