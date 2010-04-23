import os, string
from string import Template

class Database:
    """
    Pickel'd database - Stores periodic table
    Index 1 is the names, Index 0 is the data. (Indexed for easy lookup).
    """
    import cPickle
    db = cPickle.load(file('ptable.data'))
    @classmethod
    def getSymbol(self, name):
        if name in self.db[1]:
            item = self.db[1].index(name)
            return self.db[0][item]
    @classmethod
    def getAll(self):
        return self.db[0]
        
#Unused for Original PyMonogo Interface
"""
class Database:
    db = Connection().chemistry.periodic_elements
    @classmethod
    def getSymbol(self, name):
        return self.db.find_one({"symbol": name})
"""

def sanitize(text):
    """
    Sanitizes text for referral URLS and for not found errors
    """
    text = string.replace(text, '<', '')
    text = string.replace(text, '>', '')
    return text

class Tag:
    """
    HTML Tag Helper
    """
    def header(self):
        pass
    def __init__(self):
        self.special_tags = {'br':'<br />', 's':'<br />', 'hr': '<hr />', 's_div':'<div>', 'e_div':'</div>'}
    def method_missing(self, tag, *args, **kwargs):
        attr = ''; text = ''; klass = ''
        if tag in self.special_tags:
            self.out = self.special_tags[tag]
        else:
            text = len(args) > 0 and args[0] or ''
            klass = len(args) > 1 and (" class='%s'" % args[1]) or ''
            if len(kwargs) > 0:
                for key in kwargs:
                    attr += " %s='%s'" % (key, kwargs[key])
            self.out = "<"+tag+attr+klass+">"+text+"</"+tag+">"
    def __getattr__(self, attr):
        def callable(*args, **kwargs):
            self.method_missing(attr, *args, **kwargs)
            return self.out
        return callable
        
class Buffer:
    """
    A Wrapper buffer class for syntax, instead of passing a string around.
    """
    def __init__(self):
        self.text = ''
    def a(self, text, *args):
        self.text += text + " ".join(args)
    def show(self):
        print self.text
    def flush(self):
        txt = self.text; self.text = ' '
        print txt

class Lookup:
    """
    Lookup an Element & Render It
    """
    def __init__(self):
        self.out = Buffer()
        self.t = Tag()
        self.db = Database()
    def render_symbol(self,sym, out):
        t = self.t
        out.a(t.br(), t.s_div())
        out.a(t.h3(t.a(sym['name'], style="color:#222", href=("?s="+sym['symbol'])), 'eln'))
        for prop in sym:
            out.a(t.s_div())
            out.a(' '.join(map(lambda w:w.capitalize(), prop.split('_'))))
            out.a(t.span(': ', 'sep'))
            out.a(t.span(str(sym[prop]), 'propval'))
            out.a(t.e_div())
        out.a(t.e_div())
        out.flush()
    def get_symbol(self,symi):
        t = self.t; out = self.out
        sym = self.db.getSymbol(symi)
        if (sym):
            self.render_symbol(sym, out)
        else:
            if (symi.find('<') == 0 or symi.find('>') == 0):
                symi = 'unknown'
            out.a(t.div(t.h4("Error: " + t.span("Cannot find element " + t.em(symi), 'el') + " by abbreviation."), 'error'))
    def show_all(self):
        allel = self.db.getAll()
        b = Buffer()
        for element in allel:
            self.render_symbol(element, b)
            b.a(self.t.br())
            print b.flush()
        self.out.a(b.text)
    def __del__(self):
        self.out.show()

