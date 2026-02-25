"use client";

import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/governance/ThemeToggle";
import { fetchAuthSession, login, logout, type SessionUser } from "@/lib/governance/api-client";

export default function SettingsPage() {
  const runtimeApiBase =
    process.env.GOVERNANCE_API_URL ||
    (typeof window !== "undefined"
      ? `${window.location.protocol}//${window.location.hostname}:8080`
      : "http://127.0.0.1:8080");
  const [user, setUser] = useState<SessionUser | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Login form state
  const [loginName, setLoginName] = useState("");
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginLoading, setLoginLoading] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await fetchAuthSession();
        setAuthenticated(session.authenticated);
        if (session.user) {
          setUser(session.user);
        }
      } catch (err) {
        console.error("Failed to check auth session:", err);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);
    setLoginLoading(true);

    try {
      const response = await login({
        name: loginName,
        email: loginEmail,
        password: loginPassword,
      });

      if (response.success && response.authenticated) {
        setAuthenticated(true);
        setUser(response.user || null);
        setLoginName("");
        setLoginEmail("");
        setLoginPassword("");
      } else {
        setLoginError(response.message || "Login failed");
      }
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setAuthenticated(false);
      setUser(null);
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-token-primary mx-auto mb-4"></div>
          <p className="text-token-secondary">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-token-primary mb-1">Settings</h1>
        <p className="text-sm text-token-secondary">
          Manage theme, identity, and preferences
        </p>
      </div>

      {/* Theme Settings */}
      <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
        <h2 className="text-lg font-semibold text-token-primary mb-4">
          Appearance
        </h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-token-primary">Theme</p>
            <p className="text-xs text-token-tertiary">
              Choose light or dark theme
            </p>
          </div>
          <ThemeToggle />
        </div>
      </div>

      {/* Identity Management */}
      <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
        <h2 className="text-lg font-semibold text-token-primary mb-4">
          Identity & Authentication
        </h2>

        {authenticated && user ? (
          <div className="space-y-4">
            <div className="p-4 bg-token-inset rounded-md">
              <p className="text-sm font-medium text-token-primary mb-2">
                Logged in as
              </p>
              <div className="space-y-1 text-sm">
                <p>
                  <span className="text-token-secondary">Name:</span>{" "}
                  <span className="text-token-primary">{user.name}</span>
                </p>
                <p>
                  <span className="text-token-secondary">Email:</span>{" "}
                  <span className="text-token-primary">{user.email}</span>
                </p>
                <p>
                  <span className="text-token-secondary">Role:</span>{" "}
                  <span className="text-token-primary">{user.role}</span>
                </p>
                {user.roles && user.roles.length > 0 && (
                  <p>
                    <span className="text-token-secondary">All Roles:</span>{" "}
                    <span className="text-token-primary">
                      {user.roles.join(", ")}
                    </span>
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-token-danger text-white rounded-md hover:bg-opacity-90 transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-token-primary mb-1">
                Name
              </label>
              <input
                type="text"
                value={loginName}
                onChange={(e) => setLoginName(e.target.value)}
                required
                className="w-full px-3 py-2 bg-token-canvas border border-token-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-token-primary focus:border-transparent"
                placeholder="Enter your name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-token-primary mb-1">
                Email
              </label>
              <input
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                required
                className="w-full px-3 py-2 bg-token-canvas border border-token-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-token-primary focus:border-transparent"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-token-primary mb-1">
                Password
              </label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
                className="w-full px-3 py-2 bg-token-canvas border border-token-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-token-primary focus:border-transparent"
                placeholder="Enter your password"
              />
            </div>
            {loginError && (
              <p className="text-sm text-token-danger">⚠️ {loginError}</p>
            )}
            <button
              type="submit"
              disabled={loginLoading}
              className="w-full px-4 py-2 bg-token-primary text-white rounded-md hover:bg-opacity-90 transition-colors disabled:opacity-50"
            >
              {loginLoading ? "Logging in..." : "Login"}
            </button>
          </form>
        )}
      </div>

      {/* API Configuration */}
      <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
        <h2 className="text-lg font-semibold text-token-primary mb-4">
          API Configuration
        </h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
              <span className="text-token-secondary">Base URL:</span>
            <code className="text-token-primary font-mono text-xs">
              {runtimeApiBase}
            </code>
          </div>
          <div className="flex justify-between">
            <span className="text-token-secondary">Credentials:</span>
            <span className="text-token-primary">Include</span>
          </div>
          <div className="flex justify-between">
            <span className="text-token-secondary">Content-Type:</span>
            <span className="text-token-primary">application/json</span>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="bg-token-elevated rounded-lg border border-token-border-default p-6">
        <h2 className="text-lg font-semibold text-token-primary mb-4">About</h2>
        <div className="space-y-2 text-sm">
          <p className="text-token-secondary">
            <strong className="text-token-primary">Substrate Governance</strong>
            <br />
            AI-optimized work breakdown structure and packet governance system
          </p>
          <p className="text-token-tertiary text-xs">
            Built with Next.js, TypeScript, and Tailwind CSS
          </p>
        </div>
      </div>
    </div>
  );
}
