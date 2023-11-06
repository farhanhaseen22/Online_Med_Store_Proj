
// Inserting an item in the cart //

$('.update_cart').click(function(e){
	e.preventDefault() 
	var item_quantity = $("#item_quantity").val();
	
	if( !parseInt(item_quantity) ) {
		$('#modalBody').text("Have to select a Valid Quantity")
	}
	else {
		item_quantity = parseInt(item_quantity);
		// console.log(item_quantity)
	
		if(item_quantity < 1 || item_quantity > 9 ) {
			$('#modalBody').text("Select a quantity from 1 to 9")
		}
		else {
			var product_id = $(this).attr("product_id");
			$.ajax(
			{ 
				type:"POST", 
				url: "http://127.0.0.1:8000/insert_cart/",
				data:{ 
						'product_id' : product_id,
						'item_quantity' : item_quantity.toString(),
						'csrfmiddlewaretoken' : '{{ csrf_token }}',
				},
				dataType : 'json', 
				success: function(response) 
				{
					console.log(`Cart: ${response['total_item_cart']}`);
					$('#modalBody').text(`Added this item ${item_quantity} times to Cart`);
					$('#cart-total').text(response['total_item_cart']);
				}
			})
		}
	}
});

// Update the quantity of an item in cart //

$('.update_cart_quantity').click(function(e){ 
	e.preventDefault()
	var product_id = $(this).attr("product_id");
	var action = $(this).attr("action")
	console.log(product_id)
	
	$.ajax( 
	{ 
	    type:"POST", 
	    url: 'http://127.0.0.1:8000/cart/update_item/',
	    data:{ 
	      		'product_id' : product_id,
	      		'action' : action,
	      		'csrfmiddlewaretoken' : '{{ csrf_token }}',
		},
		dataType : 'json', 
		success: function(response) 
		{ 	
			window.location.reload();
		}  
	}) 
});

// Adding an item to Favourites //

$('.add_to_favs').click(function(e){
	e.preventDefault() 
	var product_id = $(this).attr("product_id");

	$.ajax( 
	{ 
	    type:"POST", 
	    url: "http://127.0.0.1:8000/add_to_favs/",
	    data:{ 
	      		'product_id' : product_id,
	      		'csrfmiddlewaretoken' : '{{ csrf_token }}',
		},
		dataType : 'json', 
		success: function(response) 
		{ 	
			console.log(response['message']);
			$('#modalBody').text(response['message']);
		}	  
	}) 
});

$('#modalCloseButton').click(function(e){
	window.location.reload();
});

// Both adding a rating to an item //
// And updating the rating of an item //

$('.rating_submit_btn').click(function(e){
	e.preventDefault() 
	var product_id = $(this).attr("product_id");
	// var selected_rating = document.getElementsByClassName("select-selected")[0].innerHTML;
	var selected_rating = $(".select-selected").text();
	// console.log("Selected_rating=",selected_rating)

	if( !parseInt(selected_rating) ) {
		$('#modalBody').text("Have to select a Valid Rating Score!")
	}
	else {
		$.ajax(
		{ 
			type:"POST", 
			url: "http://127.0.0.1:8000/update_rating/",
			data:{ 
						'product_id' : product_id,
						'selected_rating' : selected_rating,
						'csrfmiddlewaretoken' : '{{ csrf_token }}',
			},
			dataType : 'json',
			success: function(response)
			{
				if(response === 1) window.location.reload();
			}
		})
	}
});



// Sticky Navbar //

document.addEventListener("DOMContentLoaded", function(){
	window.addEventListener('scroll', function() {
		if (window.scrollY > 50) {
			document.getElementById('navbar_top').classList.add('fixed-top');
			// add padding top to show content behind navbar
			navbar_height = document.querySelector('.navbar').offsetHeight;
			document.body.style.paddingTop = navbar_height + 'px';
		} else {
			document.getElementById('navbar_top').classList.remove('fixed-top');
			// remove padding top from body
			document.body.style.paddingTop = '0';
		} 
	});
}); 



// let navbar = document.getElementById("navigation");
// let shouldStickPosition = navbar.offsetTop;

// function addOrRemoveStickyClass() {
// 	// if (window.pageYOffset >= shouldStickPosition) {
// 	if (window.scrollY >= shouldStickPosition) {
// 		navbar.classList.add("sticky");
// 	}
// 	else {
// 		navbar.classList.remove("sticky");
// 	}
// }

// window.onscroll = () => {
// 	addOrRemoveStickyClass();
// };

// window.onresize = () => {
// 	shouldStickPosition = navbar.offsetTop;
// };

///////////////////////
