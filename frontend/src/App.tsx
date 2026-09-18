import { useMemo, useRef, useState, type DragEvent } from "react";
import { DEMO_ITEMS } from "./demo";
import { Icon } from "./icons";
import { buildPlan, DEFAULT_RULES, formatBytes, planToCsv } from "./organizer";
import type { PlanStatus, WebPlanItem } from "./types";

const REPOSITORY_URL = "https://github.com/DanielRobertoRibeiro/Organizador_Inteligente_De_Arquivos";
const CLI_COMMAND = 'organizer analyze --source "C:\\Users\\Daniel\\Downloads" --config config.json';

const statusLabel: Record<PlanStatus, string> = {
  planned: "Planejado",
  duplicate: "Duplicado",
  skipped: "Ignorado",
};

function downloadReport(items: readonly WebPlanItem[]) {
  const blob = new Blob(["\ufeff", planToCsv(items)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `organizer-web-${new Date().toISOString().replaceAll(":", "-")}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

function App() {
  const fileInput = useRef<HTMLInputElement>(null);
  const folderInput = useRef<HTMLInputElement>(null);
  const [items, setItems] = useState<WebPlanItem[]>(DEMO_ITEMS);
  const [isDemo, setIsDemo] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [filter, setFilter] = useState<"all" | PlanStatus>("all");
  const [query, setQuery] = useState("");
  const [notice, setNotice] = useState("Prévia demonstrativa carregada");

  const summary = useMemo(
    () => ({
      total: items.length,
      planned: items.filter((item) => item.status === "planned").length,
      duplicates: items.filter((item) => item.status === "duplicate").length,
      size: items.reduce((total, item) => total + item.size, 0),
    }),
    [items],
  );

  const visibleItems = useMemo(() => {
    const term = query.trim().toLocaleLowerCase("pt-BR");
    return items.filter((item) => {
      const statusMatches = filter === "all" || item.status === filter;
      const termMatches = !term || `${item.filename} ${item.category} ${item.target}`.toLocaleLowerCase("pt-BR").includes(term);
      return statusMatches && termMatches;
    });
  }, [filter, items, query]);

  async function analyze(files: readonly File[]) {
    if (!files.length) return;
    setIsAnalyzing(true);
    setNotice(`Calculando SHA-256 de ${files.length} arquivo${files.length === 1 ? "" : "s"}…`);
    try {
      const plan = await buildPlan(files);
      setItems(plan);
      setIsDemo(false);
      setFilter("all");
      setQuery("");
      setNotice("Análise concluída localmente — nada foi enviado");
    } catch {
      setNotice("Não foi possível ler um dos arquivos selecionados");
    } finally {
      setIsAnalyzing(false);
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    void analyze(Array.from(event.dataTransfer.files));
  }

  async function copyCommand() {
    await navigator.clipboard.writeText(CLI_COMMAND);
    setNotice("Comando da CLI copiado");
  }

  return (
    <div className="site-shell">
      <header className="hero" id="inicio">
        <nav className="nav page-width" aria-label="Navegação principal">
          <a className="brand" href="#inicio" aria-label="Organizador Inteligente — início">
            <span className="brand-mark"><Icon name="folder" /></span>
            <span>organiza<span className="brand-dot">.</span></span>
          </a>
          <div className="nav-links">
            <a href="#produto">Produto</a>
            <a href="#seguranca">Segurança</a>
            <a href="#arquitetura">Arquitetura</a>
          </div>
          <a className="button button-small button-ghost" href={REPOSITORY_URL} target="_blank" rel="noreferrer">
            <Icon name="github" /> Repositório
          </a>
        </nav>

        <div className="hero-grid page-width">
          <div className="hero-copy">
            <p className="eyebrow"><span className="pulse" /> Automação segura · Python + React</p>
            <h1>Seu caos digital,<br /><span>em ordem.</span></h1>
            <p className="hero-description">
              Classifique arquivos, encontre duplicados e revise cada movimento antes de alterar qualquer coisa.
              Previsível por regra. Seguro por padrão.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="#produto">Testar agora <Icon name="arrow" /></a>
              <button className="button button-text" onClick={() => void copyCommand()}><Icon name="terminal" /> Copiar comando CLI</button>
            </div>
            <div className="trust-list" aria-label="Diferenciais de segurança">
              <span><Icon name="check" /> 100% local</span>
              <span><Icon name="check" /> Zero uploads</span>
              <span><Icon name="check" /> Simulação padrão</span>
            </div>
          </div>

          <div className="hero-visual" aria-label="Resumo de uma análise de arquivos">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="floating-card main-card">
              <div className="card-topline"><span>ANÁLISE / 001</span><span className="live-dot">LOCAL</span></div>
              <div className="folder-illustration"><Icon name="folder" /></div>
              <div className="big-number">05</div>
              <p>arquivos analisados</p>
              <div className="progress"><span /></div>
              <div className="card-footer"><span>4 movimentos</span><span>1 duplicado</span></div>
            </div>
            <div className="floating-card hash-card"><Icon name="hash" /><div><strong>SHA-256</strong><span>conteúdo verificado</span></div></div>
            <div className="floating-card safe-card"><Icon name="shield" /><div><strong>Modo seguro</strong><span>nenhuma alteração</span></div></div>
          </div>
        </div>
      </header>

      <main>
        <section className="product-section" id="produto">
          <div className="page-width">
            <div className="section-heading">
              <div><p className="section-kicker">01 / Experimente</p><h2>Veja o plano antes<br />de mover.</h2></div>
              <p>Selecione arquivos reais para gerar uma prévia no seu navegador. O conteúdo nunca sai do seu dispositivo.</p>
            </div>

            <div className="workspace">
              <aside className="control-panel">
                <div className="panel-label"><span>ENTRADA</span><span>01</span></div>
                <div
                  className={`dropzone ${isDragging ? "is-dragging" : ""}`}
                  onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
                  onDragOver={(event) => event.preventDefault()}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                >
                  <div className="drop-icon"><Icon name="upload" /></div>
                  <h3>{isAnalyzing ? "Analisando…" : "Solte seus arquivos"}</h3>
                  <p>ou selecione uma opção abaixo</p>
                  <div className="picker-actions">
                    <button onClick={() => fileInput.current?.click()} disabled={isAnalyzing}>Arquivos</button>
                    <button onClick={() => folderInput.current?.click()} disabled={isAnalyzing}>Pasta</button>
                  </div>
                  <input ref={fileInput} type="file" multiple hidden onChange={(event) => void analyze(Array.from(event.target.files ?? []))} />
                  <input
                    ref={(node) => {
                      folderInput.current = node;
                      if (node) (node as HTMLInputElement & { webkitdirectory: boolean }).webkitdirectory = true;
                    }}
                    type="file"
                    multiple
                    hidden
                    onChange={(event) => void analyze(Array.from(event.target.files ?? []))}
                  />
                </div>

                <div className="privacy-note"><Icon name="lock" /><div><strong>Privacidade real</strong><span>Processamento feito no navegador. Nenhum upload.</span></div></div>

                <div className="rules-block">
                  <div className="rules-title"><span>REGRAS ATIVAS</span><span>{DEFAULT_RULES.length + 1}</span></div>
                  <div className="rule-chips">
                    {DEFAULT_RULES.map((rule) => <span className={`rule-chip tone-${rule.tone}`} key={rule.name}>{rule.name}<b>{rule.extensions.length}</b></span>)}
                    <span className="rule-chip tone-neutral">Outros<b>∞</b></span>
                  </div>
                </div>
              </aside>

              <div className="results-panel">
                <div className="results-header">
                  <div><span className="results-label">PLANO DE ORGANIZAÇÃO</span><span className={`mode-badge ${isDemo ? "" : "mode-live"}`}>{isDemo ? "DEMO" : "SEUS ARQUIVOS"}</span></div>
                  <div className="search-box"><Icon name="search" /><input aria-label="Buscar no plano" placeholder="Buscar arquivo…" value={query} onChange={(event) => setQuery(event.target.value)} /></div>
                </div>

                <div className="metric-row">
                  <div><span>Total</span><strong>{String(summary.total).padStart(2, "0")}</strong></div>
                  <div><span>Planejados</span><strong>{String(summary.planned).padStart(2, "0")}</strong></div>
                  <div><span>Duplicados</span><strong className="accent-warm">{String(summary.duplicates).padStart(2, "0")}</strong></div>
                  <div><span>Tamanho</span><strong>{formatBytes(summary.size)}</strong></div>
                </div>

                <div className="filter-row" role="group" aria-label="Filtrar plano">
                  {(["all", "planned", "duplicate"] as const).map((value) => (
                    <button className={filter === value ? "active" : ""} key={value} onClick={() => setFilter(value)}>
                      {value === "all" ? "Todos" : statusLabel[value]}
                    </button>
                  ))}
                  <span className="analysis-notice">{notice}</span>
                </div>

                <div className="file-table" role="table" aria-label="Plano de organização">
                  <div className="table-head" role="row"><span>Arquivo</span><span>Categoria</span><span>Destino</span><span>Status</span></div>
                  <div className="table-body">
                    {visibleItems.map((item) => (
                      <div className="file-row" role="row" key={item.id}>
                        <div className="file-name-cell"><span className="file-icon"><Icon name="file" /></span><div><strong>{item.filename}</strong><span>{formatBytes(item.size)} · {item.sha256.slice(0, 8)}</span></div></div>
                        <span className={`category category-${item.category.toLocaleLowerCase("pt-BR").normalize("NFD").replace(/[\u0300-\u036f]/g, "")}`}>{item.category}</span>
                        <span className="target-cell" title={item.target}>{item.target.replace("Arquivos organizados/", "…/")}</span>
                        <span className={`status status-${item.status}`}><i />{statusLabel[item.status]}</span>
                      </div>
                    ))}
                    {!visibleItems.length && <div className="empty-state">Nenhum item corresponde ao filtro.</div>}
                  </div>
                </div>

                <div className="results-footer">
                  <p><Icon name="shield" /> Esta prévia nunca move ou exclui arquivos.</p>
                  <button className="button button-export" onClick={() => downloadReport(items)} disabled={!items.length}><Icon name="download" /> Exportar CSV</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="safety-section" id="seguranca">
          <div className="page-width">
            <div className="section-heading light-heading">
              <div><p className="section-kicker">02 / Segurança</p><h2>Confiança não é<br />um detalhe.</h2></div>
              <p>A arquitetura assume que arquivos pessoais merecem proteção por padrão, não como configuração opcional.</p>
            </div>
            <div className="safety-grid">
              <article><span className="feature-index">01</span><Icon name="search" /><h3>Primeiro, simule.</h3><p>O plano completo aparece antes de qualquer alteração no disco.</p></article>
              <article className="feature-highlight"><span className="feature-index">02</span><Icon name="shield" /><h3>Nunca sobrescreva.</h3><p>Colisões recebem nomes numerados. O arquivo existente permanece intacto.</p></article>
              <article><span className="feature-index">03</span><Icon name="hash" /><h3>Compare conteúdo.</h3><p>SHA-256 identifica arquivos idênticos sem depender apenas do nome.</p></article>
              <article><span className="feature-index">04</span><Icon name="file" /><h3>Audite tudo.</h3><p>Logs e CSV registram origem, destino, estado e resultado de cada item.</p></article>
            </div>
          </div>
        </section>

        <section className="architecture-section" id="arquitetura">
          <div className="page-width architecture-grid">
            <div>
              <p className="section-kicker">03 / Arquitetura</p>
              <h2>Do navegador<br />ao sistema de arquivos.</h2>
              <p className="architecture-copy">A vitrine React oferece uma demonstração local e interativa. O núcleo Python executa a organização real com as mesmas regras de classificação e segurança.</p>
              <a className="text-link" href={REPOSITORY_URL} target="_blank" rel="noreferrer">Explorar o código <Icon name="arrow" /></a>
            </div>
            <div className="pipeline" aria-label="Arquitetura do projeto">
              <div className="pipeline-node"><span>01</span><div><b>React</b><small>Seleção e prévia local</small></div><Icon name="chevron" /></div>
              <div className="pipeline-node"><span>02</span><div><b>Regras JSON</b><small>Classificação previsível</small></div><Icon name="chevron" /></div>
              <div className="pipeline-node"><span>03</span><div><b>Python CLI</b><small>Planejamento e execução</small></div><Icon name="chevron" /></div>
              <div className="pipeline-node"><span>04</span><div><b>CSV + Log</b><small>Auditoria completa</small></div><Icon name="check" /></div>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="page-width footer-grid">
          <div className="brand footer-brand"><span className="brand-mark"><Icon name="folder" /></span><span>organiza<span className="brand-dot">.</span></span></div>
          <p>Software livre, local e construído para organizar sem surpresas.</p>
          <a href={REPOSITORY_URL} target="_blank" rel="noreferrer"><Icon name="github" /> GitHub</a>
          <span>MIT · 2026</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
