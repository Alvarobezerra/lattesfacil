/* Prévia em memória. Nenhum conteúdo de projeto é persistido ou transmitido. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const packs = ['Bancada, Biológicas & Farmácia', 'Ensaios Clínicos & Intervenções', 'Saúde Coletiva, Revisões & PTT', 'Computação, IA & Ciência de Dados', 'Engenharias, Indústria & TRL', 'Agrárias, Alimentos & Ambientais', 'Humanas, Sociais Aplicadas & Artes', 'Big Science, Química & Consórcios'];
  const folders = ['Identidade e planejamento', 'Ética e protocolos', 'Execução e etapas', 'Congressos e certificados', 'Produtos e versões', 'Prestação de contas'];
  const stages = ['A fazer', 'Em execução', 'Revisar', 'Concluído'];
  const pillars = [
    ['Identidade e natureza', 'Objetivo, natureza, vigência e módulos de especialidade.'],
    ['Equipe e papéis por projeto', 'Coordenador, orientador, parceiro e orientando. Convites e permissões em preparação.'],
    ['Carteira de fomentos', 'Múltiplas agências por projeto e produto. Funding e relatórios por processo em preparação.'],
    ['Marcos e repositório', 'Etapas e entregas do quadro. Preservação de arquivos após a defesa em preparação.'],
    ['Produtos, CRediT e versões', 'Autoria, versões e agrupamento de obras multilíngues. Integração em preparação.'],
    ['Propagação para o Lattes', 'Uma aprovação prepara registros para orientador e coautores. Sincronização e dossiê em preparação.']
  ];
  const task = (id, title, folder, stage, owner, due = '') => ({id, title, folder, stage, owner, due});
  const projects = [
    {id:'exemplo-babacu', title:'Bioprodutos do Babaçu', area:'Ciências Biológicas', nature:'Pesquisa', role:'Coordeno', status:'Em andamento', objective:'Cenário ilustrativo inspirado no resumo executivo; não representa o andamento real do grupo.', start:'2025-01-01', end:'2027-12-31', packs:[0,5], image:'proj-babacu.jpg', phase:'Ensaios biológicos', health:'Revisões pendentes', indicator:['Amostras / N experimental','24 / 36'], funding:'FAPEMA · FINEP · CAPES · BNB (exemplo)', compliance:'CEUA: renovação a acompanhar · SisGen: conferência prevista · INPI: verificar antes de submeter.', tasks:[task('b1','Processar lotes de amostras',2,0,'Orientanda A'),task('b2','Conferir proteção intelectual com o NIT',4,0,'Coordenador'),task('b3','Renovar protocolo CEUA',1,0,'Coordenador'),task('b4','Ensaios celulares',2,1,'Orientanda A'),task('b5','Preparar relatório de fomento',5,1,'Orientando B'),task('b6','Revisar manuscrito e contribuições CRediT',4,2,'Orientanda A'),task('b7','Validar certificado de congresso',3,2,'Orientando B'),task('b8','Conferir cadastro SisGen',1,3,'Coordenador'),task('b9','Concluir extração e caracterização',2,3,'Equipe')], activity:[]},
    {id:'exemplo-mhealth', title:'mHealth e educação em saúde', area:'Ciências da Saúde', nature:'Desenvolvimento tecnológico', role:'Colaboro', status:'Em andamento', objective:'Cenário ilustrativo de colaboração em produto técnico e tecnológico.', start:'2026-01-01', end:'2027-06-30', packs:[2,3], image:'proj-mhealth.jpg', phase:'Validação do produto', health:'Check-in previsto', indicator:['Etapas de validação','1 / 3'], funding:'Carteira de fomentos a definir', compliance:'CEP/CAAE e direitos do software: conferir conforme o projeto.', tasks:[task('m1','Preparar roteiro de validação',2,1,'Parceira A'),task('m2','Revisar versão do produto educacional',4,2,'Parceiro B'),task('m3','Definir plano de pesquisa',0,3,'Equipe')], activity:[]}
  ];
  // A URL carrega somente o ID público da referência. Nenhuma pesquisa privada é persistida.
  const editalId = new URLSearchParams(location.search).get('edital');
  const edital = window.EditaisCatalog?.items.find(item => item.id === editalId);
  if (edital) {
    const proposalId = 'edital-' + edital.id;
    const importedTasks = [
      task(proposalId+'-revisao','Conferir edital original, elegibilidade e retificações',0,0,'Coordenação'),
      task(proposalId+'-submissao','Preparar proposta para submissão',0,0,'Coordenação',edital.deadline || ''),
      task(proposalId+'-contas','Revisar rubricas e obrigações de prestação de contas',5,0,'Coordenação')
    ];
    if(edital.scholarships.length) importedTasks.push(task(proposalId+'-bolsas','Planejar seleção e indicação de bolsistas: '+edital.scholarships.join(', '),2,0,'Coordenação'));
    const packIds = [];
    if(edital.compliance.some(c=>['SisGen','SISBIO','CEUA'].includes(c)))packIds.push(0);
    if(edital.compliance.includes('CEP / CNS 510'))packIds.push(edital.area==='Ciências Humanas'?6:2);
    if(edital.compliance.includes('TRL / Empresas'))packIds.push(4);
    projects.push({id:proposalId,title:edital.title,area:edital.area==='Todas'?'A definir':edital.area,nature:'Pesquisa',role:'Coordeno',status:'Planejamento',objective:'Rascunho temporário a partir de referência documental. Confira requisitos e datas antes de preparar a candidatura.',start:'',end:'',packs:packIds,phase:'Preparação da candidatura',health:'Revisão do edital necessária',indicator:['Submissão (referência)',edital.deadline || 'A confirmar'],funding:edital.agency+' · '+edital.basis+' · '+(edital.amount===null?'Valor a conferir':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(edital.amount)),compliance:edital.eligibility+' Requisitos: '+(edital.compliance.join(', ')||'A conferir'),tasks:importedTasks,activity:['Rascunho preparado a partir do buscador. Nenhum projeto foi salvo.']});
    if(!location.hash)history.replaceState(null,'',location.pathname+location.search+'#'+proposalId);
  }
  let activeFolder = '', currentId = '';
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  function el(tag, text = '', className) { const node = document.createElement(tag); node.textContent = text; if(className) node.className = className; return node; }
  function button(text, action, className = 'button') { const node = el('button',text,className); node.type='button'; node.addEventListener('click',action); return node; }
  const current = () => projects.find(p=>p.id===location.hash.slice(1));
  const completed = p => p.tasks.filter(t=>t.stage===3).length;
  const progress = p => p.tasks.length ? Math.round(completed(p)/p.tasks.length*100) : 0;
  function meter(p) { const wrap=el('div','','project-progress');const bar=el('progress');bar.max=100;bar.value=progress(p);bar.setAttribute('aria-label','Entregas concluídas');wrap.append(el('span',`${completed(p)} de ${p.tasks.length} entregas concluídas · ${progress(p)}%`),bar);return wrap; }
  function summary(target, values) { target.replaceChildren(...values.map(([label,value])=>{const card=el('div','','panel');card.append(el('strong',value),el('p',label));return card;})); }
  function openProject(p, review = false) { activeFolder=''; if(location.hash.slice(1)===p.id) route(); else location.hash=p.id; if(review) requestAnimationFrame(()=>$('projectBoard').scrollIntoView({block:'start'})); }
  function projectCard(p) {
    const card=el('article','','panel project-card');
    if(p.image){const img=el('img');img.src='/img/projetos/'+p.image;img.alt='';img.loading='lazy';card.append(img);}
    card.append(el('span',p.health,'project-badge'),el('h3',p.title),el('small',`${p.nature} · ${p.phase}`),el('p',p.packs.map(i=>packs[i]).join(' · ') || 'Sem módulo selecionado'),meter(p),el('small',`${p.tasks.filter(t=>t.stage===2).length} entregas para revisão · ${p.status}`),button('Abrir projeto',()=>openProject(p)));
    return card;
  }
  function renderHub() {
    summary($('projectSummary'),[['Projetos nesta prévia',projects.length],['Entregas para revisar',projects.reduce((n,p)=>n+p.tasks.filter(t=>t.stage===2).length,0)],['Sob minha coordenação',projects.filter(p=>p.role==='Coordeno').length]]);
    const query=normalize($('projectSearch').value.trim());
    const visible=projects.filter(p=>(!query||normalize(p.title+' '+p.area).includes(query))&&(!$('projectRole').value||p.role===$('projectRole').value)&&(!$('projectStatus').value||p.status===$('projectStatus').value));
    $('projectCount').textContent=`${visible.length} de ${projects.length} projetos nesta prévia`;
    $('projectEmpty').hidden=visible.length>0;
    const featured=visible.find(p=>p.role==='Coordeno'&&p.tasks.some(t=>t.stage===2)) || visible[0];
    $('projectFeatured').hidden=!featured;$('projectFeatured').replaceChildren();
    if(featured){const content=el('div','','featured-content');content.append(el('span','EM DESTAQUE · DADOS DEMONSTRATIVOS','featured-label'),el('h2',featured.title),el('p',`${featured.phase} · ${featured.tasks.filter(t=>t.stage===2).length} entregas aguardando revisão`),meter(featured),button('Continuar projeto',()=>openProject(featured),'button primary'));if(featured.image){const img=el('img');img.src='/img/projetos/'+featured.image;img.alt='';$('projectFeatured').append(img);}$('projectFeatured').append(content);}
    $('projectList').replaceChildren();
    for(const [role,title] of [['Coordeno','Continuar executando · Projetos que coordeno'],['Colaboro','Projetos em que colaboro']]){const list=visible.filter(p=>p.role===role);if(!list.length)continue;const section=el('section');const grid=el('div','','project-grid');grid.append(...list.map(projectCard));section.append(el('h2',title,'project-rail-title'),grid);$('projectList').append(section);}
  }
  function renderBoard(p) {
    const visible=p.tasks.filter(t=>activeFolder===''||t.folder===Number(activeFolder));
    $('projectFolders').replaceChildren(...[['','Todas as pastas'],...folders.map((name,i)=>[String(i),name])].map(([id,name])=>{const count=p.tasks.filter(t=>id===''||t.folder===Number(id)).length;const b=button(`${name} (${count})`,()=>{activeFolder=id;renderBoard(p);});b.setAttribute('aria-pressed',String(activeFolder===id));return b;}));
    $('boardCount').textContent=`${visible.length} entregas nesta seleção`;
    $('projectBoard').replaceChildren(...stages.map((stage,index)=>{
      const col=el('section','','board-column stage-'+index);const tasks=visible.filter(t=>t.stage===index);col.append(el('h4',`${stage} · ${tasks.length}`));
      if(!tasks.length)col.append(el('p','Nenhuma entrega nesta etapa.','muted'));
      for(const t of tasks){const card=el('article','','delivery-card');card.append(el('small',folders[t.folder]),el('h5',t.title),el('p',t.owner),el('small',t.due?'Prazo: '+new Date(t.due+'T12:00:00').toLocaleDateString('pt-BR'):'Sem prazo definido'));
        if(index<3){const action=index===2?'Simular aprovação':index===1?'Enviar para revisão':'Iniciar entrega';
          if(index===2&&p.role!=='Coordeno')card.append(el('small','Aguardando coordenação'));
          else card.append(button(action,()=>{t.stage++;p.activity.unshift(`${action}: ${t.title}`);renderWorkspace(p);renderHub();$('projectFeedback').textContent=index===2?'Aprovação simulada. Nenhum registro foi enviado ao Lattes.':'Etapa atualizada nesta prévia.';const next=$('projectBoard').querySelector('.stage-'+t.stage+' h4');next.tabIndex=-1;next.focus();}));
        } else card.append(el('small','Validado na prévia · Sem sincronização'));
        col.append(card);
      }return col;
    }));
  }
  function renderWorkspace(p) {
    $('workspaceTitle').textContent=p.title;$('workspaceMeta').textContent=`${p.nature} · ${p.role} · ${p.status}`;$('workspaceObjective').textContent=p.objective;
    $('workspacePacks').replaceChildren(...p.packs.map(i=>el('span','Pack '+(i+1)+' · '+packs[i],'project-badge')));
    summary($('workspaceMetrics'),[['Entregas concluídas',progress(p)+'%'],p.indicator,['Para revisão',p.tasks.filter(t=>t.stage===2).length]]);
    renderBoard(p);
    const sections=[['Radar de prazos e protocolos',p.compliance],['Fomentos e metas',p.funding+'. A comparação previsto × entregue por processo está em preparação.'],['Esteira editorial e cobertura Lattes',`${p.tasks.filter(t=>t.folder===4).length} entregas de produtos e versões · ${completed(p)} entregas validadas na prévia · 0 sincronizadas. Fluxo previsto: dados, rascunho, submissão, DOI e Lattes.`],['Check-in da equipe','Cadência prevista: semanal. Conversas, convites e notificações ainda não estão ativos.'],['Atividade desta prévia',p.activity.slice(0,4).join(' • ')||'Nenhuma alteração nesta sessão. Este histórico temporário não é um log de auditoria.'],['Trajetória do aluno convidado',`${completed(p)} entregas validadas neste exemplo. A futura atribuição por autor alimentará a trajetória e a fila individual do Lattes. Convites, planos e pagamentos em preparação.`]];
    $('projectMonitoring').replaceChildren(...sections.map(([title,text])=>{const card=el('article','','panel project-card');card.append(el('h3',title),el('p',text));return card;}));
    $('projectPillars').replaceChildren(...pillars.map(([name,description],index)=>{const card=el('article','','panel project-card');card.append(el('h3',name),el('p',description));if(index===0)card.append(el('small',`${p.area} · Vigência: ${p.start||'a definir'} a ${p.end||'a definir'}`));return card;}));
  }
  function route() {
    const p=current();$('projectHub').hidden=!!p;$('projectWorkspace').hidden=!p;
    if(!p){currentId='';renderHub();return;}
    if(currentId!==p.id){activeFolder='';$('projectFeedback').textContent='';currentId=p.id;}
    renderWorkspace(p);$('workspaceTitle').focus();
  }
  function validate(form,names){for(const name of names){const field=form.elements.namedItem(name);field.setCustomValidity(field.value.trim()?'':'Preencha este campo.');if(!field.reportValidity())return false;}return true;}
  $('projectPackOptions').replaceChildren(...packs.map((name,i)=>{const label=el('label','','pack-option');const input=el('input');input.type='checkbox';input.name='packs';input.value=String(i);label.append(input,el('span',name));return label;}));
  $('deliveryFolder').replaceChildren(...folders.map((name,i)=>{const option=el('option',name);option.value=String(i);return option;}));
  ['projectSearch','projectRole','projectStatus'].forEach(id=>$(id).addEventListener('input',renderHub));
  $('clearFilters').addEventListener('click',()=>{['projectSearch','projectRole','projectStatus'].forEach(id=>$(id).value='');renderHub();$('projectSearch').focus();});
  $('backProjects').addEventListener('click',()=>{location.hash='';route();$('projectSearch').focus();});
  $('newProject').addEventListener('click',()=>$('projectDialog').showModal());
  $('cancelProject').addEventListener('click',()=>$('projectDialog').close());
  $('newDelivery').addEventListener('click',()=>$('deliveryDialog').showModal());
  $('cancelDelivery').addEventListener('click',()=>$('deliveryDialog').close());
  $('projectForm').addEventListener('submit',event=>{
    event.preventDefault();const form=event.currentTarget;if(!validate(form,['title','area']))return;const v=new FormData(form);
    const end=form.elements.namedItem('end');end.setCustomValidity(v.get('start')&&v.get('end')&&v.get('end')<v.get('start')?'O término deve ser igual ou posterior ao início.':'');if(!end.reportValidity())return;
    const p={id:'rascunho-'+crypto.randomUUID(),title:v.get('title').trim(),area:v.get('area').trim(),objective:v.get('objective').trim(),nature:v.get('nature'),role:v.get('role'),start:v.get('start'),end:v.get('end'),packs:v.getAll('packs').map(Number),status:'Planejamento',phase:'Estruturação do projeto',health:'Planejamento',tasks:[],activity:[],indicator:['Indicador da pesquisa','A definir'],funding:'Nenhum fomento definido',compliance:'Nenhum protocolo definido. Selecione as exigências aplicáveis à pesquisa.'};
    projects.push(p);form.reset();$('projectDialog').close();renderHub();openProject(p);
  });
  $('deliveryForm').addEventListener('submit',event=>{event.preventDefault();const form=event.currentTarget;if(!validate(form,['title','owner']))return;const p=current();if(!p)return;const v=new FormData(form);p.tasks.push(task(crypto.randomUUID(),v.get('title').trim(),Number(v.get('folder')),0,v.get('owner').trim(),v.get('due')));p.activity.unshift('Entrega adicionada: '+v.get('title').trim());activeFolder='';form.reset();$('deliveryDialog').close();renderWorkspace(p);renderHub();$('projectFeedback').textContent='Entrega adicionada à coluna A fazer, apenas nesta prévia.';});
  for(const id of ['projectForm','deliveryForm'])$(id).addEventListener('input',event=>{if(event.target.setCustomValidity)event.target.setCustomValidity('');if(id==='projectForm')$('projectForm').elements.namedItem('end').setCustomValidity('');});
  window.addEventListener('hashchange',route);renderHub();route();
})();
