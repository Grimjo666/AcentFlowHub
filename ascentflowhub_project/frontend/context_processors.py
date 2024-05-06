# def set_previous_url_page(request):
#
#     url = request.session.get('previous_page')
#     request.session['previous_page'] = request.build_absolute_uri()
#
#     return {
#         'previous_page_url': url
#     }