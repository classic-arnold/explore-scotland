from django import template

from explore_scotland_app.models import Photo

register = template.Library()

@register.inclusion_tag('explore_scotland_app/search-form.html')
def get_search_form(category_searched=None, sorted_by=None, query=None):
	return {'categories': Photo.CATEGORY_CHOICES, 'category_searched': category_searched, 'sorted_by': sorted_by, 'query': query}
	
@register.inclusion_tag('explore_scotland_app/photo-grid.html')
def get_photo_grid(photos):
	return {'photos': photos,}
	
@register.inclusion_tag('explore_scotland_app/photo-carousel.html')
def photo_carousel():
	return