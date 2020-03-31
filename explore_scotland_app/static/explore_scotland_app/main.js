$('document').ready(function(){
	$('form').addClass('form-group');
	$('input').addClass('form-control');
	
	$('input[type="submit"]').removeClass('form-control');
	$('input[type="submit"]').addClass('btn btn-primary');
	
	$('input[type="file"]').addClass('p-1');
	$('input[type="button"]').addClass('btn btn-primary');
	
	var prev_img = '<img src="#" id="img_preview" width="60px" height="auto" alt="" class="mt-3"/>';
	
	$("input[type=file]").after(prev_img);
	
	$("input[type=file]").change(function() {
	  readImageURL(this);
	});
	
	if($('title').html().includes("About")){
		$("#about").addClass('mb-5');
	}
	
	if( ($('#message_modal').find('.modal-body').children().length > 0 ) ){
		$('#message_modal').modal('show');
	}
});

function confirm_delete() {
  return confirm('Are you sure?');
}

function readImageURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    
    reader.onload = function(e) {
      $('#img_preview').attr('src', e.target.result);
    }
    
    reader.readAsDataURL(input.files[0]);
  }
}

function alertUser(){
	alert("Twitter and IG login will not work properly, as it is still being worked on. We await an API key from the appropriate service.");
	return true;
}