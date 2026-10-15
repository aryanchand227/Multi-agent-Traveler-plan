export function Footer() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--card)] py-6">
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm text-[var(--muted-foreground)]">
          AI Travel Planner — Multi-Agent Travel Planning Platform
        </p>
        <p className="text-xs text-[var(--muted-foreground)] mt-1">
          Powered by LangGraph + FastAPI + Next.js
        </p>
      </div>
    </footer>
  );
}
