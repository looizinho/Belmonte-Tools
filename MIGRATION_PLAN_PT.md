# Plano de Migração BelmonteTools  
#   
****Objetivo****  
Migrar o lançador de manutenção baseado em PowerShell para Python, de forma que possa ser distribuído primeiro como um executável de CLI e posteriormente estendido com uma interface gráfica.  
  
## Progresso Atual  
* Estrutura de pacote Python criada em ==src/belmonte_tools==.  
* Ponto de entrada da CLI adicionado, com um comando por ação de manutenção.  
* Lançador ==.cmd== legado redirecionado para a CLI em Python.  
  
****Estado Atual****  
O repositório agora contém a implementação legada em PowerShell e um esqueleto de CLI em Python. O script PowerShell permanece disponível como implementação de referência enquanto a versão em Python se torna o novo caminho de execução.  
  
O script PowerShell atualmente oferece:  
* Uma interface Windows Forms com botões para ações de manutenção.  
* Pontos de entrada para restauração e recuperação do sistema.  
* Alterações em serviços, firewall, Defender, descoberta de rede, compartilhamento SMB e perfil de energia.  
* Ações de conveniência como abrir pastas, mostrar o IP local, copiar o caminho de rede e iniciar ferramentas externas.  
  
- ****Princípios de Migração****  
* Manter a primeira versão em Python funcionalmente equivalente à ferramenta atual.  
* Separar a lógica de comandos da lógica de interface desde o início.  
* Priorizar módulos da biblioteca padrão e adicionar dependências externas apenas quando as APIs do Windows exigirem.  
* Tratar ações privilegiadas como operações explícitas e auditáveis.  
* Fazer da CLI a fonte de verdade, para que a futura GUI apenas encapsule a mesma camada de ações.  
  
## Arquitetura Alvo  
##   
### 1. Camada central de ações  
Criar um pacote Python que exponha uma função por ação de manutenção.  
  
Layout sugerido:  
* ==belmonte_tools/==  
* ==belmonte_tools/actions/==  
* ==belmonte_tools/ui/==  
* ==belmonte_tools/cli.py==  
* ==belmonte_tools/config.py==  
* ==belmonte_tools/logging.py==  
  
Responsabilidades:  
* ==actions/==: operações de sistema, cada uma isolada e testável.  
* ==cli.py==: análise de argumentos e despacho de comandos.  
* ==ui/==: ponto de entrada da futura GUI, inicialmente vazio ou mínimo.  
* ==config.py==: constantes como caminhos, URLs, listas de serviços e nomes de pontos de restauração.  
  
### 2. CLI primeiro  
O executável Python deve expor:  
* Um comando de listagem para mostrar as ações disponíveis.  
* Um comando por ação.  
* Um comando de executar tudo ou perfil para fluxos combinados, como modo de evento ou compartilhamento completo de rede.  
* Saída clara, códigos de retorno e logs adequados para diagnóstico.  
  
### 3. GUI depois  
Após a CLI estar estável, adicionar uma camada de GUI que apenas chame as mesmas funções de ação.  
Isso mantém a lógica de negócios reutilizável e evita uma segunda implementação de cada tarefa de manutenção.  
  
****Inventário de Comandos****  
  
O script atual em PowerShell contém os seguintes grupos de ações:  
  
- **Ações seguras ou de baixo risco**  
* Abrir Restauração do Sistema.  
* Abrir uma pasta compartilhada no Explorer.  
* Mostrar o endereço IP local.  
* Copiar o caminho de rede do computador.  
* Abrir pasta do Google Drive.  
* Executar Limpeza de Disco.  
  
- **Ações elevadas ou de alto risco**  
* Criar ponto de restauração.  
* Definir serviços como manual ou automático.  
* Desativar ou reativar a proteção em tempo real do Defender.  
* Desativar ou habilitar perfis de firewall.  
* Habilitar descoberta de rede e compartilhamento de arquivos.  
* Criar um compartilhamento SMB.  
* Alterar a categoria da rede para Privada.  
* Habilitar NetBIOS sobre TCP/IP.  
* Definir plano de energia ultra desempenho.  
* Executar SFC.  
* Executar CHKDSK.  
* Acionar "Winget upgrade all".  
* Desativar aplicativos em segundo plano.  
* Configurar o pacote de modo de evento.  
* Restaurar padrões do Windows.  
  
## Estratégia Sugerida de Implementação em Python  
##   
### Fase 1. Inventário e paridade  
Antes de reescrever, mapear cada botão PowerShell para:  
* Sequência exata de comandos.  
* Se requer privilégios de administrador.  
* Se a ação é idempotente.  
* Se pode falhar sem causar problemas.  
* Se precisa de confirmação do usuário.  
  
Entregável:  
* Uma matriz de comandos em código ou documentação.  
  
