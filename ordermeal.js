function inventory(orders) {
	num_orders = orders.length;
	tot_amount_1 = parseInt(orders[0].totalAmount["N"]);
	var totalOptionOne = 0;
	var totalOptionTwo = 0;
	for (i = 0; i < num_orders; i++) { 
			totalOptionOne += parseInt(orders[i].mealOption1["N"]);
 			totalOptionTwo += parseInt(orders[i].mealOption2["N"]);
	}
	document.getElementById("num_orders").innerHTML = num_orders + " Orders Today:"
	console.log(totalOptionOne + " Quantities of mealOption1");
	console.log(totalOptionTwo + " Quantities of mealOption2");
	document.getElementById("num_daal").innerHTML =(totalOptionOne + totalOptionTwo) + " Servings of Dal";
	document.getElementById("num_bhaji").innerHTML = (totalOptionOne + totalOptionTwo) + " Servings of Bhaji";
	document.getElementById("num_chapati").innerHTML = ((totalOptionOne * 2) + (totalOptionTwo * 4)) + " Servings of Chapati";
	document.getElementById("num_rice").innerHTML = (totalOptionOne * 2) + " Servings of Rice";
}

function delivery(orders) {
	var num_orders = orders.length;
	var order_info = "";
	for (i = 0; i < num_orders; i++) {
		// name
		order_info += orders[i].name['S'] + "<br>";
		//street address
		order_info += orders[i].street['S'] + "<br>";
		//city/zip
		order_info += orders[i].city['S'] + " " + orders[i].zipCode['N'] + "<br>";
		var payment = "";
		if (orders[i].paid["BOOL"] == false) {
			payment = "Unpaid, owes $" + orders[i].totalAmount['N'];
		}
		else {
			payment = "Paid $" + orders[i].totalAmount['N'];
		}
		order_info += orders[i].deliveryTime["S"] + " Delivery<br>";
		order_info += payment + "<br>";

		one = parseInt(orders[i].mealOption1["N"])
		two = parseInt(orders[i].mealOption2["N"])

		var rder = (one + two) + " daal & bhaji servings<br>" + ((one * 2) + (two * 4)) + " chapatis<br>" + one + " rice servings";
		order_info += rder + "<br><br>";

		//document.getElementById("delivery").innerHTML = orders[i].name['S'] + "<br>" + orders[i].street['S'] + "<br>" + orders[i].city['S'] + " " + orders[i].zipCode['N'] + "<br><br>" + payment + rder;
	}
	document.getElementById("delivery").innerHTML = order_info;
}

$(document).ready(function(){
	const Url = 'https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/api/v1/meal/order';
	$.ajax({
		url: Url,
		type: "GET",
		datatype: 'json',
		success: function(res) {
			orders = res["result"];
			inventory(orders);
			delivery(orders);
		},
		error: function(error) {
			console.log("Error ${error}")
		}
	})
})