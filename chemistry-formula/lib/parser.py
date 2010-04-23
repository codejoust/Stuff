import re, sys, time, html
from re import compile as reinit
import parser

class TreeParser:
    """
    Parse a full formula, splits into elements or products and reactants
    """
    pattern = reinit(" ?(?:=|\-)*> ?")
    def __init__(self, string):
        sides = self.pattern.split(string)
        if len(sides) == 2:
            self.reactant = parser.Reactant(sides[0])
            self.product  = parser.Product(sides[1])
        elif len(sides) == 1:
            self.element = parser.Formula(string)
        
    def add_symbols(self):
        pass
    def isBalanced(self):
        result = (reactantWeight == productWeight)

class EquationBalancer:
    """
    Incomplete Class to balance equations
    """
    def __init__(self, parser):
        self.parser = parser
        self.reactant = self.parser.reactant
        self.product  = self.parser.product
    def isBalanced(self):
        return (self.reactant.weight() == self.product.weight())
    def getDifference(self):
        return abs(self.product.weight() - self.reactant.weight())
        
class Formula:
    """
    Represents a formula, holds Molecule and Element Classes
    """
    pattern = reinit(" ?\+ ?")
    def __init__(self, string):
        self.text = string
        self.molecues = list()
        for el in self.pattern.split(self.text):
            self.molecues.append(parser.Molecule(el))
    def getElements(self):
        self.elements = list()
        for molecue in self.molecues:
            for element in molecue:
                self.elements.append(parser.Element)
        return self.elements
    
    def __str__(self):
        return "Formula: %s" % self.text
        
class Reactant(parser.Formula):
    """
    Extension to Formula that just returns a different name, and has a different identity.
    """
    def __str__(self):
        return "Reactant Formula: %s" % self.text
class Product(parser.Formula):
    """
    Extension to Formula that just returns a different name, and has a different identity.
    """
    def __str__(self):
        return "Product: %s" % self.text
        
class Molecule:
    """
    Holds many elements and their relationships. Parses text for moles, too.
    """
    pattern = reinit("^(\d?)(.+)")
    def __init__(self, string):
        self.text = string
        match = self.pattern.match(self.text).groups()
        self.moles = match[0] and int(match[0]) or 1
        self.elementsuc = match[1]
        self.elements = list()
        eles = Element.pattern.findall(self.elementsuc)
        self.weight = 0
        for element in eles:
            newel = parser.Element(element, self.moles)
            self.elements.append(newel)
            self.weight += newel.weight * newel.amt * self.moles
         
    def __str__(self):
        return 'Molecule: %s - %i <abbr title="moles">m.</abbr> - %g g/m<br />' % (self.text, self.moles, self.weight)
            
# @todo Convert string formatting to string templates.
class Element:
    """
    Base element class stores element properties, and looks up the element in the periodic table database.
    """
    pattern = reinit("(([A-Z][a-z]?)(?:(?:\.|_)(\d+))?)") 
    def __init__(self, data, moles):
        self.moles = moles
        self.data = data
        self.symbol = data[1]
        if len(data[2]):
            self.amt  = int(data[2])
        else:
            self.amt = 1
        self.info = (html.Database()).getSymbol(self.symbol)
        try:
            self.weight = round(self.info['weight'], 2)
            self.name = self.info['name']
        except TypeError:
            self.weight = 0
            self.name = 'Match not found'
    def __str__(self):
        return ('<div class="molecule" style="padding-left:20px">'+("<br />\n".join(
                ['<a class="grey" href="./element-info?s=%s">Element: %s - %i</a>',
                "~> Name: %s",
                "~> Weight: %.2f ^ %i = %.2f g/m"]))+'</div>\n') % (
                self.symbol, self.symbol, self.amt, self.name,
                self.weight, self.amt, self.weight * self.amt)

