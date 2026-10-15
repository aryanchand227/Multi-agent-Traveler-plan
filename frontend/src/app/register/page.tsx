"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();

  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await register(email, password, displayName || undefined);
      router.push("/plan");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Registration failed. Please check your information and try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-lg p-8">
        <div className="text-center mb-6">
          <span className="text-3xl">✈️</span>
          <h1 className="text-2xl font-bold mt-2">Create an Account</h1>
          <p className="text-sm text-[var(--muted-foreground)] mt-1">
            Save your trips, personalize preferences, and explore the world.
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-500 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)] mb-1">
              Your Name (Optional)
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Alex Smith"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)] mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)] mb-1">
              Password (Min 8 characters)
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)] mb-1">
              Confirm Password
            </label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--border)] bg-[var(--background)] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow"
          >
            {isSubmitting ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-[var(--muted-foreground)]">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-500 hover:underline font-medium">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
