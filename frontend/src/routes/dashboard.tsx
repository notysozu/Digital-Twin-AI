import { useMemo, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowUpRight, BookOpen, MoonStar, Plus, RefreshCw, Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Gauge } from "@/components/gauge";
import { useIsMobile } from "@/hooks/use-mobile";
import { useGuard } from "@/lib/use-guard";
import { baseline, focusIndex, healthIndex, money, today, useTwin } from "@/lib/twin-store";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Twin Core — Digital Twin" },
      { name: "description", content: "Your live indices, feed and daily numbers in one view." },
      { property: "og:title", content: "Twin Core — Digital Twin" },
      {
        property: "og:description",
        content: "Your live indices, feed and daily numbers in one view.",
      },
    ],
  }),
  component: DashboardPage,
});

function DashboardPage() {
  const ok = useGuard();
  const navigate = useNavigate();
  const { state, addLog, addTxn } = useTwin();
  const [drawer, setDrawer] = useState(false);
  const [txnOpen, setTxnOpen] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [stamp, setStamp] = useState<number>(0);
  const isMobile = useIsMobile();
  const gaugeSize = isMobile ? 150 : 190;

  const base = useMemo(() => baseline(state.logs), [state.logs, stamp]);
  const p = state.profile;
  const health = base.days
    ? healthIndex(base.sleep, base.exercise, base.screen)
    : healthIndex(p.sleepHours, p.exerciseDays * 20, p.screenTime);
  const focus = base.days
    ? focusIndex(base.sleep, base.study, base.screen)
    : focusIndex(p.sleepHours, p.studyHours / 7, p.screenTime);

  const trend = useMemo(
    () =>
      state.logs.slice(-14).map((l) => ({
        date: l.date.slice(5),
        focus: focusIndex(l.sleep, l.study, l.screen),
        health: healthIndex(l.sleep, l.exercise, l.screen),
      })),
    [state.logs],
  );

  if (!ok) return null;

  const goalPct = Math.min(100, Math.round((p.goalCurrent / Math.max(1, p.goalTarget)) * 100));

  return (
    <AppShell
      title="Twin Core"
      subtitle={`Modelled on ${base.days || 0} days of logged history`}
      actions={
        <>
          <Button size="sm" onClick={() => setDrawer(true)}>
            Log Daily Habits
          </Button>
          <Button size="sm" variant="outline" onClick={() => setTxnOpen(true)}>
            Record Transaction
          </Button>
          <Button size="sm" variant="outline" onClick={() => navigate({ to: "/simulator" })}>
            Optimize Routine
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setSyncing(true);
              setTimeout(() => {
                setStamp(Date.now());
                setSyncing(false);
                toast.success("Baseline recalculated from local history");
              }, 900);
            }}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${syncing ? "animate-spin" : ""}`} />
            Refresh Twin Status
          </Button>
        </>
      }
    >
      <div className="grid gap-5 lg:grid-cols-3">
        <div className="panel flex flex-wrap items-center justify-around gap-4 p-6 lg:col-span-2">
          <Gauge
            size={gaugeSize}
            value={health}
            label="Health & Vitality"
            sublabel={health < 5 ? "Burnout risk" : "Steady"}
            warning={health < 5}
            animating={syncing}
          />
          <Gauge
            size={gaugeSize}
            value={focus}
            label="Cognitive Focus"
            sublabel={focus < 5 ? "Below target" : "On track"}
            warning={focus < 5}
            animating={syncing}
          />
        </div>

        <div className="panel p-6">
          <p className="label-xs">Twin Status Feed</p>
          <div className="mt-4 space-y-4 text-sm">
            <FeedItem
              text={`Screen time is averaging ${base.screen || p.screenTime}h. Focus prediction moves ${
                (base.screen || p.screenTime) > 4 ? "down 4%" : "up 3%"
              } at this level.`}
            />
            <FeedItem
              text={`Sleep baseline sits at ${base.sleep || p.sleepHours}h. Adding 30 minutes lifts the vitality index by about 0.6.`}
            />
            <FeedItem
              text={`At ${p.savingsRate}% savings you clear ${money(
                (p.monthlyIncome - p.monthlyExpenses) * 12,
              )} per year toward ${p.goalName}.`}
            />
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-5 sm:grid-cols-3">
        <Stat icon={Wallet} label="Current net worth" value={money(p.netWorth)} />
        <Stat icon={MoonStar} label="Daily sleep" value={`${base.sleep || p.sleepHours}h`} />
        <Stat
          icon={BookOpen}
          label="Weekly study hours"
          value={`${base.days ? (base.study * 7).toFixed(1) : p.studyHours}h`}
        />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-3">
        <div className="panel p-6 lg:col-span-2">
          <p className="label-xs">Index trend — last 14 days</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-foreground)" stopOpacity={0.28} />
                    <stop offset="100%" stopColor="var(--color-foreground)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="date" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis domain={[0, 10]} stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={24} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="focus" stroke="var(--color-foreground)" fill="url(#g1)" strokeWidth={2} />
                <Area type="monotone" dataKey="health" stroke="var(--color-muted-foreground)" fill="none" strokeWidth={1.5} strokeDasharray="4 4" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel flex flex-col justify-between p-6">
          <div>
            <p className="label-xs">Primary goal</p>
            <h3 className="mt-2 font-display text-xl font-semibold">{p.goalName}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {money(p.goalCurrent)} of {money(p.goalTarget)}
            </p>
          </div>
          <div className="mt-6">
            <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-foreground transition-all duration-700"
                style={{ width: `${goalPct}%` }}
              />
            </div>
            <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
              <span>{goalPct}% complete</span>
              <span className="flex items-center gap-1">
                <ArrowUpRight className="h-3 w-3" /> on track
              </span>
            </div>
          </div>
        </div>
      </div>

      <HabitDrawer open={drawer} onOpenChange={setDrawer} onSave={addLog} />
      <TxnDialog open={txnOpen} onOpenChange={setTxnOpen} onSave={addTxn} />
    </AppShell>
  );
}

export const tooltipStyle = {
  background: "var(--color-popover)",
  border: "1px solid var(--color-border)",
  borderRadius: 8,
  fontSize: 12,
  color: "var(--color-popover-foreground)",
};

function FeedItem({ text }: { text: string }) {
  return (
    <div className="border-l border-border pl-4">
      <p className="text-sm leading-relaxed text-muted-foreground">{text}</p>
    </div>
  );
}

function Stat({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Wallet;
  label: string;
  value: string;
}) {
  return (
    <div className="panel flex items-center gap-4 p-5 transition-shadow hover:shadow-[0_0_22px_-8px_var(--color-foreground)]">
      <div className="rounded-md border border-border p-2">
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <p className="label-xs">{label}</p>
        <p className="font-display text-xl font-semibold">{value}</p>
      </div>
    </div>
  );
}

export function HabitDrawer({
  open,
  onOpenChange,
  onSave,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (l: { date: string; sleep: number; screen: number; study: number; exercise: number; mood: number }) => void;
}) {
  const [f, setF] = useState({ date: today(), sleep: 7.5, screen: 4, study: 1.5, exercise: 30, mood: 7 });

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Log daily activities</SheetTitle>
          <SheetDescription>Sleep, screen time, study and movement for one day.</SheetDescription>
        </SheetHeader>
        <div className="mt-6 space-y-4 px-4 pb-6">
          {(
            [
              ["date", "Date", "date"],
              ["sleep", "Sleep (hours)", "number"],
              ["screen", "Screen time (hours)", "number"],
              ["study", "Study / deep work (hours)", "number"],
              ["exercise", "Exercise (minutes)", "number"],
              ["mood", "Mood / energy (1-10)", "number"],
            ] as const
          ).map(([key, label, type]) => (
            <div key={key} className="grid gap-1.5">
              <Label className="label-xs" htmlFor={key}>
                {label}
              </Label>
              <Input
                id={key}
                type={type}
                value={String(f[key])}
                onChange={(e) =>
                  setF({ ...f, [key]: type === "number" ? Number(e.target.value) : e.target.value })
                }
              />
            </div>
          ))}
          <div className="flex gap-2 pt-2">
            <Button
              className="flex-1"
              onClick={() => {
                if (f.sleep <= 0 || f.sleep > 16) {
                  toast.error("Sleep must be between 0 and 16 hours");
                  return;
                }
                onSave(f);
                toast.success("Log submitted");
                onOpenChange(false);
              }}
            >
              Submit Log
            </Button>
            <Button variant="ghost" className="flex-1" onClick={() => onOpenChange(false)}>
              Cancel Log
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

export function TxnDialog({
  open,
  onOpenChange,
  onSave,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (t: { date: string; label: string; amount: number; kind: "income" | "expense" }) => void;
}) {
  const [label, setLabel] = useState("");
  const [amount, setAmount] = useState(0);
  const [kind, setKind] = useState<"income" | "expense">("expense");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Record transaction</DialogTitle>
          <DialogDescription>Money in or out — it updates your net worth.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid gap-1.5">
            <Label className="label-xs">Description</Label>
            <Input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Groceries" />
          </div>
          <div className="grid gap-1.5">
            <Label className="label-xs">Amount</Label>
            <Input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} />
          </div>
          <div className="grid gap-1.5">
            <Label className="label-xs">Type</Label>
            <Select value={kind} onValueChange={(v) => setKind(v as "income" | "expense")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="expense">Expense</SelectItem>
                <SelectItem value="income">Income</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button
            className="w-full"
            onClick={() => {
              if (!label || amount <= 0) {
                toast.error("Add a description and a positive amount");
                return;
              }
              onSave({ date: today(), label, amount, kind });
              toast.success("Transaction recorded");
              setLabel("");
              setAmount(0);
              onOpenChange(false);
            }}
          >
            <Plus className="mr-2 h-4 w-4" /> Save transaction
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
