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

function doAjaxImage(url, pictureUrl, mediaUrl, boardType){
	$('document').ready(function(){
		$('.carousel-inner').html('loading images...');
		$.ajax(url,
		{
			dataType: 'json', // type of response data
			timeout: 10000,     // timeout milliseconds
			success: function (data,status,xhr) {   // success callback function
				$('.carousel-inner').empty();
				data = JSON.parse(data);
				var active = 'active';
				if (data.length === 0){
					var paragraph = `<p class="text-center">No photos</p>`;
					$('.carousel').html(paragraph);
				}
				data.map((photo, i)=>{
					var photoMeta = `<li data-target="#photoCarousel" data-slide-to="${i}" class="${active}"></li>`
					var photoDiv = `<div class="carousel-item ${active}">
										<a href='${pictureUrl}${photo.pk}'>
											<img src="${mediaUrl}/${photo.fields.picture}" alt="" class="img-responsive" width="100%" height="auto">
											<div class="carousel-caption d-none d-md-block">
												<p>${photo.fields.description}</p>
											</div>
										</a>
									</div>`;
					$('.carousel-indicators').append(photoMeta);
					$('.carousel-inner').append(photoDiv);
					active = '';
				});
			},
			error: function (jqXhr, textStatus, errorMessage) { // error callback
				if(errorMessage === 'timeout'){
					doAjaxImage();
				} else {
					$('.carousel-inner').html('Error: ' + errorMessage);	
				}
			}
		});
	
		$(`#${boardType}`).addClass('mb-5');
	});
}
