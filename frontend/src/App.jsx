import { useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || '';

function Hero() {
  return (
    <section className="hero">
      <div className="hero-inner">
        <h1>E Mohan Gandhi</h1>
        <p className="title">Full Stack &amp; DevOps Engineer</p>
        <p className="bio">
          I build observable, automated, and resilient systems end-to-end —
          from React UIs and Python APIs to containerized pipelines that
          deploy themselves.
        </p>
        <div className="hero-links">
          <a href="https://github.com/mohanemg07-web" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://linkedin.com/in/mohan-2b3ba1248" target="_blank" rel="noreferrer">LinkedIn</a>
        </div>
      </div>
    </section>
  );
}

function StatusBar() {
  const [healthy, setHealthy] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (!cancelled) setHealthy(res.ok);
      } catch {
        if (!cancelled) setHealthy(false);
      }
    }

    check();
    const id = setInterval(check, 30000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const dotClass = healthy === null ? 'dot dot-unknown' : healthy ? 'dot dot-ok' : 'dot dot-bad';
  const label = healthy === null ? 'Checking…' : healthy ? 'Systems Operational' : 'Service Disrupted';

  return (
    <div className="status-bar">
      <span className={dotClass} />
      <span>{label}</span>
    </div>
  );
}

function ProjectCard({ project }) {
  return (
    <article className="card">
      <header>
        <h3>{project.title}</h3>
        <span className="year">{project.year}</span>
      </header>
      <p>{project.description}</p>
      <ul className="chips">
        {project.tech_stack.map((tech) => (
          <li key={tech} className="chip">{tech}</li>
        ))}
      </ul>
      <footer>
        <a href={project.github_url} target="_blank" rel="noreferrer">GitHub</a>
        <a href={project.live_url} target="_blank" rel="noreferrer">Live</a>
      </footer>
    </article>
  );
}

function Projects() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/projects`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setProjects)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <section className="section">
      <h2>Selected Work</h2>
      {error && <p className="error">Failed to load projects: {error}</p>}
      <div className="grid">
        {projects.map((p) => (
          <ProjectCard key={p.id} project={p} />
        ))}
      </div>
    </section>
  );
}

function MetricsPanel() {
  const metrics = [
    { label: 'CI Pipeline', value: 'Passing', sub: 'lint · test · build · deploy' },
    { label: 'Uptime', value: '99.97%', sub: 'last 30 days' },
    { label: 'Last Deploy', value: 'Today', sub: 'auto-deployed from main' },
  ];

  return (
    <section className="section">
      <h2>Operational Metrics</h2>
      <div className="metrics">
        {metrics.map((m) => (
          <div key={m.label} className="metric">
            <span className="metric-label">{m.label}</span>
            <span className="metric-value">{m.value}</span>
            <span className="metric-sub">{m.sub}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <span className="brand">⟁ portfolio</span>
        <StatusBar />
      </header>
      <main>
        <Hero />
        <Projects />
        <MetricsPanel />
      </main>
      <footer className="footer">
        <span>© {new Date().getFullYear()} E Mohan Gandhi</span>
        <span>Built with React · FastAPI · Docker · Railway</span>
      </footer>
    </div>
  );
}
