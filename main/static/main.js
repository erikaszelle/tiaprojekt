$(document).ready(function () {
	console.log("jQuery: READY");

	$("#loginButton").click(function () {
		console.log("login button clicked");
		$(".modal-header > h4").html("Login");

		$.get('/login/', function(data){
			console.log("login form:" + data);
			$('.modal-body').html(data);
		})
	});

	$("#logoutButton").click(function () {
		console.log("logout button clicked");
		$(".modal-header > h4").html("Logout");

		$.get('/logout/', function(data){
			console.log("login form:" + data);
			$('.modal-body').html(data);
		})
	});

	$("#registerButton").click(function () {
		$(".modal-header > h4").html("Register");

		$.get('/register/', function(data){
			$('.modal-body').html(data);
		})
	});

	$("#myModal .close").click(function () {
		console.log("modal closed.");
		location.href = location.localhost;
		location.reload(true);
	});

	$("#newCategoryButton").click(function () {
		console.log("add category button clicked");
		$(".modal-header > h4").html("Add category");

		$.get('/category/add/', function(data){
			console.log("add category form:" + data);
			$('.modal-body').html(data);
		})
	});

	$("#addUrlButton").click(function () {
		console.log("add site button clicked");
		$(".modal-header > h4").html("Add new site");

		$.get('/url/add/', function(data){
			console.log("add url form:" + data);
			$('.modal-body').html(data);
		})
	});
});
