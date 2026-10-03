import json

import agent


def test_contrato_da_ferramenta_somar_esta_consistente():
    assert isinstance(agent.FERRAMENTAS, list)
    assert len(agent.FERRAMENTAS) > 0

    ferramenta = agent.FERRAMENTAS[0]
    assert ferramenta["type"] == "function"

    func = ferramenta["function"]
    assert func["name"] == "somar"
    assert "Soma dois números" in func["description"]
    assert func["parameters"]["type"] == "object"
    assert func["parameters"]["required"] == ["a", "b"]

    props = func["parameters"]["properties"]
    assert props["a"]["type"] == "number"
    assert props["b"]["type"] == "number"
    assert "Primeiro número" in props["a"]["description"]
    assert "Segundo número" in props["b"]["description"]

    assert "somar" in agent.EXECUTORES
    assert callable(agent.EXECUTORES["somar"])


def test_executar_ferramenta_respeita_contrato_json_de_entrada_e_saida():
    payload = json.loads(agent.executar_ferramenta("somar", {"a": 7, "b": 5}))
    assert payload == {"resultado": 12}

    erro = json.loads(agent.executar_ferramenta("desconhecida", {"a": 1}))
    assert "desconhecida" in erro["erro"]
    assert "não existe" in erro["erro"]
