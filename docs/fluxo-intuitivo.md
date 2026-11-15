# Fluxo intuitivo: da evidência ao formulário do Lattes

Princípio: **o usuário entrega o documento; o sistema descobre onde ele entra no Lattes.** O usuário não precisa
saber o nome de nenhuma aba. Protótipo em `classificador.py`, testado por `tests/teste_classificador.py`.

## 1. Três caminhos, decididos pela confiança do reconhecimento

| Decisão | Quando | O que o usuário vê |
| --- | --- | --- |
| **Avançar** | 1º candidato com confiança ≥ 0,70 e vantagem ≥ 0,25 sobre o 2º | "Entendi: **Apresentação de trabalho** (cita apresentação oral; trabalho intitulado…)". Formulário já preenchido; botão "Não é isso" discreto |
| **Confirmar** | Há 2 a 3 candidatos plausíveis | Cartões lado a lado, cada um com o motivo em uma frase e uma prévia dos campos que seriam preenchidos |
| **Escolher** | Nenhum candidato ≥ 0,35, ou o arquivo não tem texto legível | Escolhedor guiado (abaixo) |

Regras de segurança: o sistema **nunca preenche em silêncio** um item que ainda não implementamos; mostra "reconhecido,
preenchimento em breve" e leva ao escolhedor. Itens com `implementado: false` seguem esse caminho.

## 2. Quando nada serve: escolhedor guiado em 3 camadas

1. **Pergunta em linguagem do usuário**, não em nomes do Lattes (cada `grupo` do classificador):
   - Publiquei ou apresentei um trabalho · Participei ou organizei um evento · Orientei ou fui banca ·
   - Estudei (diploma, curso) · Trabalho ou trabalhei (vínculo, revisor, editor) · Registrei ou criei algo (patente, software, produto) ·
   - Recebi prêmio/idioma/licença · Projeto de pesquisa ou extensão · **Outro**.
2. **Dentro do grupo, lista curta com exemplo de documento** ("Certificado de ministrante → Curso ministrado").
3. **Busca livre em todos os 70 itens**, com sinônimos ("TCC", "monitoria", "parecer", "palestra"), sempre visível no topo.

Último recurso ("Outro"): mostrar o item mais próximo de **Outras informações relevantes** e registrar o documento
para revisão humana (ver §4). Nunca deixar o usuário sem saída.

## 3. Um documento, vários registros

Certificado de apresentação comprova também a participação no evento; ata de defesa comprova banca, orientação e, às vezes,
titulação. O resultado traz `tambem_pode_gerar`: depois de concluir o primeiro registro, o sistema oferece "Quer registrar
também a **participação no evento**?" com os dados já preenchidos. Nunca cria o segundo sem confirmação.

## 4. O sistema aprende com a correção

Cada vez que o usuário escolhe outro item que não o sugerido, guardamos (texto resumido, item sugerido, item escolhido).
Isso alimenta: (a) ajuste dos pesos das regras; (b) lista de documentos que precisam de regra nova; (c) a ordem das
opções no escolhedor (mais escolhido primeiro). Sem enviar o documento a terceiros.

## 5. Casos de borda a tratar

- **PDF escaneado** (sem texto): pedir OCR ou ir ao escolhedor, dizendo o motivo.
- **Vários documentos de uma vez**: fila com um cartão por documento, cada um com sua decisão.
- **Usuário não consta no documento**: avisar antes de avançar (já existe para certificado, artigo e orientação).
- **Caderno com muitos resumos**: caminho próprio (busca pelo nome do usuário).

## 6. O que ainda não está provado

O protótipo acerta os 30 casos de teste, mas **26 deles foram escritos junto com as regras**, então isso mede consistência,
não acerto no mundo real. O próximo teste honesto é com **documentos reais**: cada documento novo entra no teste com o item
esperado, e a regra só é ajustada quando um documento real falha.
