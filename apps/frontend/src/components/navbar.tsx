"use client";

import Link from "next/link";
import { useState } from "react";
import { useAppStore } from "@/lib/store";

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const user = useAppStore((s) => s.user);

  return (
    <nav className="sticky top-0 z-50 bg-card/80 backdrop-blur-lg border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📖</span>
            <span className="font-bold text-xl text-foreground">Apologia</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            <Link href="/sermons" className="text-muted-foreground hover:text-foreground transition-colors">
              Sermons
            </Link>
            <Link href="/graph" className="text-muted-foreground hover:text-foreground transition-colors">
              Knowledge Graph
            </Link>
            <Link href="/courses" className="text-muted-foreground hover:text-foreground transition-colors">
              Courses
            </Link>
            <Link href="/workbench" className="text-muted-foreground hover:text-foreground transition-colors">
              Workbench
            </Link>
            {user ? (
              <span className="text-sm text-muted-foreground bg-secondary px-3 py-1.5 rounded-md">
                {user.email}
              </span>
            ) : (
              <Link
                href="/login"
                className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile nav */}
        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link href="/sermons" className="block py-2 text-muted-foreground hover:text-foreground">
              Sermons
            </Link>
            <Link href="/graph" className="block py-2 text-muted-foreground hover:text-foreground">
              Knowledge Graph
            </Link>
            <Link href="/courses" className="block py-2 text-muted-foreground hover:text-foreground">
              Courses
            </Link>
            <Link href="/workbench" className="block py-2 text-muted-foreground hover:text-foreground">
              Workbench
            </Link>
            {user ? (
              <span className="block py-2 text-sm text-muted-foreground">
                {user.email}
              </span>
            ) : (
              <Link
                href="/login"
                className="block bg-primary text-primary-foreground px-4 py-2 rounded-md text-center"
              >
                Sign In
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
