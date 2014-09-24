class CartMiddleware(object):
	"""docstring for CartMiddleware"""

	def process_request(self, request):
		if request.session.get("cart",""):
			request.nbre_achats = len(request.session['cart'])
		else:
			request.nbre_achats = 0

	def process_response(self, request, response):
		return response