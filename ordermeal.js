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

$(document).ready(function(){
	const Url = 'https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/api/v1/meal/order';
	$.ajax({
		url: Url,
		type: "GET",
		datatype: 'json',
		success: function(res) {
			orders = res["result"];
			inventory(orders);
		},
		error: function(error) {
			console.log("Error ${error}")
		}
	})
})