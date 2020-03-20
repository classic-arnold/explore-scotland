$('document').ready(function(){
	$('form').addClass('form-group');
	$('input').addClass('form-control');
	
	$('input[type="submit"]').removeClass('form-control');
	$('input[type="submit"]').addClass('btn btn-primary');
	
	$('input[type="file"]').addClass('p-1');
	$('input[type="button"]').addClass('btn btn-primary');
	
	$("input[type=file]").change(function() {
	  readURL(this);
	});
});

function confirm_delete() {
  return confirm('Are you sure?');
}

function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    
    reader.onload = function(e) {
      $('#img_preview').attr('src', e.target.result);
    }
    
    reader.readAsDataURL(input.files[0]);
  }
}