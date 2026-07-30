import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { GaugeCircle, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { useTwin } from "@/lib/twin-store";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";


export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Sign in — Digital Twin" },
      {
        name: "description",
        content: "Create your twin profile or load the demo twin to explore the dashboard.",
      },
      { property: "og:title", content: "Sign in — Digital Twin" },
      {
        property: "og:description",
        content: "Create your twin profile or load the demo twin to explore the dashboard.",
      },
    ],
  }),
  component: AuthPage,
});

function AuthPage() {
  const { state, ready, signIn, loadDemo, setTheme } = useTwin();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [activeTab, setActiveTab] = useState<"signup" | "login">("signup");
  const [showSignUpDialog, setShowSignUpDialog] = useState(false);

  useEffect(() => {
    if (ready && state.authed && state.profile.onboarded) navigate({ to: "/dashboard" });
  }, [ready, state.authed, state.profile.onboarded, navigate]);


  const submit = async (mode: "signup" | "login") => {
    if (!email || !password || (mode === "signup" && !name)) {
      toast.error("Fill in every field to continue");
      return;
    }
    const isLogin = mode === "login";
    const username = isLogin ? email.split("@")[0] : name;
    try {
      const onboarded = await signIn(username, email, !isLogin);
      toast.success(isLogin ? "Welcome back" : "Twin profile created");
      navigate({ to: onboarded && isLogin ? "/dashboard" : "/setup" });
    } catch (e: any) {
      if (e.message.includes("Please sign up first")) {
        setShowSignUpDialog(true);
      } else {
        toast.error(e.message || "Failed to log in");
      }
    }
  };



  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between border-r border-border bg-sidebar p-12 lg:flex">
        <div className="flex items-center gap-2">
          <GaugeCircle className="h-5 w-5" />
          <span className="font-display text-sm font-semibold">Digital Twin</span>
        </div>
        <div className="max-w-md">
          <h2 className="font-display text-4xl font-semibold leading-tight">
            A model of you, running a few years ahead.
          </h2>
          <p className="mt-4 text-sm text-muted-foreground">
            Log the day, plan the day, and watch how small changes to money, sleep and focus
            reshape the next five years.
          </p>
          <div className="mt-10 grid grid-cols-3 gap-6 border-t border-border pt-6">
            {[
              ["30d", "history modelled"],
              ["500", "Monte Carlo runs"],
              ["5y", "forward horizon"],
            ].map(([a, b]) => (
              <div key={b}>
                <div className="font-display text-2xl font-semibold">{a}</div>
                <div className="label-xs mt-1">{b}</div>
              </div>
            ))}
          </div>
        </div>
        <p className="text-xs text-muted-foreground">Local demo — data stays in your browser.</p>
      </div>

      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm animate-rise">
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-2 lg:hidden">
              <GaugeCircle className="h-5 w-5" />
              <span className="font-display text-sm font-semibold">Digital Twin</span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="ml-auto"
              aria-label="Toggle theme"
              onClick={() => setTheme(state.theme === "dark" ? "light" : "dark")}
            >
              {state.theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>

          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="signup">Sign up</TabsTrigger>
              <TabsTrigger value="login">Log in</TabsTrigger>
            </TabsList>


            <TabsContent value="signup" className="mt-6 space-y-4">
              <div className="grid gap-1.5">
                <Label className="label-xs" htmlFor="name">Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Alice" />
              </div>
              <Field id="email" label="Email" value={email} set={setEmail} type="email" />
              <Field id="password" label="Password" value={password} set={setPassword} type="password" />
              <Button className="w-full" onClick={() => submit("signup")}>
                Create Twin Profile
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={async () => {
                  try {
                    await loadDemo();
                    toast.success("Demo twin loaded with 30 days of history");
                    navigate({ to: "/dashboard" });
                  } catch (e: any) {
                    toast.error(e.message || "Failed to load demo twin");
                  }
                }}
              >
                Load Demo Twin
              </Button>

            </TabsContent>

            <TabsContent value="login" className="mt-6 space-y-4">
              <Field id="email2" label="Email" value={email} set={setEmail} type="email" />
              <Field id="password2" label="Password" value={password} set={setPassword} type="password" />
              <Button className="w-full" onClick={() => submit("login")}>
                Log In
              </Button>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      <AlertDialog open={showSignUpDialog} onOpenChange={setShowSignUpDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Account Not Found</AlertDialogTitle>
            <AlertDialogDescription>
              We couldn't find a digital twin profile registered under that email/username. Please sign up first to get started!
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                setShowSignUpDialog(false);
                setActiveTab("signup");
              }}
            >
              Sign Up Now
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}


function Field({
  id,
  label,
  value,
  set,
  type = "text",
}: {
  id: string;
  label: string;
  value: string;
  set: (v: string) => void;
  type?: string;
}) {
  return (
    <div className="grid gap-1.5">
      <Label className="label-xs" htmlFor={id}>
        {label}
      </Label>
      <Input id={id} type={type} value={value} onChange={(e) => set(e.target.value)} />
    </div>
  );
}
