import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/AuthContext";
import { fetchApi } from "@/lib/api";

export function AuthModal() {
  const { showAuthModal, setShowAuthModal, login } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isLogin) {
        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);

        const response = await fetchApi("/auth/login", {
          method: "POST",
          body: formData,
        });
        
        // Also fetch user details
        const userData = await fetchApi("/auth/me", {
          headers: { Authorization: `Bearer ${response.access_token}` }
        });

        login(response.access_token, userData);
        setShowAuthModal(false);
      } else {
        const response = await fetchApi("/auth/register", {
          method: "POST",
          body: JSON.stringify({
            email,
            password,
            username: username,
          }),
        });

        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);

        const loginResponse = await fetchApi("/auth/login", {
          method: "POST",
          body: formData,
        });

        login(loginResponse.access_token, response);
        setShowAuthModal(false);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    setShowAuthModal(open);
    if (!open) {
      setTimeout(() => {
        setIsLogin(true);
        setUsername("");
        setEmail("");
        setPassword("");
        setError("");
      }, 300);
    }
  };

  return (
    <Dialog open={showAuthModal} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md rounded-2xl bg-card text-foreground soft-shadow border border-border">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold font-display">{isLogin ? "Welcome back" : "Create an account"}</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            {isLogin ? "Enter your details to access your kitchen." : "Join CookAI to start your mindful cooking journey."}
          </DialogDescription>
        </DialogHeader>
        
        {error && <div className="text-destructive text-sm font-semibold bg-destructive/10 p-3 rounded-lg">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {!isLogin && (
            <div className="space-y-2">
              <Label htmlFor="username" className="text-xs font-bold uppercase text-muted-foreground">Username</Label>
              <Input 
                id="username" 
                placeholder="chefolivia" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                required={!isLogin}
                className="rounded-xl bg-secondary border-border"
              />
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-xs font-bold uppercase text-muted-foreground">Email</Label>
            <Input 
              id="email" 
              type="email" 
              placeholder="chef@example.com" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
              className="rounded-xl bg-secondary border-border"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password" className="text-xs font-bold uppercase text-muted-foreground">Password</Label>
            <Input 
              id="password" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              className="rounded-xl bg-secondary border-border"
            />
          </div>
          <Button type="submit" className="w-full rounded-full h-11 font-semibold" disabled={loading}>
            {loading ? "Please wait..." : (isLogin ? "Sign In" : "Sign Up")}
          </Button>
        </form>

        <div className="text-center mt-4 text-sm">
          <span className="text-muted-foreground">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
          </span>
          <button 
            type="button" 
            onClick={() => setIsLogin(!isLogin)} 
            className="text-primary font-bold hover:underline"
          >
            {isLogin ? "Sign up" : "Sign in"}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
