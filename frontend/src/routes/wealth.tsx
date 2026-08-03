// import { useMemo, useState } from "react";
// import { createFileRoute } from "@tanstack/react-router";
// import {
//   Area,
//   AreaChart,
//   CartesianGrid,
//   Line,
//   LineChart,
//   ResponsiveContainer,
//   Tooltip,
//   XAxis,
//   YAxis,
// } from "recharts";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";
// import { toast } from "sonner";
// import { AppShell } from "@/components/app-shell";
// import { Gauge } from "@/components/gauge";
// import { useGuard } from "@/lib/use-guard";
// import { money, monteCarlo, projectNetWorth, useTwin } from "@/lib/twin-store";
// import { tooltipStyle } from "@/routes/dashboard";

// export const Route = createFileRoute("/wealth")({
//   head: () => ({
//     meta: [
//       { title: "Wealth Planner — Digital Twin" },
//       { name: "description", content: "Monte Carlo and deterministic projections toward your target." },
//       { property: "og:title", content: "Wealth Planner — Digital Twin" },
//       {
//         property: "og:description",
//         content: "Monte Carlo and deterministic projections toward your target.",
//       },
//     ],
//   }),
//   component: WealthPage,
// });

// function WealthPage() {
//   const ok = useGuard();
//   const { state, updateProfile } = useTwin();
//   const p = state.profile;
//   const years = Math.max(1, p.targetAge - p.age);
//   const monthly = Math.max(0, p.monthlyIncome - p.monthlyExpenses);

//   const [mode, setMode] = useState<"mc" | "det">("mc");
//   const [running, setRunning] = useState(false);
//   const [seed, setSeed] = useState(0);
//   const [targets, setTargets] = useState({ targetAge: p.targetAge, targetNetWorth: p.targetNetWorth });

//   const mc = useMemo(() => monteCarlo(p.netWorth, monthly, years), [p.netWorth, monthly, years, seed]);
//   const det = useMemo(
//     () =>
//       projectNetWorth(p.netWorth, monthly, years).map((r) => ({
//         year: new Date().getFullYear() + r.year,
//         value: r.value,
//       })),
//     [p.netWorth, monthly, years],
//   );

//   const success = useMemo(() => {
//     const finals = mc.paths.map((path) => path[path.length - 1]);
//     return Math.round((finals.filter((v) => v >= p.targetNetWorth).length / finals.length) * 100);
//   }, [mc, p.targetNetWorth]);

//   if (!ok) return null;

//   const discretionary = Math.round(p.monthlyExpenses * 0.35);
//   const fixed = p.monthlyExpenses - discretionary;

//   return (
//     <AppShell
//       title="Financial Twin"
//       subtitle={`${years} years to age ${p.targetAge} · target ${money(p.targetNetWorth)}`}
//       actions={
//         <>
//           <Button
//             size="sm"
//             onClick={() => {
//               setRunning(true);
//               setMode("mc");
//               setTimeout(() => {
//                 setSeed((s) => s + 1);
//                 setRunning(false);
//                 toast.success("500 iterations complete");
//               }, 800);
//             }}
//           >
//             Run Monte Carlo Model
//           </Button>
//           <Button size="sm" variant="outline" onClick={() => setMode("det")}>
//             Show Deterministic Path
//           </Button>
//         </>
//       }
//     >
//       <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
//         <div className={`panel p-6 ${running ? "animate-pulse-glow" : ""}`}>
//           <p className="label-xs">
//             {mode === "mc" ? "Monte Carlo probability bands" : "Deterministic compound path"}
//           </p>
//           <div className="mt-4 h-80">
//             <ResponsiveContainer width="100%" height="100%">
//               {mode === "mc" ? (
//                 <AreaChart data={mc.data}>
//                   <defs>
//                     <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
//                       <stop offset="0%" stopColor="var(--color-foreground)" stopOpacity={0.18} />
//                       <stop offset="100%" stopColor="var(--color-foreground)" stopOpacity={0.02} />
//                     </linearGradient>
//                   </defs>
//                   <CartesianGrid stroke="var(--color-border)" vertical={false} />
//                   <XAxis dataKey="year" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
//                   <YAxis stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={58} tickFormatter={(v) => `$${Math.round(v / 1000)}k`} />
//                   <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => money(v)} />
//                   <Area type="monotone" dataKey="p90" name="90th percentile" stroke="var(--color-foreground)" strokeWidth={1.5} fill="url(#band)" />
//                   <Area type="monotone" dataKey="p50" name="Median" stroke="var(--color-foreground)" strokeWidth={2.5} fill="none" />
//                   <Area type="monotone" dataKey="p10" name="10th percentile" stroke="var(--color-muted-foreground)" strokeWidth={1.5} strokeDasharray="4 4" fill="none" />
//                 </AreaChart>
//               ) : (
//                 <LineChart data={det}>
//                   <CartesianGrid stroke="var(--color-border)" vertical={false} />
//                   <XAxis dataKey="year" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
//                   <YAxis stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={58} tickFormatter={(v) => `$${Math.round(v / 1000)}k`} />
//                   <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => money(v)} />
//                   <Line type="monotone" dataKey="value" name="Projected net worth" stroke="var(--color-foreground)" strokeWidth={2.5} dot={false} />
//                 </LineChart>
//               )}
//             </ResponsiveContainer>
//           </div>
//         </div>

