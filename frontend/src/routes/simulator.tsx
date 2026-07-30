import { useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CheckCircle2, TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { useGuard } from "@/lib/use-guard";
import { focusIndex, healthIndex, money, projectNetWorth, useTwin } from "@/lib/twin-store";
import { tooltipStyle } from "@/routes/dashboard";
import { compareScenarios } from "@/lib/api";


export const Route = createFileRoute("/simulator")({
  head: () => ({
    meta: [
      { title: "What-If Simulator — Digital Twin" },
      { name: "description", content: "Compare two versions of the next five years side by side." },
      { property: "og:title", content: "What-If Simulator — Digital Twin" },
      {
        property: "og:description",
        content: "Compare two versions of the next five years side by side.",
      },
    ],
  }),
  component: SimulatorPage,
});

type Scenario = { savings: number; sleep: number; study: number };
const ZERO: Scenario = { savings: 0, sleep: 0, study: 0 };

function SimulatorPage() {
  const ok = useGuard();
  const { state, updateProfile } = useTwin();
  const p = state.profile;
  const [a, setA] = useState<Scenario>({ savings: 400, sleep: 0.5, study: 4 });
  const [b, setB] = useState<Scenario>({ savings: 1200, sleep: -1, study: 12 });
  const [dragging, setDragging] = useState(false);
  const [ran, setRan] = useState(true);
  const [burst, setBurst] = useState(false);
  const [backendResult, setBackendResult] = useState<any>(null);


  const monthlyBase = Math.max(0, p.monthlyIncome - p.monthlyExpenses);

  const evaluate = (s: Scenario) => {
    const sleep = p.sleepHours + s.sleep;
    const study = p.studyHours / 7 + s.study / 7;
    const health = healthIndex(sleep, p.exerciseDays * 20, p.screenTime);
    const focus = focusIndex(sleep, study, p.screenTime);
    const path = projectNetWorth(p.netWorth, monthlyBase + s.savings, 5);
    return { sleep, health, focus, path, terminal: path[path.length - 1].value };
  };

  const A = useMemo(() => evaluate(a), [a, p]);
  const B = useMemo(() => evaluate(b), [b, p]);

  const chart = useMemo(() => {
    if (backendResult) {
      return backendResult.scenario_a.datapoints.map((dp: any, i: number) => ({
        year: `Y${dp.year}`,
        netA: dp.net_worth,
        netB: backendResult.scenario_b.datapoints[i].net_worth,
        focusA: dp.focus_index,
        focusB: backendResult.scenario_b.datapoints[i].focus_index
      }));
    }
    return A.path.map((row, i) => ({
      year: `Y${row.year}`,
      netA: row.value,
      netB: B.path[i].value,
      focusA: +(A.focus - i * 0.02).toFixed(2),
      focusB: +(B.focus - i * 0.05).toFixed(2),
    }));
  }, [A, B, backendResult]);

  const runComparison = async () => {
    const userId = p.id;
    if (!userId) {
      toast.error("Sign in first to run comparisons");
      return;
    }
    setRan(false);
    try {
      const result = await compareScenarios(userId, {
        scenario_a: {
          monthly_investment_change: a.savings,
          sleep_hours_change: a.sleep,
          weekly_study_change: a.study
        },
        scenario_b: {
          monthly_investment_change: b.savings,
          sleep_hours_change: b.sleep,
          weekly_study_change: b.study
        },
        years: 5
      });
      setBackendResult(result);
      toast.success("Comparative analysis complete");
    } catch (e: any) {
      toast.error(e.message || "Failed to run simulation comparison");
    } finally {
      setRan(true);
    }
  };


  if (!ok) return null;

  const verdict = () => {
    const better = B.terminal > A.terminal ? "B" : "A";
    const worse = better === "A" ? B : A;
    const win = better === "A" ? A : B;
    const gap = Math.abs(A.terminal - B.terminal);
    return [
      `> comparing scenario a and scenario b over 60 months`,
      `> net worth delta: ${money(gap)} in favour of scenario ${better.toLowerCase()}`,
      `> health index: A ${A.health} / B ${B.health}`,
      `> focus index: A ${A.focus} / B ${B.focus}`,
      worse.health < 5
        ? `> warning: scenario ${better === "A" ? "b" : "a"} drops health below 5.0 — burnout risk`
        : `> both scenarios keep health above the safe floor`,
      `> VERDICT: adopt scenario ${better.toLowerCase()} — it reaches ${money(
        win.terminal,
      )} while holding focus at ${win.focus}.`,
    ];
  };

  const adopt = (s: Scenario, name: string) => {
    const r = evaluate(s);
    updateProfile({
      sleepHours: +r.sleep.toFixed(1),
      studyHours: Math.max(0, p.studyHours + s.study),
      savingsRate: Math.min(
        95,
        Math.round(((monthlyBase + s.savings) / Math.max(1, p.monthlyIncome)) * 100),
      ),
    });
    setBurst(true);
    setTimeout(() => setBurst(false), 600);
    toast.success(`Scenario ${name} adopted as your active metrics`);
  };

  return (
    <AppShell
      title="Decision Sandbox"
      subtitle="Move the sliders. The twin re-runs the next five years instantly."
      actions={
        <>
          <Button
            size="sm"
            onClick={runComparison}
          >
            Run Comparative Analysis
          </Button>
          <Button size="sm" variant="outline" onClick={() => adopt(a, "A")}>
            Adopt Scenario A
          </Button>
          <Button size="sm" variant="outline" onClick={() => adopt(b, "B")}>
            Adopt Scenario B
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setA(ZERO);
              setB(ZERO);
              setBackendResult(null);
              toast("Sandbox reset to your baseline");
            }}
          >
            Reset Sandbox
          </Button>
        </>
      }
    >

      <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
        <div className="space-y-5">
          <ScenarioCard name="A" s={a} set={setA} result={A} onDrag={setDragging} />
          <ScenarioCard name="B" s={b} set={setB} result={B} onDrag={setDragging} />
        </div>

        <div className="space-y-5">
          <div
            className={`panel p-6 ${dragging || !ran ? "animate-pulse-glow" : ""}`}
          >
            <div className="flex items-center justify-between">
              <p className="label-xs">Future trajectory comparison</p>
              <span className="text-xs text-muted-foreground">
                {dragging || !ran ? "Syncing twin forecast…" : "Synced"}
              </span>
            </div>
            <div className="mt-4 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chart}>
                  <CartesianGrid stroke="var(--color-border)" vertical={false} />
                  <XAxis dataKey="year" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis yAxisId="left" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={58} tickFormatter={(v) => `$${Math.round(v / 1000)}k`} />
                  <YAxis yAxisId="right" orientation="right" domain={[0, 10]} stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={26} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line yAxisId="left" type="monotone" dataKey="netA" name="Net worth A" stroke="var(--color-foreground)" strokeWidth={2} dot={false} />
                  <Line yAxisId="left" type="monotone" dataKey="netB" name="Net worth B" stroke="var(--color-muted-foreground)" strokeWidth={2} dot={false} />
                  <Line yAxisId="right" type="monotone" dataKey="focusA" name="Focus A" stroke="var(--color-foreground)" strokeDasharray="3 3" strokeWidth={1.5} dot={false} />
                  <Line yAxisId="right" type="monotone" dataKey="focusB" name="Focus B" stroke="var(--color-muted-foreground)" strokeDasharray="3 3" strokeWidth={1.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel p-6 font-mono text-xs leading-relaxed">
            <div className="flex items-center justify-between pb-3">
              <p className="label-xs font-sans">Twin advisor verdict</p>
              {burst && (
                <span className="flex items-center gap-1 text-xs text-foreground animate-pulse-glow rounded-full px-2">
                  <CheckCircle2 className="h-4 w-4" /> adopted
                </span>
              )}
            </div>
            <div className="space-y-1 border-t border-border pt-3 text-muted-foreground font-sans">
              {backendResult ? (
                <div className="whitespace-pre-line text-sm text-foreground">
                  {backendResult.recommendation}
                </div>
              ) : (
                verdict().map((line) => (
                  <p key={line} className={line.startsWith("> VERDICT") ? "text-foreground" : ""}>
                    {line}
                  </p>
                ))
              )}
            </div>
          </div>

        </div>
      </div>
    </AppShell>
  );
}

