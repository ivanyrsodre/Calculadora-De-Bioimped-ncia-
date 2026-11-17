Plano do projeto — CorpoFit
Objetivo
Aplicação web em português para estimar densidade corporal e percentual de gordura, útil para profissionais de educação física, nutricionistas e público geral. A interface usa a imagem de referência enviada como direção visual: painel limpo, controles de medidas à esquerda, resultados destacados à direita, cores violeta/azul e modos claro e noturno.
Implementação
Backend: Python 3.11+ com Flask e rotas server-rendered para cálculos, perfis/avaliações, edição, exclusão, impressão e exportação CSV; os gráficos recebem dados JSON embutidos na página.
Persistência: SQLite local em instance/corpofit.sqlite3, schema inicializado automaticamente e migrado sem apagar avaliações existentes. O banco, exports privados, ambientes virtuais e arquivos locais ficam ignorados pelo Git. A instalação é voltada a uso local; a documentação explicará que publicar uma instância multiusuário exige armazenamento persistente, controle de acesso e avaliação de privacidade.
Frontend: HTML semântico com Jinja, CSS responsivo e JavaScript sem framework. Gráficos SVG são desenhados pelo próprio app para evitar dependência de serviço externo. Tema escolhido pelo usuário salvo no navegador.
Organização: app.py cria a aplicação e registra rotas; corpofit/calculations.py implementa fórmulas e validações puras; corpofit/db.py encapsula schema e consultas SQLite; corpofit/routes.py lida com páginas e operações; templates/ contém formulários, resultado e histórico; static/css/ e static/js/ guardam tema, interações, validação client-side e gráficos; tests/ contém testes das equações e regras. requirements.txt, .gitignore, README.md, LICENSE e plan.md descrevem execução e compartilhamento.
Protocolos: estimativa por circunferências da Marinha dos EUA (equações específicas por sexo, reescritas algebricamente para operar diretamente em cm); Jackson–Pollock de 3 sítios (peitoral/abdômen/coxa para equação masculina; tríceps/supra-ilíaca/coxa para feminina) e de 7 sítios (peitoral, axilar média, tríceps, subescapular, abdômen, supra-ilíaca e coxa), com as equações masculina/feminina e conversão Siri. Peso em kg, estatura/circunferências em cm e dobras em mm; sem conversão nem seletor de unidades imperiais. Mostrar método, equação/referência e instruções de medição. Para o método Navy, a densidade será derivada da estimativa de percentual pela relação inversa de Siri, e isso será explicado na interface.
Indicadores: IMC, gordura em kg, massa livre de gordura em kg, razão cintura/estatura quando houver uma medida de cintura compatível (não calcular a partir do abdômen da equação Navy masculina); percentuais comparáveis somente entre avaliações com método igual. Categorias são orientativas e não diagnósticas. A aplicação não calculará prescrição de dieta, risco clínico nem escore de saúde.
Dados e análise: perfis identificados por nome/apelido e avaliações datadas; histórico filtrável por perfil, edição/exclusão, gráficos de peso, percentual de gordura e massa livre de gordura; comparação da variação apenas entre os dois registros mais recentes com o mesmo protocolo; CSV e página preparada para impressão/PDF pelo navegador.
Experiência: cadastro guiado, dicas de medição específicas, mensagens de validação legíveis, apenas unidades métricas, formulários responsivos e suporte a leitores de tela. Sem login nesta versão: não enviar dados pessoais para serviços externos.
Decisões de desenho
Movimento: minimalismo editorial de produto de saúde digital, evitando aparência de diagnóstico hospitalar.
Princípios: clareza das medidas; resultado transparente e contextualizado; baixa fricção para leigos; privacidade por padrão.
Cores: violeta/índigo como assinatura de dados e ação, azul-petróleo para confirmação; fundos claros frios e superfícies profundas no noturno. Texto e estados devem manter contraste acessível.
Layout: painel assimétrico de duas áreas em desktop: formulário amplo à esquerda e resumo de resultado ancorado à direita; em telas estreitas, fluxo vertical com resultado imediatamente após o cálculo.
Elementos marcantes: anel de percentual com progresso; chips de método/unidade; linha do tempo de avaliações como gráfico SVG.
Interação/animação: atualização do resultado após envio, confirmação breve ao salvar, animação curta no anel; respeitar prefers-reduced-motion; alternância de tema imediata e persistente.
Tipografia: Inter para interface e números, com fallback de sistema; títulos sem serifa de peso 650–750, campos e rótulos com hierarquia nítida e números tabulares.
Essência da marca: “Composição corporal em contexto, para acompanhar melhor cada avaliação”; personalidade: clara, respeitosa e prática.
Tom: direto, acolhedor e sem julgamento. Exemplos: “Informe as medidas feitas hoje.” e “Estimativa para acompanhar tendências, não um diagnóstico.”
Marca/logotipo: wordmark “CorpoFit” acompanhado de um monograma geométrico formado por dois arcos, sugerindo fita métrica e evolução.
Cor assinatura: violeta índigo #5946D8, ajustado no tema escuro para legibilidade.
Referências metodológicas
Potter et al. (2022), estudo sobre estimativas baseadas em circunferência e limites de concordância com DXA: https://pmc.ncbi.nlm.nih.gov/articles/PMC9008774/
Shaheen et al. (2019), método Navy e fórmulas de circunferência; comparação com BIA: https://pmc.ncbi.nlm.nih.gov/articles/PMC6650177/
CDC, IMC como indicador de triagem e suas limitações: https://www.cdc.gov/bmi/about/index.html
Nevill et al. (2008), avaliação das equações Jackson–Pollock: https://pmc.ncbi.nlm.nih.gov/articles/PMC2891061/
Jagim et al. (2023), validação de equações de dobras cutâneas e erro de estimativa: https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2023.1240252/full
Jackson & Pollock (1978), equações masculinas originais: https://pubmed.ncbi.nlm.nih.gov/718832/
Jackson, Pollock & Ward (1980), equações femininas originais: https://pubmed.ncbi.nlm.nih.gov/7402053/
Formulação e sítios das equações JP3/JP7: https://www.topendsports.com/testing/density-jackson-pollock.htm
Estas equações fornecem estimativas populacionais e podem divergir de DXA ou outras técnicas de referência; método e limitações serão exibidos junto dos resultados.