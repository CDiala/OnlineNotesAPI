from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    '''
    Returns a PDF file created as per the template and dictionary passed in
    :param template_src: The path of the html template to be used for pdf generation
    :param context_dict: Dictionary containing variables to pass into the html template
    :return: A PDF object that can then be sent back to client or saved on server
    '''
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')
