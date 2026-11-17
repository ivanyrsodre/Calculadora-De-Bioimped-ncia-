# CorpoFit — calculadora de composição corporal

Aplicação web em português para estimar densidade corporal e percentual de gordura, registrar avaliações antropométricas e acompanhar tendências. Feita com Python, Flask, SQLite, HTML, CSS e JavaScript.

> **Importante:** os resultados são estimativas produzidas por equações antropométricas. Não são diagnóstico, prescrição ou substituto de avaliação profissional. Padronize protocolo, técnica e condições de medida ao comparar resultados.

## Funcionalidades

- Protocolos de circunferências da Marinha dos EUA (Navy), com equações masculina e feminina.
- Jackson–Pollock de 3 sítios e de 7 sítios, com conjuntos de medidas correspondentes à equação selecionada.
- Estimativa de densidade corporal, percentual de gordura, massa de gordura e massa livre de gordura; IMC complementar e razão cintura/estatura quando aplicável.
- Perfis locais e histórico de avaliações com data, filtro, edição e exclusão.
- Gráficos SVG de percentual de gordura, peso e massa livre de gordura; exportação CSV e relatório imprimível/salvável como PDF pelo navegador.
- Temas claro e noturno, formulários guiados e validação no navegador e no servidor.
- Unidades métricas exclusivamente: peso em kg, estatura e circunferências em cm, dobras em mm.

## Requisitos

- Python 3.11 ou mais recente.
- Git, para clonar o repositório.
- `pip` (normalmente instalado com Python).

Dependências Python declaradas em `requirements.txt`:

- Flask 3.1.1
- itsdangerous 2.2.0

O banco de dados é o SQLite incluído na biblioteca padrão do Python; não é necessário instalar um servidor de banco separado.

## Instalação após clonar do GitHub

Substitua `SEU_USUARIO` e `SEU_REPOSITORIO` pelo endereço do seu repositório:

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
python -m venv .venv
```

Ative o ambiente virtual. No macOS ou Linux:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Como executar

Com o ambiente virtual ativado, na pasta raiz do projeto, rode:

```bash
python app.py
```

Abra [http://127.0.0.1:3000](http://127.0.0.1:3000) no navegador. Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`.

O servidor de desenvolvimento usa `127.0.0.1` e a porta `3000` por padrão. É possível alterar a porta, por exemplo:

macOS/Linux:

```bash
PORT=5000 python app.py
```

Windows PowerShell:

```powershell
$env:PORT = "5000"
python app.py
```

