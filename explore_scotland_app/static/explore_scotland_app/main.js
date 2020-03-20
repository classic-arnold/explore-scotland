$('document').ready(function(){
	$('form').addClass('form-group');
	$('input').addClass('form-control');
	
	$('input[type="submit"]').removeClass('form-control');
	$('input[type="submit"]').addClass('btn btn-primary');
	
	$('input[type="file"]').addClass('p-1');
	$('input[type="button"]').addClass('btn btn-primary');
});

function confirm_delete() {
  return confirm('Are you sure?');
}