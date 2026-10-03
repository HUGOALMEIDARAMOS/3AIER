import json

import agent


def test_carregar_contexto_inclui_agente_e_memoria(monkeypatch, tmp_path):
    agente_arquivo = tmp_path / "agent.md"
    memoria_arquivo = tmp_path / "memory.md"
    agente_arquivo.write_text("Você é um agente de teste.", encoding="utf-8")
    memoria_arquivo.write_text(
        "Memória persistente: o usuário gosta de matemática.",
        encoding="utf-8",
    )

    monkeypatch.setattr(agent, "AGENT_MD", agente_arquivo)
    monkeypatch.setattr(agent, "MEMORY_MD", memoria_arquivo)

    contexto = agent.carregar_contexto()

    assert "Você é um agente de teste." in contexto
    assert "Memória persistente" in contexto


def test_executar_ferramenta_soma_e_erro_em_ferramenta_inexistente():
    resultado = json.loads(agent.executar_ferramenta("somar", {"a": 2, "b": 3}))
    assert resultado["resultado"] == 5

    erro = json.loads(agent.executar_ferramenta("desconhecida", {}))
    assert "não existe" in erro["erro"]


def test_responder_texto_sem_ferramenta(monkeypatch):
    class MensagemFake:
        def __init__(self, content):
            self.content = content
            self.tool_calls = []

        def model_dump(self, exclude_none=True):
            return {"role": "assistant", "content": self.content}

    class RespostaFake:
        def __init__(self, content):
            self.choices = [type("Choice", (), {"message": MensagemFake(content)})()]

    class ClienteFake:
        class chat:
            class completions:
                @staticmethod
                def create(model, messages, tools, temperature):
                    return RespostaFake("Resposta direta")

    monkeypatch.setattr(agent, "get_cliente", lambda: ClienteFake())

    mensagens = [{"role": "user", "content": "Olá"}]
    resposta = agent.responder(mensagens)

    assert resposta == "Resposta direta"
    assert mensagens[-1] == {"role": "assistant", "content": "Resposta direta"}
