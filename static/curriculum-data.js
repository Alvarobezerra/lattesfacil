/* Regras de apresentação compartilhadas, sem mutações ou chamadas de rede. */
(() => {
  const production = new Set(['artigo','artigo_aceito','trabalho_evento','apresentacao','livro','capitulo','texto_jornal','patente','software','trabalho_tecnico','produto_tecnologico','outra_producao_bibliografica','outra_producao_tecnica','producao_artistica']);
  const normalize = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const group = item => production.has(item.categoria) ? 'producoes' : /^orientacao_/.test(item.categoria) ? 'orientacoes' : item.categoria === 'projeto' ? 'projetos' : 'outros';
  const needsAttention = item => item.categoria === 'artigo' && !String(item.doi || '').trim();
  function filter(items, { category = '', query = '', year = '', situation = '', selectedGroup = '' } = {}) {
    const q = normalize(query).trim();
    return items.filter(i => (!category || i.categoria === category) && (!year || String(i.ano || '') === year) &&
      (!selectedGroup || group(i) === selectedGroup) && (!situation || (situation === 'sem-doi' && needsAttention(i))) &&
      (!q || normalize([i.titulo, i.doi, i.veiculo, i.instituicao, ...(i.autores || [])].join(' ')).includes(q)));
  }
  function summary(items) {
    const authors = new Set();
    items.forEach(i => (i.autores || []).forEach(a => authors.add(normalize(a).trim())));
    return { productions: items.filter(i => production.has(i.categoria)).length, orientations: items.filter(i => i.categoria === 'orientacao_concluida').length,
      projects: items.filter(i => i.categoria === 'projeto').length, authors };
  }
  const api = { production, normalize, group, filter, needsAttention, summary };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else window.CurriculumData = api;
})();
