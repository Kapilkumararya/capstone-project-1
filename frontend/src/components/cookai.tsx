import { Link, useRouterState } from "@tanstack/react-router";
import { useRef, useState, useEffect, type ReactNode } from "react";
import {
  ArrowLeft, ArrowRight, Bell, Bookmark, Camera, Check, ChefHat, ChevronDown,
  Clock3, CookingPot, Flame, Heart, Home, Leaf, Menu, MessageCircle, Mic,
  MicOff, Search, Send, Settings, SlidersHorizontal, Sparkle, Star, ThumbsUp,
  Users, UtensilsCrossed, Video, VideoOff, WandSparkles, X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Conversation, ConversationContent } from "@/components/ai-elements/conversation";
import { Message, MessageContent } from "@/components/ai-elements/message";
import { PromptInput, PromptInputFooter, PromptInputSubmit, PromptInputTextarea } from "@/components/ai-elements/prompt-input";
import produce from "@/assets/cookai-produce.jpg";
import bowl from "@/assets/cookai-bowl.jpg";
import pasta from "@/assets/cookai-pasta.jpg";
import eggs from "@/assets/cookai-eggs.jpg";
import chopping from "@/assets/cookai-chopping.jpg";
import participantOne from "@/assets/cookai-participant-1.jpg";
import participantTwo from "@/assets/cookai-participant-2.jpg";
import { useAuth } from "@/context/AuthContext";
import { AuthModal } from "@/components/AuthModal";
import { fetchApi } from "@/lib/api";
import { useNavigate, getRouteApi } from "@tanstack/react-router";

const recipesRoute = getRouteApi("/recipes");
const cookRoute = getRouteApi("/cook");


const navItems = [
  { label: "Home", to: "/", icon: Home },
  { label: "AI Recipes", to: "/recipes", icon: WandSparkles },
  { label: "Community", to: "/community", icon: Users },
  { label: "Cook Together", to: "/cook-together", icon: Video },
  { label: "Saved", to: "/saved", icon: Bookmark },
] as const;
const pantryItems = [
  { label: "Dietary Preferences", to: "/preferences", icon: Leaf },
  { label: "Settings", to: "/settings", icon: Settings },
] as const;

function Brand() {
  return <Link to="/" className="flex items-center gap-2.5" aria-label="CookAI home">
    <span className="grid size-9 place-items-center rounded-xl bg-primary text-primary-foreground"><ChefHat className="size-5" /></span>
    <span><strong className="block font-display text-lg leading-none">CookAI</strong><small className="mt-1 block text-[9px] font-bold uppercase text-muted-foreground">Culinary AI</small></span>
  </Link>;
}

