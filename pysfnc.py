import ast
import attr


########################################################################

def psf_attr(nd, raise_if_not=True):
    """
    Extract the attribute name from an AST node of the form

        PSF.something

    If the given AST node is not of that form, either raise a
    ValueError (if raise_if_not is True), or return None (if
    raise_if_not is False).
    """
    attr_val = None
    if isinstance(nd, ast.Attribute):
        val = nd.value
        if isinstance(val, ast.Name) and val.id == 'PSF':
            attr_val = nd.attr
    if attr_val is None and raise_if_not:
        raise ValueError('expected PSF.something')
    return attr_val


def chained_key(nd):
    """
    Given an AST node representing a value like

        foo['bar']['baz']

    return a list of the components involved; here,

        ['foo', 'bar', 'baz']

    If the given node is not of that form, raise a ValueError.
    """
    if isinstance(nd, ast.Name):
        return [nd.id]
    if isinstance(nd, ast.Subscript):
        if isinstance(nd.slice, ast.Index):
            if isinstance(nd.slice.value, ast.Str):
                suffix = nd.slice.value.s
                if isinstance(nd.value, ast.Name):
                    prefix = [nd.value.id]
                else:
                    prefix = chained_key(nd.value)
                return prefix + [suffix]
    raise ValueError('expected chained lookup via strings on name')


########################################################################

@attr.s
class TestComparison:
    predicate_name = attr.ib()
    predicate_variable = attr.ib()
    predicate_literal = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd, ast.Call) and len(nd.args) == 2:
            return cls(psf_attr(nd.func),
                       chained_key(nd.args[0]),
                       nd.args[1].s)
        raise ValueError('expected function-call PSF.something(...)')