### Fase 2. Construir a camada de ações  
Implementar as operações de sistema em Python usando o menor conjunto de dependências possível.  
  
Ferramentas prováveis:  
* ==subprocess== para comandos nativos como ==rstrui.exe==, ==powercfg==, ==netsh==, ==sfc==, ==chkdsk==, ==winget==, ==cleanmgr e== ==reg==.  
* ==ctypes== ou ==pywin32== para APIs específicas do Windows quando necessário.  
* ==psutil== para inspeção de rede e processos, se necessário.  
* ==winreg== para gravações no registro.  
* ==socket== ou ==psutil== para exibir IP.  
* ==logging== para logs estruturados.  
  
Comportamentos importantes a preservar:  
* Ações não devem ignorar falhas silenciosamente.  
* Ações perigosas devem pedir confirmação no modo CLI.  
* Comandos que requerem elevação devem detectar isso cedo e explicar o motivo.  
  
### Fase 3. Executável da CLI  
Construir uma interface de linha de comando em torno da camada de ações.  
  
Comportamento recomendado:  
* ==belmonte-tools --help==  
* ==belmonte-tools list==  
* ==belmonte-tools restore-point==  
* ==belmonte-tools disable-firewall==  
* ==belmonte-tools event-mode==  
  
Experiência recomendada:  
* Usar nomes de comando curtos e descritivos.  
* Imprimir resumo de sucesso ou falha após cada ação.  
* Sair com código diferente de zero em caso de falha.  
  
### Fase 4. Empacotamento  
Empacotar a CLI em um executável Windows.  
  
Abordagem recomendada:  
* Começar com PyInstaller para criar rapidamente um ==.exe distribuível==.  
* Adicionar um script de build que defina versão, ícone e pasta de saída.  
* Manter o layout do código Python compatível com o futuro empacotamento da GUI.  
  
### Fase 5. Fundação da GUI  
Quando a CLI estiver estável:  
* Introduzir um framework de GUI como Tkinter, PySide6 ou outro compatível com Windows.  
* Reutilizar a mesma camada de ações.  
* Manter os widgets da GUI simples e declarativos.  
* Evitar embutir comandos do shell na camada de interface.  
  
1. ****Ordem de Implementação Sugerida****  
2. Recriar o inventário de ações em Python.  
3. Implementar utilitários para elevação, logging e execução de comandos.  
4. Migrar primeiro as ações de menor risco.  
5. Migrar os fluxos de rede compartilhada e perfil de energia.  
6. Migrar as ações elevadas que alteram o sistema.  
7. Adicionar parsing de argumentos e texto de ajuda.  
8. Adicionar empacotamento para executável único.  
9. Somente depois adicionar a GUI.  
  
## Áreas de Risco  
##   
**Privilégios e elevação**  
Muitas ações exigem direitos de administrador. A versão em Python deve detectar status de elevação e autoelevar ou falhar com mensagem clara.  
  
**Comportamento exclusivo do Windows**  
O projeto depende fortemente de APIs e ferramentas do Windows. A versão em Python deve declarar explicitamente que funciona apenas em Windows.  
  
**Efeitos colaterais**  
Algumas ações atuais alteram firewall, Defender, serviços e configurações de compartilhamento de rede. Estas precisam de:  
* confirmação explícita,  
* caminhos claros de rollback quando possível,  
* e logging cuidadoso.  
  
**Compatibilidade de comandos**  
Alguns cmdlets do PowerShell não possuem equivalente direto em Python. Nesses casos, chamar a ferramenta nativa do Windows em vez de tentar reimplementar o recurso.  
  
- ****Requisitos de Qualidade Recomendados****  
* Cada ação pode ser executada de forma independente via CLI.  
* Cada ação informa sucesso/falha claramente.  
* Modo de evento e modo de restaurar padrões funcionam como pares opostos.  
* Ações administrativas falham graciosamente quando não elevadas.  
* O empacotamento gera um executável funcional em uma máquina Windows limpa.  
* Teste manual simples cobre todos os comandos equivalentes aos botões.  
  
- ****Questões em Aberto a Decidir no Início****  
* Qual framework de GUI será usado depois.  
* Se a CLI deve autoelevar ou exigir que o usuário execute como administrador.  
* Se manter o wrapper .cmd existente por compatibilidade ou substituí-lo por um lançador Python.  
* Se manter os rótulos atuais em português ou adotar nomes bilíngues.  
  
****Recomendação Rápida****  
O caminho mais seguro é:  
* Camada de ações em Python primeiro.  
* CLI em segundo.  
* Empacotamento em terceiro.  
* GUI por último.  
  
Essa ordem minimiza riscos de reescrita e permite validar comandos que alteram o sistema antes de adicionar complexidade de interface.  