//         <div className="space-y-5">
//           <div className="panel flex flex-col items-center p-6">
//             <Gauge
//               size={190}
//               value={success / 10}
//               display={`${success}%`}
//               label="Success odds"
//               sublabel="over 500 runs"
//               warning={success < 50}
//               animating={running}
//             />
//           </div>

//           <div className="panel p-6">
//             <p className="label-xs">Targets</p>
//             <div className="mt-4 space-y-3">
//               <div className="grid gap-1.5">
//                 <Label className="label-xs">Target age</Label>
//                 <Input
//                   type="number"
//                   value={targets.targetAge}
//                   onChange={(e) => setTargets({ ...targets, targetAge: Number(e.target.value) })}
//                 />
//               </div>
//               <div className="grid gap-1.5">
//                 <Label className="label-xs">Target net worth</Label>
//                 <Input
//                   type="number"
//                   value={targets.targetNetWorth}
//                   onChange={(e) =>
//                     setTargets({ ...targets, targetNetWorth: Number(e.target.value) })
//                   }
//                 />
//               </div>
//               <Button
//                 className="w-full"
//                 onClick={() => {
//                   updateProfile(targets);
//                   toast.success("Targets updated");
//                 }}
//               >
//                 Update Targets
//               </Button>
//             </div>
//           </div>
//         </div>
//       </div>

//       <div className="mt-5 panel p-6">
//         <p className="label-xs">Monthly budget</p>
//         <div className="mt-4 grid gap-6 md:grid-cols-4">
//           <Figure label="Income" value={money(p.monthlyIncome)} />
//           <Figure label="Fixed costs" value={money(fixed)} />
//           <Figure label="Discretionary" value={money(discretionary)} />
//           <Figure label="Invested" value={money(monthly)} />
//         </div>
//         <div className="mt-6 flex h-3 overflow-hidden rounded-full bg-muted">
//           <Bar w={(fixed / p.monthlyIncome) * 100} className="bg-foreground" />
//           <Bar w={(discretionary / p.monthlyIncome) * 100} className="bg-muted-foreground" />
//           <Bar w={(monthly / p.monthlyIncome) * 100} className="bg-foreground/30" />
//         </div>
//       </div>
//     </AppShell>
//   );
// }

// function Bar({ w, className }: { w: number; className: string }) {
//   return <div className={className} style={{ width: `${Math.max(0, Math.min(100, w))}%` }} />;
// }

// function Figure({ label, value }: { label: string; value: string }) {
//   return (
//     <div>
//       <p className="label-xs">{label}</p>
//       <p className="mt-1 font-display text-2xl font-semibold">{value}</p>
//     </div>
//   );
// }
import { useEffect, useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Gauge } from "@/components/gauge";
import { useGuard } from "@/lib/use-guard";
import { money, useTwin } from "@/lib/twin-store";
import { tooltipStyle } from "@/routes/dashboard";

export const Route = createFileRoute("/wealth")({
  head: () => ({
    meta: [
      { title: "Wealth Planner — Digital Twin" },
      { name: "description", content: "Monte Carlo and deterministic projections toward your target." },
      { property: "og:title", content: "Wealth Planner — Digital Twin" },
      {
        property: "og:description",
        content: "Monte Carlo and deterministic projections toward your target.",
      },
    ],
  }),
  component: WealthPage,
});

