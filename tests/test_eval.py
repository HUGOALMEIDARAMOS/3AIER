import types

import agent


def test_eval_agente_soma_numero_com_ferramenta(monkeypatch):
    class ToolCallFake:
        def __init__(self, tool_id, name, arguments):
            self.id = tool_id
            self.function = types.SimpleNamespace(name=name, arguments=arguments)

    class MensagemComFerramenta:
        def __init__(self, tool_calls):
            self.tool_calls = tool_calls
            self.content = None

        def model_dump(self, exclude_none=True):
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": item.id,
                        "type": "function",
                        "function": {
                            "name": item.function.name,
                            "arguments": item.function.arguments,
                        },
                    }
                    for item in self.tool_calls
                ],
            }

    class MensagemFinal:
        def __init__(self, content):
            self.content = content
            self.tool_calls = []

        def model_dump(self, exclude_none=True):
            return {"role": "assistant", "content": self.content}

    class RespostaFake:
        def __init__(self, message):
            self.choices = [types.SimpleNamespace(message=message)]

    class FakeCompletions:
        def __init__(self, respostas):
            self._respostas = list(respostas)

        def create(self, **kwargs):
            return self._respostas.pop(0)

    class FakeChat:
        def __init__(self, respostas):
            self.completions = FakeCompletions(respostas)

    class ClienteFake:
        def __init__(self, respostas):
            self.chat = FakeChat(respostas)

    cliente_fake = ClienteFake(
        [
            RespostaFake(
                MensagemComFerramenta(
                    [ToolCallFake("call_1", "somar", '{"a": 1234, "b": 5678}')]
                )
            ),
            RespostaFake(MensagemFinal("1234 + 5678 = 6912")),
        ]
    )

    monkeypatch.setattr(agent, "get_cliente", lambda: cliente_fake)
    monkeypatch.setattr(agent, "MAX_ITERACOES", 3)

    mensagens = [{"role": "user", "content": "quanto é 1234 mais 5678?"}]
    resposta = agent.responder(mensagens)

    assert resposta == "1234 + 5678 = 6912"
    assert mensagens[-1] == {"role": "assistant", "content": "1234 + 5678 = 6912"}
    assert mensagens[-2]["content"] == '{"resultado": 6912}'


def test_eval_agente_trata_ferramenta_invalida_sem_quebrar(monkeypatch):
    class ToolCallFake:
        def __init__(self, tool_id, name, arguments):
            self.id = tool_id
            self.function = types.SimpleNamespace(name=name, arguments=arguments)

    class MensagemComFerramenta:
        def __init__(self, tool_calls):
            self.tool_calls = tool_calls
            self.content = None

        def model_dump(self, exclude_none=True):
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": item.id,
                        "type": "function",
                        "function": {
                            "name": item.function.name,
                            "arguments": item.function.arguments,
                        },
                    }
                    for item in self.tool_calls
                ],
            }

    class MensagemFinal:
        def __init__(self, content):
            self.content = content
            self.tool_calls = []

        def model_dump(self, exclude_none=True):
            return {"role": "assistant", "content": self.content}

    class RespostaFake:
        def __init__(self, message):
            self.choices = [types.SimpleNamespace(message=message)]

    class FakeCompletions:
        def __init__(self, respostas):
            self._respostas = list(respostas)

        def create(self, **kwargs):
            return self._respostas.pop(0)

    class FakeChat:
        def __init__(self, respostas):
            self.completions = FakeCompletions(respostas)

    class ClienteFake:
        def __init__(self, respostas):
            self.chat = FakeChat(respostas)

    cliente_fake = ClienteFake(
        [
            RespostaFake(
                MensagemComFerramenta([ToolCallFake("call_1", "ferramenta_inexistente", '{}')])
            ),
            RespostaFake(MensagemFinal("Tente outra abordagem.")),
        ]
    )

    monkeypatch.setattr(agent, "get_cliente", lambda: cliente_fake)
    monkeypatch.setattr(agent, "MAX_ITERACOES", 3)

    mensagens = [{"role": "user", "content": "Use uma ferramenta inválida"}]
    resposta = agent.responder(mensagens)

    assert resposta == "Tente outra abordagem."
    assert '"erro": "Ferramenta \'ferramenta_inexistente\' não existe."' in mensagens[-2]["content"]
