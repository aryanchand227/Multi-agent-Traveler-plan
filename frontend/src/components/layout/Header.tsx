"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="border-b border-[var(--border)] bg-[var(--card)] sticky top-0 z-40 backdrop-blur-md bg-opacity-90">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl">✈️</span>
          <span className="text-lg font-semibold tracking-tight">AI Travel Planner</span>
        </Link>
        <nav className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
          >
            Home
          </Link>
          <Link
            href="/plan"
            className="text-sm font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
          >
            Plan Trip
          </Link>
          <Link
            href="/preferences"
            className="text-sm font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
          >
            Preferences
          </Link>

          {isAuthenticated ? (
            <div className="flex items-center gap-4 pl-4 border-l border-[var(--border)]">
              <span className="text-xs text-[var(--muted-foreground)] hidden sm:inline-block">
                {user?.display_name || user?.email}
              </span>
              <button
                onClick={() => logout()}
                className="text-xs px-3 py-1.5 rounded-md border border-[var(--border)] hover:bg-[var(--accent)] hover:text-[var(--accent-foreground)] transition-colors"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3 pl-4 border-l border-[var(--border)]">
              <Link
                href="/login"
                className="text-sm font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="text-xs font-medium px-3.5 py-1.5 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm"
              >
                Sign Up
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
