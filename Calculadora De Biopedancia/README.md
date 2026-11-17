CorpoFit — Calculadora de composição corporal
Aplicação local para registrar avaliações antropométricas e acompanhar tendências de composição corporal. A experiência oferece protocolos por circunferências e por dobras cutâneas, indicadores complementares, histórico em SQLite, gráficos SVG e exportação CSV.
Os resultados são estimativas populacionais, não diagnóstico nem substituto de avaliação profissional. Para comparar tendências, repita a medida com o mesmo protocolo, técnica e condições.
Recursos
Equação de circunferências da Marinha dos EUA, com entradas específicas para as equações masculina e feminina.
Jackson–Pollock de três sítios, com conjuntos específicos para cada equação, e de sete sítios para ambas as equações: peitoral, axilar média, tricipital, subescapular, abdominal, supra-ilíaca e coxa. As equações estimam densidade corporal e o modelo de Siri converte a densidade em percentual.
Percentual de gordura, densidade corporal, massa de gordura, massa livre de gordura, IMC e, para circunferências, razão cintura/estatura.
Perfis locais, avaliações com data, edição e exclusão, filtro por perfil, comparação de variação, gráficos SVG de peso, percentual de gordura e massa livre de gordura, CSV e relatório para imprimir/salvar como PDF.
Formulário guiado, validação no navegador e no servidor, dicas de medição, unidades exclusivamente métricas (kg, cm e mm) e tema claro/noturno.
Requisitos
Python 3.11 ou mais recente e pip.
Executar localmente
Bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
Abra http://127.0.0.1:3000. O banco é criado automaticamente em instance/corpofit.sqlite3. Para mudar localmente a localização dos dados, defina CORPOFIT_DB_PATH. Não coloque o banco em uma pasta sincronizada/publicada se isso puder expor informações pessoais.
O servidor escuta em 127.0.0.1 por padrão. Em ambiente de desenvolvimento hospedado que exija escuta externa, execute com HOST=0.0.0.0 PORT=3000 python app.py; não exponha essa configuração publicamente sem adicionar autenticação, armazenamento durável, transporte seguro e uma política de privacidade.
Testes
Bash
python -m unittest discover -s tests -v
Métodos e interpretação
A equação Navy masculina calcula o percentual a partir da diferença entre abdômen e pescoço e da altura. A equação feminina usa cintura, quadril, pescoço e altura. O app aplica formas algébricas equivalentes formuladas diretamente para centímetros; não há entradas, conversões ou seletores imperiais. A densidade apresentada para esse protocolo é derivada de BF% pela relação inversa de Siri, não uma medição independente.
Jackson–Pollock estima densidade corporal a partir da soma de dobras cutâneas e idade. O JP3 usa três sítios específicos para cada equação. O JP7 usa peitoral, axilar média, tricipital, subescapular, abdominal, supra-ilíaca e coxa. Depois, a fórmula de Siri (% gordura = 495 / densidade − 450) produz o percentual estimado. A equação feminina original estudou mulheres de 18 a 55 anos e recomenda cautela acima dos 40; a masculina estudou adultos de 18 a 61 anos. A técnica de adipometria e os pontos anatômicos influenciam o resultado, e as equações quadráticas podem não representar bem medidas fora da amostra original.
As faixas de composição corporal são referências gerais ACE para adultos, segmentadas pelas equações masculina/feminina; não são idade-específicas nem adequadas como metas individuais. O IMC é mostrado apenas como triagem complementar e não distingue gordura, músculo e osso. Pessoas com resultados inesperados, condições clínicas ou necessidades específicas devem discutir a avaliação com um profissional habilitado.
Privacidade e uso pretendido
O app não possui login e não envia registros para serviços externos. O banco SQLite fica no ambiente onde o aplicativo executa: em execução local, no computador do usuário; na prévia hospedada do Manus, no ambiente de execução hospedado — não no telefone/computador de quem acessa. A prévia é para demonstração; não insira nela dados identificáveis ou medições reais de clientes. Use apelidos e rode localmente para manter a base no próprio computador.
O banco local e os arquivos .env são excluídos pelo .gitignore; revise alterações antes de qualquer commit e nunca envie dados identificáveis ao GitHub. Esta versão não tem login nem isolamento por usuário. Uma instância pública compartilhada exigiria autenticação, isolamento por usuário, banco e armazenamento persistentes, HTTPS e análise dos requisitos legais de privacidade aplicáveis. Um contêiner hospedado pode perder arquivos SQLite durante reinicializações ou implantações.
Referências metodológicas
Hodgdon JA, Beckett MB. Equações de circunferência para estimar percentual de gordura (equações referenciadas em estudo de comparação): Shaheen et al., 2019.
Potter AW et al. Circumference-Based Predictions of Body Fat Revisited, 2022: estudo completo.
Jackson AS, Pollock ML, Ward A. Equações generalizadas para estimar densidade corporal de mulheres, 1980, e equações de homens, 1978; fórmulas analisadas por Nevill et al., 2008.
Jackson AS, Pollock ML. Equações generalizadas para prever densidade corporal de homens, estudo original de 1978; Jackson AS, Pollock ML, Ward A. Equações generalizadas para prever densidade corporal de mulheres, estudo original de 1980. Fórmulas e sítios JP3/JP7: guia de avaliação Jackson–Pollock.
Jagim AR et al. Validação de equações de dobras cutâneas em atletas, 2023: Frontiers in Sports and Active Living.
CDC. About Body Mass Index.
American Council on Exercise. Referência ACE de composição corporal.
Licença
MIT. Consulte LICENSE.