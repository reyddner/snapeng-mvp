"""
Motor de processamento de templates de engenharia
Arquivo: backend/app/services/template_engine.py
"""

from typing import Dict, Any, List
import re

from app.core.safe_formula import evaluate_formula, substitute_inputs


class TemplateEngine:
    """
    Motor de processamento de templates de engenharia
    Suporta:
    - Variáveis dinâmicas: {{variavel}}
    - Cálculos automáticos
    """
    _VARIABLE_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")
    _UNSAFE_MARKERS = ("{%", "%}", "{#", "#}")

    def render_template(
        self, template_structure: Dict[str, Any], user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Renderiza template com dados do usuário

        Args:
            template_structure: Estrutura JSON do template
            user_data: Dados preenchidos pelo usuário

        Returns:
            Dict com conteúdo renderizado
        """
        calculations = self._process_calculations(
            template_structure.get("calculations", []), user_data
        )
        render_data = dict(user_data)
        for name, result in calculations.items():
            if "value" in result:
                render_data[name] = result["value"]

        rendered_sections = []

        for section in template_structure.get("sections", []):
            rendered_section = {
                "title": section["title"],
                "content": self._render_content(section["content"], render_data),
                "subsections": [],
            }

            # Renderizar subseções se existirem
            for subsection in section.get("subsections", []):
                rendered_section["subsections"].append(
                    {
                        "title": subsection["title"],
                        "content": self._render_content(subsection["content"], render_data),
                    }
                )

            rendered_sections.append(rendered_section)

        # Processar cálculos automáticos
        return {
            "sections": rendered_sections,
            "calculations": calculations,
            "normas": template_structure.get("normas", []),
            "metadata": {
                "generated_at": "timestamp",
                "template_version": template_structure.get("version", "1.0"),
            },
        }

    def _render_content(self, content: str, data: Dict[str, Any]) -> str:
        """Renderiza apenas placeholders simples {{variavel}} com substituição segura."""
        self._validate_safe_template_content(content)

        def _replace(match: re.Match[str]) -> str:
            variable_name = match.group(1)
            value = data.get(variable_name)
            return "" if value is None else str(value)

        return self._VARIABLE_PATTERN.sub(_replace, content)

    def _validate_safe_template_content(self, content: str) -> None:
        if any(marker in content for marker in self._UNSAFE_MARKERS):
            raise ValueError(
                "Template contém sintaxe não permitida. Use apenas placeholders no formato {{variavel}}."
            )

    def _process_calculations(
        self, calculations: List[Dict], data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Processa cálculos de engenharia

        Exemplo de calculation:
        {
            "name": "cbr_projeto",
            "formula": "cbr_campo / 1.5",
            "inputs": ["cbr_campo"],
            "unit": "%"
        }
        """
        results = {}

        for calc in calculations:
            try:
                formula = substitute_inputs(
                    calc["formula"], calc.get("inputs", []), data
                )
                result = evaluate_formula(formula)
                results[calc["name"]] = {
                    "value": result,
                    "unit": calc.get("unit", ""),
                    "formula": calc["formula"],
                }
            except (ValueError, TypeError, SyntaxError, ZeroDivisionError) as e:
                results[calc["name"]] = {"error": str(e)}

        return results

    def validate_variables(
        self, template_structure: Dict[str, Any], user_data: Dict[str, Any]
    ) -> List[str]:
        """
        Valida se todas as variáveis necessárias foram preenchidas

        Returns:
            Lista de variáveis faltantes
        """
        required_vars = set()

        # Extrair variáveis de todas as seções
        for section in template_structure.get("sections", []):
            content = section.get("content", "")
            # Regex para encontrar {{variavel}}
            vars_in_content = re.findall(r"\{\{(\w+)\}\}", content)
            required_vars.update(vars_in_content)

        for variable in template_structure.get("variables", []):
            if variable.get("required"):
                required_vars.add(variable["name"])

        missing = []
        for variable in sorted(required_vars):
            value = user_data.get(variable)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(variable)
        return missing

    def validate_user_data(
        self, template_structure: Dict[str, Any], user_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Valida respostas do questionário antes da renderização."""
        errors = {}
        for variable in template_structure.get("variables", []):
            name = variable.get("name")
            value = user_data.get(name)
            if not self.is_question_active(variable, user_data):
                continue
            if variable.get("required") and (value is None or value == ""):
                errors[name] = "Este campo é obrigatório."
                continue

            if value is None or value == "":
                continue

            if variable.get("type") == "number":
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    errors[name] = "Informe um número válido."
                    continue
                if variable.get("min") is not None and numeric_value < variable["min"]:
                    errors[name] = f"O valor mínimo é {variable['min']}."
                elif variable.get("max") is not None and numeric_value > variable["max"]:
                    errors[name] = f"O valor máximo é {variable['max']}."

            if variable.get("type") == "select":
                allowed_values = {
                    option.get("value") for option in variable.get("options", [])
                }
                if value not in allowed_values:
                    errors[name] = "Selecione uma opção válida."

        return errors

    @staticmethod
    def is_question_active(question: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        dependency = question.get("depends_on")
        if not dependency:
            return True
        actual = user_data.get(dependency.get("field"))
        if "equals" in dependency:
            return actual == dependency["equals"]
        if dependency.get("not_empty"):
            return actual is not None and actual != ""
        if "in" in dependency:
            return actual in dependency["in"]
        return False