function WealthPage() {
  const ok = useGuard();
  const { state, updateProfile, loadForecast } = useTwin();
  const p = state.profile;

  const [mode, setMode] = useState<"mc" | "det">("mc");
  const [targets, setTargets] = useState({ targetAge: p.targetAge, targetNetWorth: p.targetNetWorth });

  // Fetch the real forecast from the backend when the page loads
  // or when the profile id becomes available (e.g. right after sign-in).
  useEffect(() => {
    if (p.id !== null && p.id !== undefined) {
      loadForecast();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [p.id]);

  const forecast = state.forecast;
  const running = state.forecastLoading;

  // Map backend monte_carlo shape into the {year, p10, p50, p90} shape the chart expects
  const mcData = useMemo(() => {
    if (!forecast) return [];
    const { years, median, p10, p90 } = forecast.monte_carlo;
    return years.map((year, i) => ({
      year,
      p10: p10[i],
      p50: median[i],
      p90: p90[i],
    }));
  }, [forecast]);

  // Map backend deterministic shape into the {year, value} shape the chart expects
  const detData = useMemo(() => {
    if (!forecast) return [];
    return forecast.deterministic.map((row) => ({
      year: row.year,
      value: row.net_worth,
    }));
  }, [forecast]);

  const success = forecast ? Math.round(forecast.probability_of_success * 100) : 0;

  if (!ok) return null;

  const monthly = Math.max(0, p.monthlyIncome - p.monthlyExpenses);
  const discretionary = Math.round(p.monthlyExpenses * 0.35);
  const fixed = p.monthlyExpenses - discretionary;
  const years = Math.max(1, p.targetAge - p.age);

  return (
    <AppShell
      title="Financial Twin"
      subtitle={`${years} years to age ${p.targetAge} · target ${money(p.targetNetWorth)}`}
      actions={
        <>
          <Button
            size="sm"
            onClick={() => {
              setMode("mc");
              loadForecast().then(() => toast.success("Forecast refreshed"));
            }}
            disabled={running}
          >
            {running ? "Running…" : "Run Monte Carlo Model"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => setMode("det")}>
            Show Deterministic Path
          </Button>
        </>
      }
    >
      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <div className={`panel p-6 ${running ? "animate-pulse-glow" : ""}`}>
          <p className="label-xs">
            {mode === "mc" ? "Monte Carlo probability bands" : "Deterministic compound path"}
          </p>

          {state.forecastError && (
            <p className="mt-4 text-sm text-destructive">
              Couldn't load forecast: {state.forecastError}
            </p>
          )}

          {!forecast && !running && !state.forecastError && (
            <p className="mt-4 text-sm text-muted-foreground">
              No forecast yet. Click "Run Monte Carlo Model" to fetch your projection.
            </p>
          )}

          {forecast && (
            <div className="mt-4 h-80">
              <ResponsiveContainer width="100%" height="100%">
                {mode === "mc" ? (
                  <AreaChart data={mcData}>
                    <defs>
                      <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-foreground)" stopOpacity={0.18} />
                        <stop offset="100%" stopColor="var(--color-foreground)" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="var(--color-border)" vertical={false} />
                    <XAxis dataKey="year" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={58} tickFormatter={(v) => `$${Math.round(v / 1000)}k`} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => money(v)} />
                    <Area type="monotone" dataKey="p90" name="90th percentile" stroke="var(--color-foreground)" strokeWidth={1.5} fill="url(#band)" />
                    <Area type="monotone" dataKey="p50" name="Median" stroke="var(--color-foreground)" strokeWidth={2.5} fill="none" />
                    <Area type="monotone" dataKey="p10" name="10th percentile" stroke="var(--color-muted-foreground)" strokeWidth={1.5} strokeDasharray="4 4" fill="none" />
                  </AreaChart>
                ) : (
                  <LineChart data={detData}>
                    <CartesianGrid stroke="var(--color-border)" vertical={false} />
                    <XAxis dataKey="year" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={58} tickFormatter={(v) => `$${Math.round(v / 1000)}k`} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => money(v)} />
                    <Line type="monotone" dataKey="value" name="Projected net worth" stroke="var(--color-foreground)" strokeWidth={2.5} dot={false} />
                  </LineChart>
                )}
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="space-y-5">
          <div className="panel flex flex-col items-center p-6">
            <Gauge
              size={190}
              value={success / 10}
              display={forecast ? `${success}%` : "—"}
              label="Success odds"
              sublabel="from backend simulation"
              warning={forecast ? success < 50 : false}
              animating={running}
            />
          </div>

          <div className="panel p-6">
            <p className="label-xs">Targets</p>
            <div className="mt-4 space-y-3">
              <div className="grid gap-1.5">
                <Label className="label-xs">Target age</Label>
                <Input
                  type="number"
                  value={targets.targetAge}
                  onChange={(e) => setTargets({ ...targets, targetAge: Number(e.target.value) })}
                />
              </div>
              <div className="grid gap-1.5">
                <Label className="label-xs">Target net worth</Label>
                <Input
                  type="number"
                  value={targets.targetNetWorth}
                  onChange={(e) =>
                    setTargets({ ...targets, targetNetWorth: Number(e.target.value) })
                  }
                />
              </div>
              <Button
                className="w-full"
                onClick={async () => {
                  updateProfile(targets);
                  toast.success("Targets updated");
                  await loadForecast(); // re-fetch so the gauge/chart reflect the new target
                }}
              >
                Update Targets
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 panel p-6">
        <p className="label-xs">Monthly budget</p>
        <div className="mt-4 grid gap-6 md:grid-cols-4">
          <Figure label="Income" value={money(p.monthlyIncome)} />
          <Figure label="Fixed costs" value={money(fixed)} />
          <Figure label="Discretionary" value={money(discretionary)} />
          <Figure label="Invested" value={money(monthly)} />
        </div>
        <div className="mt-6 flex h-3 overflow-hidden rounded-full bg-muted">
          <Bar w={(fixed / p.monthlyIncome) * 100} className="bg-foreground" />
          <Bar w={(discretionary / p.monthlyIncome) * 100} className="bg-muted-foreground" />
          <Bar w={(monthly / p.monthlyIncome) * 100} className="bg-foreground/30" />
        </div>
      </div>
    </AppShell>
  );
}

function Bar({ w, className }: { w: number; className: string }) {
  return <div className={className} style={{ width: `${Math.max(0, Math.min(100, w))}%` }} />;
}

function Figure({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="label-xs">{label}</p>
      <p className="mt-1 font-display text-2xl font-semibold">{value}</p>
    </div>
  );
}