function ScenarioCard({
  name,
  s,
  set,
  result,
  onDrag,
}: {
  name: string;
  s: Scenario;
  set: (v: Scenario) => void;
  result: { health: number; focus: number; terminal: number };
  onDrag: (v: boolean) => void;
}) {
  const warn = result.health < 5 || result.focus < 5;
  return (
    <div
      className={`panel p-5 transition-all ${
        warn ? "border-foreground/60 shadow-[0_0_22px_-10px_var(--color-foreground)]" : ""
      }`}
    >
      <div className="flex items-center justify-between">
        <p className="label-xs">Scenario {name}</p>
        {warn && (
          <span className="flex items-center gap-1 text-xs text-foreground">
            <TriangleAlert className="h-3.5 w-3.5" /> burnout risk
          </span>
        )}
      </div>

      <div className="mt-5 space-y-6">
        <SliderRow
          label="Monthly savings change"
          value={s.savings}
          display={`+$${s.savings}`}
          min={0}
          max={2000}
          step={50}
          onChange={(v) => set({ ...s, savings: v })}
          onDrag={onDrag}
        />
        <SliderRow
          label="Sleep change"
          value={s.sleep}
          display={`${s.sleep > 0 ? "+" : ""}${s.sleep}h`}
          min={-2}
          max={3}
          step={0.5}
          onChange={(v) => set({ ...s, sleep: v })}
          onDrag={onDrag}
        />
        <SliderRow
          label="Weekly study change"
          value={s.study}
          display={`${s.study > 0 ? "+" : ""}${s.study}h`}
          min={-10}
          max={20}
          step={1}
          onChange={(v) => set({ ...s, study: v })}
          onDrag={onDrag}
        />
      </div>

      <div className="mt-6 grid grid-cols-3 gap-3 border-t border-border pt-4 text-center">
        <Mini label="Health" value={result.health.toFixed(1)} />
        <Mini label="Focus" value={result.focus.toFixed(1)} />
        <Mini label="5y net" value={money(result.terminal)} />
      </div>
    </div>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="label-xs">{label}</p>
      <p className="mt-1 font-display text-sm font-semibold">{value}</p>
    </div>
  );
}

function SliderRow({
  label,
  value,
  display,
  min,
  max,
  step,
  onChange,
  onDrag,
}: {
  label: string;
  value: number;
  display: string;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  onDrag: (v: boolean) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="label-xs">{label}</span>
        <span className="font-display font-semibold tabular-nums">{display}</span>
      </div>
      <Slider
        className="mt-3"
        min={min}
        max={max}
        step={step}
        value={[value]}
        onValueChange={([v]) => {
          onDrag(true);
          onChange(v);
        }}
        onValueCommit={() => onDrag(false)}
      />
    </div>
  );
}