Nesse exemplo, acesse [http://127.0.0.1:5000](http://127.0.0.1:5000). `FLASK_DEBUG=1` pode ser usado apenas durante o desenvolvimento local; não ative o modo debug em um servidor público.

## Guardar os arquivos no GitHub

GitHub guarda o código-fonte, mas não executa este aplicativo Flask por conta própria. Se você ainda não criou o repositório:

1. No GitHub, crie um repositório vazio, por exemplo `corpofit`.
2. Não inclua um segundo README, licença ou `.gitignore` no assistente de criação, pois esses arquivos já existem no projeto.
3. Na pasta do projeto, inicialize o Git e envie os arquivos. Troque `SEU_USUARIO` pelo seu nome de usuário do GitHub:

```bash
git init -b main
git add .
git commit -m "Adiciona o CorpoFit"
git remote add origin https://github.com/SEU_USUARIO/corpofit.git
git push -u origin main
```

Se você clonou um repositório existente, não rode `git init` nem adicione outro remoto; faça as alterações, revise-as com `git status`, e então use `git add`, `git commit` e `git push` normalmente.

O `.gitignore` do projeto exclui o banco local, segredos `.env`, ambientes virtuais e arquivos temporários. Antes de enviar código, confira `git status` e nunca adicione dados de clientes, exportações privadas, senhas ou chaves.

## Executar os testes

Na raiz do projeto, com o ambiente virtual ativado:

```bash
python -m unittest discover -s tests -v
```

Os testes usam banco temporário e verificam cálculos, validações, persistência, migração de banco legado, exportação e rotas. Os dados de teste não devem conter informações pessoais reais.

## Dados e variáveis de ambiente

Na primeira execução, o aplicativo cria o SQLite automaticamente em `instance/corpofit.sqlite3`. Para alterar o caminho do banco, configure `CORPOFIT_DB_PATH` antes de iniciar.

macOS/Linux:

```bash
CORPOFIT_DB_PATH=/caminho/seguro/corpofit.sqlite3 python app.py
```

Windows PowerShell:

```powershell
$env:CORPOFIT_DB_PATH = "C:\caminho\seguro\corpofit.sqlite3"
python app.py
```

A aplicação também aceita `CORPOFIT_SECRET_KEY` para definir uma chave estável de sessão e validação de formulários, além de `HOST` e `PORT` para configuração da interface de rede e da porta. Localmente, os valores padrão são suficientes. Não compartilhe a chave nem a salve no repositório. O banco SQLite contém histórico antropométrico potencialmente sensível: mantenha-o em local seguro e faça cópias de segurança com cuidado.

## GitHub Pages e hospedagem na internet

**GitHub Pages não executa este projeto.** Pages serve arquivos estáticos; o CorpoFit precisa de um servidor Python/Flask e grava informações em SQLite. Para acessá-lo pela internet, seria necessário hospedar o backend em um serviço que execute aplicações Python e ofereça armazenamento persistente. Um arquivo SQLite dentro de um contêiner temporário pode desaparecer em reinicializações ou novas implantações.

Esta versão não inclui autenticação nem separação dos registros por usuário. Portanto, não a exponha publicamente nem use uma instância compartilhada com dados reais de clientes. Antes de uma implantação pública, implemente controle de acesso, armazenamento persistente, segredo configurado no ambiente, HTTPS, política de retenção e uma revisão dos requisitos de privacidade aplicáveis. Para produção, use um servidor WSGI adequado em vez do servidor de desenvolvimento do `python app.py`.

## Métodos e limitações

A equação Navy masculina usa abdômen, pescoço e estatura; a feminina usa cintura, quadril, pescoço e estatura. As fórmulas são expressas diretamente em centímetros. Para esse método, a densidade apresentada é derivada do percentual estimado pela relação inversa de Siri, não uma medição independente.

Jackson–Pollock estima densidade corporal a partir da soma das dobras e da idade; a fórmula de Siri converte a densidade em percentual (`% de gordura = 495 / densidade − 450`). O JP3 utiliza três sítios específicos para cada equação. O JP7 utiliza peitoral, axilar média, tricipital, subescapular, abdominal, supra-ilíaca e coxa. A equação feminina original estudou mulheres de 18 a 55 anos e recomenda cautela acima dos 40; a masculina estudou adultos de 18 a 61 anos. A técnica de adipometria, os pontos anatômicos e as características da população influenciam o resultado.

As faixas de composição corporal são referências gerais para adultos, não são específicas por idade e não devem ser tratadas como metas individuais. O IMC é apenas complementar e não distingue gordura, músculo e osso.

## Privacidade

O aplicativo não tem login e não envia os registros a serviços externos. Em execução local, o banco fica no computador que executa o servidor. Uma prévia hospedada grava no ambiente de execução hospedado, não no dispositivo da pessoa que a acessa. Para preservar a privacidade, use a execução local e prefira apelidos em vez de dados identificáveis.

## Referências metodológicas

- Hodgdon JA, Beckett MB. Equações de circunferência para estimar percentual de gordura (equações referenciadas em estudo de comparação): [Shaheen et al., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6650177/).
- Potter AW et al. *Circumference-Based Predictions of Body Fat Revisited*, 2022: [estudo completo](https://pmc.ncbi.nlm.nih.gov/articles/PMC9008774/).
- Jackson AS, Pollock ML. [Equações generalizadas para prever densidade corporal de homens, estudo original de 1978](https://pubmed.ncbi.nlm.nih.gov/718832/).
- Jackson AS, Pollock ML, Ward A. [Equações generalizadas para prever densidade corporal de mulheres, estudo original de 1980](https://pubmed.ncbi.nlm.nih.gov/7402053/).
- Fórmulas e sítios Jackson–Pollock: [guia de avaliação JP3/JP7](https://www.topendsports.com/testing/density-jackson-pollock.htm). Limitações das equações: [Nevill et al., 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2891061/).
- Jagim AR et al. Validação de equações de dobras cutâneas em atletas, 2023: [Frontiers in Sports and Active Living](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2023.1240252/full).
- CDC. [About Body Mass Index](https://www.cdc.gov/bmi/about/index.html).
- American Council on Exercise. [Referência ACE de composição corporal](https://www.acefitness.org/about-ace/press-room/in-the-news/8602/body-fat-percentage-charting-averages-in-men-and-women-very-well-health/).

## Licença

Este projeto é distribuído sob a licença MIT. Consulte [`LICENSE`](LICENSE).
