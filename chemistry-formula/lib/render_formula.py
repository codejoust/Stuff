import parser
import html
import render_formula

def formula_fetcher(cgi_data):
    """
    Render CGI formula data -- Possible Deletion
    """
    if "formula" in cgi_data:
        formulas = parser.TreeParser(cgi_data["formula"].value)
        render_formula.render(formulas)
        return True

def render(data = None):
    """
    Render The Page -- Should belong in the CGI file.
    """
    out = html.Buffer()
    t = html.Tag()
    if data:
        out.a(t.h3(" Balancing Equations: "))
        if (hasattr(data, 'product')):
            out.a(t.h2(" Reactant:  "))
            render_formula.showSingle(data.reactant, out, t, "reactant")
            out.a(t.h2(" Product: "))
            render_formula.showSingle(data.product, out, t, "product")
        else:
            out.a(t.h4("Molecular Weight:"))
            render_formula.showSingle(data.element, out, t, "element")
    else:
        out += "Please type an equation above to analyse... (error parsing previous)"
    out.show()
        
def showSingle(formula, out, tag, klass = ''):
    """
    Show Single Element
    """
    out.a(tag.s_div())
    for molecue in formula.molecues:
       out.a(tag.div(str(molecue), 'molecue'))
       for element in molecue.elements:
          out.a(tag.div(str(element), 'element'))
    out.a(tag.e_div(), tag.br())