function Sidebar({ close }: { close?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const render = (item: (typeof navItems)[number] | (typeof pantryItems)[number]) => {
    const Icon = item.icon;
    const active = pathname === item.to;
    return <Link key={item.to} to={item.to} onClick={close} className={`flex items-center gap-3 rounded-full px-4 py-3 text-sm font-medium transition-colors ${active ? "bg-secondary text-primary" : "text-foreground/75 hover:bg-muted"}`}>
      <Icon className="size-4.5 shrink-0" /><span>{item.label}</span>
    </Link>;
  };
  return <aside className="flex h-full flex-col bg-card p-5">
    <Brand />
    <nav className="mt-8 space-y-1">{navItems.map(render)}</nav>
    <p className="mb-2 mt-7 px-4 text-[10px] font-bold uppercase text-muted-foreground">Your pantry</p>
    <nav className="space-y-1">{pantryItems.map(render)}</nav>
    <div className="relative mt-auto overflow-hidden rounded-xl bg-secondary/70 p-4 leaf-doodle">
      <p className="text-xs font-bold">Kitchen Pro</p><p className="text-[11px] text-muted-foreground">Smart assistant active</p>
    </div>
  </aside>;
}

export function AppShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const { user, setShowAuthModal, logout } = useAuth();
  
  return <div className="min-h-screen bg-background text-foreground">
    <AuthModal />
    <div className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r border-border/60 lg:block"><Sidebar /></div>
    {open && <div className="fixed inset-0 z-50 lg:hidden"><div className="absolute inset-0 bg-foreground/25" onClick={() => setOpen(false)} /><div className="absolute inset-y-0 left-0 w-72"><Sidebar close={() => setOpen(false)} /></div><Button size="icon" variant="secondary" className="absolute left-[17.5rem] top-4 rounded-full" onClick={() => setOpen(false)} aria-label="Close navigation"><X /></Button></div>}
    <div className="lg:pl-60">
      <header className="sticky top-0 z-20 grid h-18 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-border/50 bg-background/90 px-4 backdrop-blur-xl sm:px-7 lg:px-8">
        <Button size="icon" variant="ghost" className="lg:hidden" onClick={() => setOpen(true)} aria-label="Open navigation"><Menu /></Button>
        <div className="hidden lg:block" />
        <label className="flex max-w-xl items-center gap-2 rounded-full border border-border bg-card px-4 py-2.5 soft-shadow">
          <Search className="size-4 shrink-0 text-muted-foreground" /><input className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground" placeholder="Search recipes, ingredients, techniques…" />
        </label>
        <div className="flex shrink-0 items-center gap-2 sm:gap-4">
          <Button size="icon" variant="ghost" className="rounded-full bg-card" aria-label="Notifications"><Bell /></Button>
          {user ? (
            <>
              <div className="hidden text-right sm:block">
                <p className="text-xs font-bold">{user.username}</p>
                <button onClick={logout} className="text-[10px] text-muted-foreground hover:text-primary">Sign out</button>
              </div>
              <div className="grid size-9 place-items-center rounded-full bg-warm text-sm font-bold text-warm-foreground">
                {(user.username || "U").charAt(0).toUpperCase()}
              </div>
            </>
          ) : (
            <Button variant="secondary" className="rounded-full h-9" onClick={() => setShowAuthModal(true)}>
              Sign In
            </Button>
          )}
        </div>
      </header>
      <main className="min-h-[calc(100vh-4.5rem)] p-4 sm:p-6 lg:p-8">{children}</main>
    </div>
  </div>;
}

