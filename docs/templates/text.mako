<%!
  def indent(s, spaces=4):
      new = s.replace('\n', '\n' + ' ' * spaces)
      return ' ' * spaces + new.strip()
%>

<%def name="deflist(s)">:${indent(s)[1:]}</%def>

<%def name="h3(s)">### ${s}
</%def>

<%def name="function(func)" buffered="True">
<%
        returns = show_type_annotations and func.return_annotation() or ''
        if returns:
            returns = ' \N{non-breaking hyphen}> ' + returns
%>
`${func.name}(${", ".join(func.params(annotate=show_type_annotations))})${returns}`
${func.docstring | deflist}
</%def>

<%def name="variable(var)" buffered="True">
<%
        annot = show_type_annotations and var.type_annotation() or ''
        if annot:
            annot = ': ' + annot
%>
`${var.name}${annot}`
${var.docstring | deflist}
</%def>

<%def name="class_(cls)" buffered="True">
`${cls.name}(${", ".join(cls.params(annotate=show_type_annotations))})`
${cls.docstring | deflist}
<%
  class_vars = cls.class_variables(show_inherited_members, sort=sort_identifiers)
  static_methods = cls.functions(show_inherited_members, sort=sort_identifiers)
  inst_vars = cls.instance_variables(show_inherited_members, sort=sort_identifiers)
  methods = cls.methods(show_inherited_members, sort=sort_identifiers)
  mro = cls.mro()
  subclasses = cls.subclasses()
%>
% if mro:
    ${h3('Przodkowie (w MRO)')}
    % for c in mro:
    * ${c.refname}
    % endfor

% endif
% if subclasses:
    ${h3('Potomkowie')}
    % for c in subclasses:
    * ${c.refname}
    % endfor

% endif
% if class_vars:
    ${h3('Zmienne klasowe')}
    % for v in class_vars:
${variable(v) | indent}

    % endfor
% endif
% if static_methods:
    ${h3('Metody statyczne')}
    % for f in static_methods:
${function(f) | indent}

    % endfor
% endif
% if inst_vars:
    ${h3('Zmienne instancji')}
    % for v in inst_vars:
${variable(v) | indent}

    % endfor
% endif
% if methods:
    ${h3('Metody')}
    % for m in methods:
${function(m) | indent}

    % endfor
% endif
</%def>

## Rozpocznij logikę wyjścia dla całego modułu.

<%
  variables = module.variables(sort=sort_identifiers)
  classes = module.classes(sort=sort_identifiers)
  functions = module.functions(sort=sort_identifiers)
  submodules = module.submodules()
  heading = 'Przestrzeń nazw' if module.is_namespace else 'Moduł'
%>

${heading} ${module.name}
=${'=' * (len(module.name) + len(heading))}
${module.docstring}


% if submodules:
Pod-moduły
----------
    % for m in submodules:
* ${m.name}
    % endfor
% endif

% if variables:
Zmienne
-------
    % for v in variables:
${variable(v)}

    % endfor
% endif

% if functions:
Funkcje
-------
    % for f in functions:
${function(f)}

    % endfor
% endif

% if classes:
Klasy
----
    % for c in classes:
${class_(c)}

    % endfor
% endif