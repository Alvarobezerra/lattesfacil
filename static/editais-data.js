/* Recorte documental do PDF de concepção; não é um catálogo atualizado de chamadas. */
(function(root){
  'use strict';
  const amazon=['AC','AP','AM','MA','MT','PA','RO','RR','TO'];
  const northeast=['AL','BA','CE','MA','PB','PE','PI','RN','SE'];
  const rows=[
    ['fapema','FAPEMA','Mobility CONFAP – Italy 2026','Estadual',['MA'],'2026-11-24',60000,'Por bolsista',['Doutorado','Sênior'],['Mobilidade'],[],'Todas',['Passagens','Bolsas'],'Vínculo com ICT do Maranhão e cooperação com a Itália.',true],
    ['amazonia','AMAZÔNIA+10','Expedições Científicas e Desafios da Amazônia','Regional',amazon,'2027-01-30',1500000,'Por projeto',['Bolsas previstas'],['Custeio','Logística'],['SisGen','SISBIO'],'Ciências Biológicas',['Custeio','Bolsas'],'Consórcio com pelo menos duas ICTs de estados distintos da Amazônia Legal.',true],
    ['cnpq','CNPq / MIR','Chamada 23/2026 — Programa Lélia Gonzalez','Federal',[],'2026-12-19',400000,'Por projeto',['IC','Mestrado','Pós-Doc'],[],['CEP / CNS 510'],'Ciências Humanas',['Custeio','Bolsas'],'Projetos coordenados por doutores vinculados a ICTs.',false],
    ['finep','FINEP','Rede EUREKA 2026','Federal',[],'2026-11-23',3000000,'Por projeto',[],['TRL 4–7'],['TRL / Empresas'],'Engenharias',['Subvenção','Custeio'],'Cooperação Brasil–Suécia com empresa e ICT.',true],
    ['confap','CONFAP','Apoio Complementar MSCA Doctoral Networks','Nacional',['AM','ES','PB','CE','RO','PR'],'2026-11-24',null,'Misto FAP + União Europeia',['Doutorado'],['Open Science'],[],'Todas',['Bolsas'],'Redes doutorais com instituições dos estados participantes e parceiros europeus.',true],
    ['faperj','FAPERJ','Edital 36/2026 — Bolsa de Iniciação Científica','Estadual',['RJ'],'2026-12-15',null,'Tabela de bolsas',['IC'],[],[],'Todas',['Bolsas'],'Orientador e bolsista vinculados a ICT do Rio de Janeiro.',false],
    ['fapemig','FAPEMIG','Chamada 19/2026 — Minas para o Mundo','Estadual',['MG'],'2027-01-20',2000000,'Por projeto',['Bolsas previstas'],['Internacional'],[],'Todas',['Custeio','Bolsas'],'Doutor vinculado a ICT mineira e cooperação internacional.',true],
    ['embrapii','EMBRAPII','Chamada Interna 03/2026 — Descarbonização (IKI)','Federal',[],'2026-12-15',5000000,'Por projeto',[],['TRL 5–8'],['TRL / Empresas','NDA / Patente'],'Engenharias',['Subvenção'],'Destinada a unidades EMBRAPII e pilotos industriais.',true],
    ['bndes','BNDES','BNDESPAR/FINEP — FIP Conexões Startups','Federal',[],'2026-11-23',50000000,'Fundo, não por projeto',[],['Capital','FIP'],['CVM'],'Ciências Sociais Aplicadas',['Capital'],'Aporte em fundo de investimento; não equivale a auxílio individual ao pesquisador.',true],
    ['capes','CAPES / INEP','Edital Conjunto 26/2026 — Licenciaturas','Federal',[],'2026-12-10',0,'Sem repasse direto',[],['Educação'],['CEP / CNS 510'],'Ciências Humanas',['Apoio logístico'],'Apoio logístico e coleta amostral em instituições de ensino superior.',false]
  ];
  const items=rows.map(([id,agency,title,sphere,ufs,deadline,amount,basis,scholarships,tags,compliance,area,expenses,eligibility,network])=>({id,agency,title,sphere,ufs,deadline,amount,basis,scholarships,tags,compliance,area,expenses,eligibility,network,pdf:'/editais-pdf/'+id+'.pdf'}));
  const normalize=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const days=(date,now=today())=>date?Math.round((Date.parse(date+'T00:00:00Z')-Date.parse(now+'T00:00:00Z'))/86400000):null;
  function matches(e,f,now=today()){
    const text=normalize([e.title,e.agency,e.area,e.eligibility,...e.tags,...e.scholarships,...e.compliance].join(' '));
    if(f.q&&!normalize(f.q).split(/\s+or\s+/).some(group=>group.trim().split(/\s+/).every(word=>text.includes(word))))return false;
    if(f.national===false&&!e.ufs.length)return false;
    const territory=f.region==='amazon'?amazon:f.region==='northeast'?northeast:f.uf?[f.uf]:[];
    if(territory.length&&!(e.ufs.length?e.ufs.some(uf=>territory.includes(uf)):f.national))return false;
    if(f.agency&&e.agency!==f.agency||f.sphere&&e.sphere!==f.sphere||f.area&&e.area!==f.area&&e.area!=='Todas')return false;
    if(f.compliance&&!e.compliance.includes(f.compliance)||f.scholarship&&!e.scholarships.includes(f.scholarship)||f.expense&&!e.expenses.includes(f.expense))return false;
    if(f.money){if(e.amount===null)return false;const a=e.amount;if(f.money==='micro'&&!(a>0&&a<=30000)||f.money==='small'&&!(a>30000&&a<=100000)||f.money==='medium'&&!(a>100000&&a<=400000)||f.money==='large'&&!(a>400000)||f.money==='none'&&a!==0)return false;}
    const d=days(e.deadline,now);
    if(f.term==='urgent'&&!(d!==null&&d>=0&&d<=15)||f.term==='medium'&&!(d>=16&&d<=45)||f.term==='long'&&!(d>45)||f.term==='closed'&&!(d!==null&&d<0)||f.term==='continuous'&&e.deadline!==null)return false;
    if(f.radar==='scholarships'&&!e.scholarships.length||f.radar==='network'&&!e.network||f.radar==='urgent'&&!(d!==null&&d>=0&&d<=15))return false;
    return true;
  }
  const api={items,amazon,northeast,normalize,today,days,matches};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.EditaisCatalog=api;
})(globalThis);