function Chip({ children, tone = "green" }: { children: ReactNode; tone?: "green" | "warm" | "sun" }) {
  const toneClass = tone === "warm" ? "bg-warm/15 text-warm" : tone === "sun" ? "bg-sun/25 text-foreground" : "bg-secondary text-primary";
  return <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold ${toneClass}`}>{children}</span>;
}

const recipeData = [
  { title: "Spinach & Tomato Egg Scramble", image: eggs, match: 90, time: "15 mins", level: "Easy", tag: "Breakfast & Brunch" },
  { title: "Mediterranean Veggie Bowl", image: bowl, match: 88, time: "25 mins", level: "Easy", tag: "Grain Bowls & Salads" },
  { title: "Tomato Spinach Pasta", image: pasta, match: 82, time: "30 mins", level: "Medium", tag: "Main Pasta" },
];

function RecipeCard({ recipe, action = false }: { recipe: any; action?: boolean }) {
  const [saved, setSaved] = useState(false);
  return <article className="group overflow-hidden rounded-2xl bg-card soft-shadow">
    <div className="relative aspect-[4/3] overflow-hidden"><img src={recipe.image} alt={recipe.title} width={1000} height={1000} loading="lazy" className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]" />
      <Button size="icon" variant="secondary" className="absolute right-3 top-3 rounded-full" onClick={() => setSaved(!saved)} aria-label={saved ? "Remove from saved" : "Save recipe"}><Heart className={saved ? "fill-warm text-warm" : ""} /></Button>
      <Chip><Sparkle className="size-3" /> {recipe.match}% match</Chip>
    </div>
    <div className="p-4"><p className="text-[10px] font-bold uppercase text-muted-foreground">{recipe.tag}</p><h3 className="mt-1 min-h-12 text-lg font-bold leading-snug">{recipe.title}</h3>
      <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground"><span className="flex items-center gap-1"><Clock3 className="size-3.5" />{recipe.time}</span><span className="flex items-center gap-1"><Flame className="size-3.5" />{recipe.level}</span></div>
      {action && <Button asChild className="mt-4 w-full rounded-full"><Link to="/cook" search={{ recipeId: recipe.id }}>Start cooking <ArrowRight /></Link></Button>}
    </div>
  </article>;
}

function PageTitle({ eyebrow, title, action }: { eyebrow?: string; title: string; action?: ReactNode }) {
  return <div className="grid grid-cols-[minmax(0,1fr)_auto] items-end gap-4"><div className="min-w-0">{eyebrow && <p className="text-[10px] font-bold uppercase text-warm">{eyebrow}</p>}<h1 className="truncate text-2xl font-extrabold sm:text-3xl">{title}</h1></div>{action}</div>;
}

export function HomePage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const { user, setShowAuthModal } = useAuth();
  const navigate = useNavigate();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    setFile(selected);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", selected);
      
      const res = await fetchApi("/detect/ingredients", {
        method: "POST",
        body: formData,
      });
      
      navigate({
        to: "/recipes",
        search: { ingredients: JSON.stringify(res.ingredients) }
      });
    } catch (err) {
      console.error(err);
      alert("Failed to process image.");
    } finally {
      setLoading(false);
    }
  };
  const features = [
    [WandSparkles, "AI Recipe Match", "Personalized recipes built around what’s already in your kitchen."],
    [CookingPot, "Cooking Assistant", "Hands-free, real-time guidance that waits for your pace."],
    [Users, "Recipe Community", "Swap family recipes, smart tweaks, and kitchen inspiration."],
    [Video, "Cook Together", "Share a recipe and cook live with the people you love."],
  ] as const;
  return <div className="mx-auto max-w-7xl space-y-10 gentle-in">
    <section className="grid items-center gap-8 xl:grid-cols-[1.2fr_.8fr]">
      <div>
        <Chip><WandSparkles className="size-3" /> Intelligent culinary companion</Chip>
        <h1 className="mt-5 max-w-xl text-4xl font-extrabold leading-[1.05] sm:text-6xl">What’s in<br/><span className="border-b-4 border-warm">your kitchen?</span></h1>
        <p className="mt-4 max-w-xl text-base text-muted-foreground">Snap a photo, let our AI detect ingredients, find the perfect recipe, and get step-by-step guidance — all in one peaceful place.</p>
        <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={handleUpload} />
        <div className="mt-6 grid min-h-56 place-items-center rounded-2xl border border-border bg-card p-6 text-center soft-shadow">
          <div><span className="mx-auto grid size-14 place-items-center rounded-full bg-secondary text-primary"><Camera /></span>
            <Button className="mt-3 rounded-full" disabled={loading} onClick={() => inputRef.current?.click()}><Camera /> {loading ? "Analyzing..." : file ? "Choose another photo" : "Upload a photo"}</Button>
            <p className="mt-2 text-xs text-muted-foreground">{file ? file.name : "or drag and drop pantry items here"}</p>
            <div className="mt-5 flex flex-wrap justify-center gap-2"><span className="text-xs font-semibold">Try with:</span>{["🍅 Tomatoes", "🥚 Eggs", "🥬 Spinach", "🍗 Chicken"].map((x) => <Chip key={x}>{x}</Chip>)}</div>
          </div>
        </div>
        <div className="mt-5 grid grid-cols-3 gap-4">{[["12,000+", "Dishes cooked"], ["98.4%", "Ingredient match"], ["4.9/5", "Home chef rating"]].map(([a,b]) => <div key={b}><strong className="font-display text-xl">{a}</strong><p className="text-[11px] text-muted-foreground">{b}</p></div>)}</div>
      </div>
      <div className="relative mx-auto w-full max-w-lg"><img src={produce} alt="Fresh tomatoes, eggs, spinach, peppers and garlic in a bowl" width={1400} height={1000} className="aspect-[4/3] w-full rounded-[2rem] object-cover soft-shadow" /><div className="absolute -bottom-4 left-4 flex items-center gap-3 rounded-xl bg-card p-3 soft-shadow"><span className="grid size-10 place-items-center rounded-full bg-secondary"><WandSparkles className="size-5" /></span><span><strong className="block text-xs">AI detects your ingredients</strong><small className="text-muted-foreground">5 fresh items recognized</small></span></div></div>
    </section>
    <section><PageTitle eyebrow="Designed for mindful cooking" title="Everything you need from pantry to plate" /><div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{features.map(([Icon,title,text]) => <article key={title} className="rounded-2xl bg-card p-5 soft-shadow"><span className="grid size-11 place-items-center rounded-xl bg-secondary"><Icon className="size-5" /></span><h3 className="mt-5 font-bold">{title}</h3><p className="mt-2 text-sm leading-relaxed text-muted-foreground">{text}</p><Link to={title === "AI Recipe Match" ? "/recipes" : title === "Cooking Assistant" ? "/cook" : title === "Recipe Community" ? "/community" : "/cook-together"} className="mt-5 flex items-center justify-between text-[10px] font-bold uppercase">Explore <ArrowRight className="size-4" /></Link></article>)}</div></section>
    <section className="rounded-2xl bg-secondary/60 p-5"><h2 className="text-lg font-bold">Trending from our community today</h2><p className="text-xs text-muted-foreground">Prepared with under 6 primary ingredients</p><div className="mt-4 grid gap-4 md:grid-cols-3">{recipeData.map((r) => <RecipeCard key={r.title} recipe={r} />)}</div></section>
  </div>;
}

export function RecipesPage() {
  const search = recipesRoute.useSearch();
  const initialIngredients = search.ingredients ? JSON.parse(search.ingredients) : ["tomato", "egg", "spinach", "onion", "garlic"];
  const [ingredients, setIngredients] = useState<string[]>(initialIngredients);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const { user } = useAuth();
  
  useEffect(() => {
    if (user && ingredients.length > 0) {
      fetchApi("/recommendations/", {
        method: "POST",
        body: JSON.stringify({ ingredients, limit: 10 })
      }).then(res => setRecommendations(res.results || []))
        .catch(console.error);
    }
  }, [ingredients, user]);

  const displayRecipes = recommendations.length > 0 
    ? recommendations.map(r => ({
        id: r.recipe_id,
        title: r.title,
        image: bowl,
        match: Math.round(r.match_score * 100),
        time: r.time,
        level: "Easy",
        tag: r.tags?.[0] || "Dinner"
      }))
    : recipeData.map(r => ({ ...r, id: "" }));

  return <div className="mx-auto max-w-7xl space-y-8 gentle-in"><PageTitle eyebrow="Pantry scan · analysis complete" title="AI Recipe Discovery" />
    <div className="grid gap-5 xl:grid-cols-[1.35fr_.9fr]">
      <section className="rounded-2xl bg-card p-5 soft-shadow"><h2 className="flex items-center gap-2 font-bold"><SlidersHorizontal className="size-5" /> Detected Ingredients</h2><div className="mt-4 grid gap-5 sm:grid-cols-[180px_1fr]"><img src={produce} alt="Detected pantry ingredients" width={1400} height={1000} className="aspect-[4/3] h-full w-full rounded-xl object-cover" /><div><p className="mb-3 text-xs text-muted-foreground">Tap to discard ingredients or refine detection:</p><div className="flex flex-wrap gap-2">{ingredients.map((x) => <Button key={x} variant="secondary" size="sm" className="rounded-full" onClick={() => setIngredients(ingredients.filter((i) => i !== x))}>{x}<X className="size-3" /></Button>)}<Button size="sm" variant="outline" className="rounded-full">+ Add more</Button></div><p className="mt-5 text-[11px] text-muted-foreground">CookAI cross-referenced 34 seasonal recipes with your pantry.</p></div></div></section>
      <section className="rounded-2xl bg-card p-5 soft-shadow"><div className="flex justify-between"><h2 className="font-bold">Your Preferences</h2><Button variant="ghost" size="sm">Edit</Button></div><p className="mt-2 text-xs text-muted-foreground">Current constraints applied from your Kitchen Profile:</p><div className="mt-4 flex flex-wrap gap-2">{["🌱 Vegetarian", "⏱ Quick < 30 mins", "⚡ High Protein", "👍 Easy Skill Level"].map(x => <Chip key={x}>{x}</Chip>)}</div><div className="mt-5 flex items-center gap-3 rounded-xl bg-secondary p-3"><strong className="grid size-11 place-items-center rounded-full border-4 border-primary">88%</strong><span className="text-xs"><b className="block">Pantry compatibility</b>{ingredients.length} ingredients matched</span></div></section>
    </div>
    <section><PageTitle title="Top Recipe Recommendations" action={<div className="flex gap-2"><Chip><Check className="size-3" /> AI Verified</Chip><Button variant="outline" size="sm" className="rounded-full">Best Match <ChevronDown /></Button></div>} /><div className="mt-5 grid gap-5 md:grid-cols-3">{displayRecipes.map((r, i) => <RecipeCard key={i} recipe={r} action />)}</div></section>
    <div className="flex items-center gap-3 rounded-2xl bg-card p-4 soft-shadow"><MessageCircle className="size-5" /><div className="hidden sm:block"><p className="text-xs font-bold">Want to tweak these suggestions?</p><p className="text-[11px] text-muted-foreground">Ask CookAI to replace an ingredient or limit prep equipment.</p></div><input className="ml-auto min-w-0 flex-1 rounded-full bg-secondary px-4 py-2 text-xs outline-none sm:max-w-sm" placeholder="e.g. Make it dairy-free…"/><Button size="icon" className="rounded-full" aria-label="Send request"><ArrowRight /></Button></div>
  </div>;
}

function AssistantChat({ messages, onSendMessage }: { messages: any[], onSendMessage: (t: string) => void }) {
  return <section className="flex min-h-[620px] flex-col rounded-2xl bg-card soft-shadow"><div className="flex items-center gap-3 border-b border-border p-5"><span className="grid size-10 place-items-center rounded-full bg-secondary"><ChefHat /></span><div><h2 className="font-bold">AI Sous Chef</h2><p className="text-[11px] text-muted-foreground">Context: Active Cooking Session</p></div></div>
    <Conversation className="min-h-0"><ConversationContent className="gap-5 p-5">{messages.map((m,i) => <Message key={i} from={m.role as "user" | "assistant"}><MessageContent className={m.role === "user" ? "bg-primary text-primary-foreground" : ""}>{m.role === "assistant" && <span className="mb-1 flex items-center gap-1 text-xs font-bold text-primary"><Sparkle className="size-3" /> CookAI</span>}<p className="leading-relaxed">{m.text}</p></MessageContent></Message>)}</ConversationContent></Conversation>
    <div className="p-4"><div className="mb-3 flex flex-wrap gap-2">{["What can I substitute?", "Next step", "Tips for better flavour"].map(x => <Button key={x} size="sm" variant="secondary" className="rounded-full" onClick={() => onSendMessage(x)}>{x}</Button>)}</div><PromptInput onSubmit={({text}) => onSendMessage(text)} className="rounded-2xl"><PromptInputTextarea placeholder="Ask anything about this step…" className="min-h-14" /><PromptInputFooter className="justify-end"><PromptInputSubmit /></PromptInputFooter></PromptInput></div>
  </section>;
}

export function CookPage() {
  const search = cookRoute.useSearch();
  const recipeId = search.recipeId;
  const { user } = useAuth();
  
  const [session, setSession] = useState<any>(null);
  const [recipe, setRecipe] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [step, setStep] = useState(1);
  const [tab, setTab] = useState("Steps"); 
  const [checked, setChecked] = useState([true,true,false,false,false]);
  
  useEffect(() => {
    if (!recipeId || !user) return;
    
    fetchApi("/assistant/sessions", {
      method: "POST",
      body: JSON.stringify({ recipe_id: recipeId })
    }).then(async (sess) => {
      setSession(sess);
      setStep(sess.current_step + 1);
      
      const rec = await fetchApi(`/recipes/${recipeId}`);
      setRecipe(rec);
      
      const fullSess = await fetchApi(`/assistant/sessions/${sess.session_id}`);
      if (fullSess.messages) {
        setMessages(fullSess.messages.map((m: any) => ({
          role: m.role,
          text: m.content
        })));
      }
    }).catch(console.error);
    
  }, [recipeId, user]);

  const handleSendMessage = async (text: string) => {
    if (!session || !text.trim()) return;
    setMessages(prev => [...prev, { role: "user", text }]);
    try {
      const res = await fetchApi(`/assistant/sessions/${session.session_id}/chat`, {
        method: "POST",
        body: JSON.stringify({ message: text })
      });
      setMessages(prev => [...prev, { role: "assistant", text: res.response }]);
      if (res.current_step !== undefined) {
        setStep(res.current_step + 1);
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (!recipe) return <div className="p-8 text-center gentle-in">Loading session...</div>;

  const totalSteps = recipe.steps ? recipe.steps.length : 7;
  const currentStepInfo = recipe.steps && recipe.steps[step - 1] ? recipe.steps[step - 1] : "Follow the AI guidance for this step.";

  return <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1.15fr_.85fr] gentle-in"><div className="space-y-5">
    <section className="grid gap-4 rounded-2xl bg-card p-4 soft-shadow sm:grid-cols-[180px_1fr]"><img src={bowl} alt="Recipe" width={1000} height={1000} className="aspect-[16/9] h-full w-full rounded-xl object-cover"/><div className="self-center"><Chip>Active session</Chip><h1 className="mt-2 text-2xl font-bold">{recipe.title}</h1><div className="mt-3 flex flex-wrap gap-2"><Chip>Vegetarian</Chip><Chip>{recipe.time || "25 mins"}</Chip><Chip>Easy</Chip></div></div></section>
    <section className="rounded-2xl bg-card p-5 soft-shadow"><div className="flex justify-center gap-2">{["Ingredients", "Steps", "Nutrition"].map(x => <Button key={x} size="sm" variant={tab === x ? "default" : "ghost"} className="rounded-full" onClick={() => setTab(x)}>{x}{x === "Steps" && ` ${step}/${totalSteps}`}</Button>)}</div>
      {tab === "Ingredients" ? <div className="mt-8 grid gap-3 sm:grid-cols-2">{(recipe.ingredients || []).map((x: string) => <div className="rounded-xl bg-muted p-4 text-sm" key={x}>{x}</div>)}</div> : tab === "Nutrition" ? <div className="mt-8 grid grid-cols-3 gap-4 text-center">{[["430","calories"],["18g","protein"],["12g","fibre"]].map(x => <div className="rounded-xl bg-muted p-5" key={x[1]}><b className="text-2xl">{x[0]}</b><p className="text-xs text-muted-foreground">{x[1]}</p></div>)}</div> : <><div className="mt-7 rounded-xl bg-secondary/70 p-4"><div className="flex justify-between"><b className="text-xs uppercase">Quick checklist</b><span className="text-[10px] text-muted-foreground">Tap to mark prepared</span></div><div className="mt-3 grid gap-3 sm:grid-cols-3">{(recipe.ingredients || ["1 cup quinoa","½ cup cherry tomatoes","1 cucumber","¼ cup feta","1 tbsp olive oil"]).slice(0,5).map((x: string,i: number) => <label key={x} className="flex items-center gap-2 rounded-lg bg-card px-3 py-2 text-xs"><Checkbox checked={checked[i]} onCheckedChange={() => setChecked(checked.map((c,j) => j === i ? !c : c))}/>{x}</label>)}</div></div>
      <div className="mt-7 flex items-center justify-between"><Chip tone="warm">{step}</Chip><p className="text-[10px] font-bold uppercase text-warm">Step {step} of {totalSteps}</p><span className="flex items-center gap-1 text-[10px]"><Clock3 className="size-3"/>In progress</span></div><h2 className="mt-4 text-3xl font-bold">Step {step}</h2><p className="mt-3 leading-relaxed text-muted-foreground">{currentStepInfo}</p><img src={chopping} alt="Step visual" width={1400} height={900} loading="lazy" className="mt-5 aspect-[16/9] w-full rounded-xl object-cover"/>
      <div className="mt-5 grid grid-cols-[auto_1fr_auto] items-center gap-4"><Button variant="secondary" className="rounded-full" disabled={step === 1} onClick={() => setStep(Math.max(1, step-1))}><ArrowLeft/>Previous</Button><div className="flex justify-center gap-1">{Array.from({length:totalSteps},(_,i) => <span key={i} className={`h-1.5 rounded-full ${i+1 === step ? "w-6 bg-primary" : "w-2 bg-secondary"}`}/>)}</div><Button className="rounded-full" disabled={step === totalSteps} onClick={() => setStep(Math.min(totalSteps, step+1))}>Next step<ArrowRight/></Button></div></>}
    </section></div><AssistantChat messages={messages} onSendMessage={handleSendMessage} /></div>;
}

function Avatar({ name }: { name: string }) { return <span className="grid size-10 shrink-0 place-items-center rounded-full bg-sun/40 font-bold text-primary">{name.slice(0,1).toUpperCase()}</span>; }

function CommunityPost({ second = false }: { second?: boolean }) {
  const [votes,setVotes] = useState(second ? 289 : 432); const [following,setFollowing] = useState(false); const [saved,setSaved] = useState(false);
  const name = second ? "goodfoodie" : "foodie.sarah";
  return <article className="rounded-2xl bg-card p-5 soft-shadow"><div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3"><Avatar name={name}/><div className="min-w-0"><p className="truncate font-bold">{name}</p><p className="text-[11px] text-muted-foreground">{second ? "4h ago" : "2h ago"} · <span className="text-primary">● Vegetarian</span></p></div><Button size="sm" variant="secondary" className="rounded-full" onClick={() => setFollowing(!following)}>{following ? "Following" : "Follow"}</Button></div>
    <h2 className="mt-5 text-xl font-bold">{second ? "Charred Lemon Herb Salmon Bowls" : "Creamy Tomato Basil Pasta 🍅"}</h2><p className="mt-1 text-sm text-muted-foreground">{second ? "Quick weekday meal prep win. Cooked with crisp snap peas, fluffy quinoa, and a bright lemon dressing." : "Super easy, super delicious! Perfect for a cozy autumn dinner. Takes only 20 mins and uses simple pantry ingredients."}</p>
    <img src={second ? bowl : pasta} alt={second ? "Salmon-style grain bowl with fresh vegetables" : "Creamy tomato basil pasta"} width={1000} height={1000} loading="lazy" className="mt-5 aspect-[16/10] w-full rounded-xl object-cover"/>
    <div className="mt-4 flex items-center gap-3"><Button variant="secondary" size="sm" className="rounded-full" onClick={() => setVotes(votes+1)}><ThumbsUp/>{votes}</Button><Button variant="ghost" size="sm"><MessageCircle/> {second ? 32 : 56}</Button><Button variant="ghost" size="sm" className="ml-auto" onClick={() => setSaved(!saved)} aria-label="Save post"><Bookmark className={saved ? "fill-primary" : ""}/></Button></div>
    {!second && <div className="mt-4 space-y-3 rounded-xl bg-muted p-4 text-xs"><p><b>mealprep.mike</b> This looks amazing! I’m definitely trying this tonight. 😍</p><p><b>cooking.with.anna</b> Added it to my weekly menu! Thank you!</p></div>}
  </article>;
}

export function CommunityPage() {
  const [tab,setTab] = useState("For You");
  return <div className="mx-auto max-w-7xl gentle-in"><div className="flex flex-wrap items-center gap-4"><PageTitle title="Community"/><div className="flex rounded-full bg-card p-1">{["For You","Following","Trending"].map(x => <Button key={x} size="sm" variant={tab === x ? "default" : "ghost"} className="rounded-full" onClick={() => setTab(x)}>{x}</Button>)}</div><Button className="ml-auto rounded-full"><span className="text-lg">+</span>Create post</Button></div>
    <div className="mt-6 grid items-start gap-6 xl:grid-cols-[1fr_310px]"><div className="space-y-6"><CommunityPost/><CommunityPost second/></div><aside className="space-y-5 xl:sticky xl:top-24"><section className="rounded-2xl bg-card p-5 soft-shadow"><h2 className="font-bold">Popular Creators</h2><div className="mt-4 space-y-4">{[["foodie.sarah","12.4k"],["mealprep.mike","8.2k"],["cooking.with.anna","6.7k"]].map(([n,c]) => <div key={n} className="grid grid-cols-[auto_1fr_auto] items-center gap-2"><Avatar name={n}/><span className="min-w-0"><b className="block truncate text-xs">{n}</b><small className="text-muted-foreground">{c} followers</small></span><Button size="sm" variant="secondary" className="rounded-full">Follow</Button></div>)}</div></section><section className="rounded-2xl bg-card p-5 soft-shadow"><h2 className="font-bold">Trending Recipes</h2><div className="mt-4 space-y-4">{recipeData.map(r => <div key={r.title} className="flex gap-3"><img src={r.image} alt="" width={1000} height={1000} loading="lazy" className="size-12 rounded-lg object-cover"/><span className="min-w-0"><b className="block truncate text-xs">{r.title}</b><small className="text-muted-foreground">↑ {r.match * 100} upvotes</small></span></div>)}</div></section></aside></div>
  </div>;
}

export function CookTogetherPage() {
  const [mic,setMic] = useState(true); const [camera,setCamera] = useState(true); const [steps,setSteps] = useState([true,true,false,false]); const [chat,setChat] = useState(["Rohan: I’m adding some chilli flakes! 🌶️", "Sneha: My water is boiling now. Dropping the rigatoni in!"]);
  const people = [[participantOne,"You"],[participantTwo,"Aarav"],[participantTwo,"Rohan"],[participantOne,"Sneha"]] as const;
  return <div className="mx-auto max-w-7xl gentle-in"><div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4"><div><div className="flex items-center gap-2"><h1 className="truncate text-2xl font-bold">Pasta Night with Friends</h1><Chip>● Live session</Chip></div><p className="text-xs text-muted-foreground">Today · 6:00 PM · 45 mins · Google Meet</p></div><Button asChild className="rounded-full"><a href="https://meet.google.com/" target="_blank" rel="noreferrer"><Video/>Join Meet</a></Button></div>
    <div className="mt-6 grid items-start gap-6 xl:grid-cols-[1.2fr_.8fr]"><div className="space-y-5"><section className="rounded-2xl bg-secondary/60 p-5"><div className="grid gap-3 sm:grid-cols-2">{people.map(([img,name],i) => <div className="relative overflow-hidden rounded-xl" key={name}><img src={img} alt={`${name} cooking during the shared video session`} width={1000} height={700} loading="lazy" className="aspect-video w-full object-cover"/><Chip><span className="absolute bottom-3 left-3">{name} {i === 2 ? "🔇" : "🎙"}</span></Chip></div>)}</div><div className="mx-auto mt-5 flex w-fit gap-2 rounded-full bg-card p-2 soft-shadow"><Button size="icon" variant={mic ? "secondary" : "destructive"} className="rounded-full" onClick={() => setMic(!mic)} aria-label="Toggle microphone">{mic ? <Mic/> : <MicOff/>}</Button><Button size="icon" variant={camera ? "secondary" : "destructive"} className="rounded-full" onClick={() => setCamera(!camera)} aria-label="Toggle camera">{camera ? <Video/> : <VideoOff/>}</Button><Button variant="destructive" className="rounded-full">Leave</Button></div></section><div className="flex items-center gap-3 rounded-2xl bg-secondary p-4"><span className="grid size-10 place-items-center rounded-full bg-accent"><ChefHat/></span><p className="text-sm"><b>AI Sous-Chef Tip</b><br/><span className="text-muted-foreground">Reserve ½ cup of salty pasta water before draining for maximum sauce silkiness.</span></p></div></div>
      <div className="space-y-5"><section className="rounded-2xl bg-card p-5 soft-shadow"><h2 className="font-bold">Shared Recipe</h2><div className="mt-4 flex gap-3 rounded-xl bg-secondary/60 p-3"><img src={pasta} alt="Creamy tomato pasta" width={1000} height={1000} loading="lazy" className="size-16 rounded-lg object-cover"/><span><b className="text-sm">Creamy Tomato Pasta</b><p className="text-xs text-muted-foreground">20 mins · Easy</p></span></div><div className="mt-4 space-y-2">{["Prep ingredients","Cook pasta al dente","Simmer cream & tomato sauce","Combine pasta, sauce & garnish"].map((x,i) => <label key={x} className={`flex items-center gap-3 rounded-xl p-3 text-sm ${steps[i] ? "bg-secondary" : "bg-muted"}`}><Checkbox checked={steps[i]} onCheckedChange={() => setSteps(steps.map((s,j) => j === i ? !s : s))}/><span><b>{i+1}. {x}</b><small className="block text-muted-foreground">{steps[i] ? "Done together" : "Waiting"}</small></span></label>)}</div></section>
      <section className="rounded-2xl bg-card p-5 soft-shadow"><div className="flex justify-between"><h2 className="font-bold">Session Chat</h2><small>4 cooks active</small></div><div className="my-5 space-y-3">{chat.map((m,i) => <p key={i} className="rounded-xl bg-secondary p-3 text-xs">{m}</p>)}</div><form className="flex gap-2" onSubmit={(e) => {e.preventDefault(); const fd = new FormData(e.currentTarget); const v = String(fd.get("message") ?? "").trim(); if(v) setChat([...chat,`You: ${v}`]); e.currentTarget.reset();}}><input name="message" className="min-w-0 flex-1 rounded-full bg-secondary px-4 text-sm outline-none" placeholder="Type a message…"/><Button size="icon" className="rounded-full" aria-label="Send message"><Send/></Button></form></section></div>
    </div>
  </div>;
}

export function SimplePage({ title, text }: { title: string; text: string }) {
  return <div className="mx-auto max-w-5xl gentle-in"><PageTitle title={title}/><section className="relative mt-6 min-h-[420px] overflow-hidden rounded-2xl bg-card p-8 soft-shadow leaf-doodle"><span className="grid size-14 place-items-center rounded-2xl bg-secondary"><Leaf/></span><h2 className="mt-6 text-2xl font-bold">Your kitchen, your way.</h2><p className="mt-2 max-w-md text-muted-foreground">{text}</p></section></div>;
}