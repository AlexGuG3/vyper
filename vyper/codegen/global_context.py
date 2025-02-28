from functools import cached_property
from typing import Optional

from vyper import ast as vy_ast
from vyper.semantics.namespace import get_namespace, override_global_namespace
from vyper.semantics.types.utils import type_from_annotation


# Datatype to store all global context information.
# TODO: rename me to ModuleT
class GlobalContext:
    def __init__(self, module: Optional[vy_ast.Module] = None):
        self._module = module

    @cached_property
    def functions(self):
        return self._module.get_children(vy_ast.FunctionDef)

    @cached_property
    def variables(self):
        # variables that this module defines, ex.
        # `x: uint256` is a private storage variable named x
        if self._module is None:  # TODO: make self._module never be None
            return None
        variable_decls = self._module.get_children(vy_ast.VariableDecl)
        return {s.target.id: s.target._metadata["varinfo"] for s in variable_decls}

    def parse_type(self, ast_node):
        # kludge implementation for backwards compatibility.
        # TODO: replace with type_from_ast
        try:
            ns = self._module._metadata["namespace"]
        except AttributeError:
            ns = get_namespace()
        with override_global_namespace(ns):
            return type_from_annotation(ast_node)

    @property
    def immutables(self):
        return [t for t in self.variables.values() if t.is_immutable]

    @cached_property
    def immutable_section_bytes(self):
        return sum([imm.typ.memory_bytes_required for imm in self.immutables])
