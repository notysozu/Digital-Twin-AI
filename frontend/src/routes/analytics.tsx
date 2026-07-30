import { useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Check } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { HabitDrawer, tooltipStyle } from "@/routes/dashboard";
import { useGuard } from "@/lib/use-guard";
import { baseline, focusIndex, useTwin } from "@/lib/twin-store";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Analytics — Digital Twin" },
      { name: "description", content: "Correlations, streaks and the full history of your logs." },
      { property: "og:title", content: "Analytics — Digital Twin" },
      {
        property: "og:description",
        content: "Correlations, streaks and the full history of your logs.",
      },
    ],
  }),
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const ok = useGuard();
  const { state, addLog, clearLogs } = useTwin();
  const [drawer, setDrawer] = useState(false);

  const base = useMemo(() => baseline(state.logs), [state.logs]);
  const scatter = useMemo(
    () =>
      state.logs.map((l) => ({
        sleep: l.sleep,
        focus: focusIndex(l.sleep, l.study, l.screen),
        z: Math.max(20, l.exercise),
      })),
    [state.logs],
  );
  const screenScatter = useMemo(
    () => state.logs.map((l) => ({ screen: l.screen, mood: l.mood, z: 40 })),
    [state.logs],
  );
  const week = state.logs.slice(-7);

  if (!ok) return null;

  const exportCsv = () => {
    const rows = [
      ["date", "sleep", "screen", "study", "exercise", "mood"],
      ...state.logs.map((l) => [l.date, l.sleep, l.screen, l.study, l.exercise, l.mood]),
    ];
    const blob = new Blob([rows.map((r) => r.join(",")).join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "twin-history.csv";
    a.click();
    URL.revokeObjectURL(url);
    toast.success("History exported");
  };

  return (
    <AppShell
      title="Analytics"
      subtitle={`${base.days} days of history`}
      actions={
        <>
          <Button size="sm" onClick={() => setDrawer(true)}>
            Log Daily Activities
          </Button>
          <Button size="sm" variant="outline" onClick={exportCsv}>
            Export History (CSV)
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button size="sm" variant="ghost">
                Clear All Logs
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete your entire log history?</AlertDialogTitle>
                <AlertDialogDescription>
                  This removes every logged day from this browser. It cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => {
                    clearLogs();
                    toast.success("Logs cleared");
                  }}
                >
                  Delete everything
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </>
      }
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <ChartCard title="Sleep hours vs focus rating">
          <ScatterChart>
            <CartesianGrid stroke="var(--color-border)" />
            <XAxis dataKey="sleep" name="Sleep" unit="h" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis dataKey="focus" name="Focus" domain={[0, 10]} stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={26} />
            <ZAxis dataKey="z" range={[40, 180]} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={scatter} fill="var(--color-foreground)" fillOpacity={0.55} />
          </ScatterChart>
        </ChartCard>

        <ChartCard title="Screen time vs mood">
          <ScatterChart>
            <CartesianGrid stroke="var(--color-border)" />
            <XAxis dataKey="screen" name="Screen" unit="h" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis dataKey="mood" name="Mood" domain={[0, 10]} stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={26} />
            <ZAxis dataKey="z" range={[40, 140]} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={screenScatter} fill="var(--color-muted-foreground)" fillOpacity={0.7} />
          </ScatterChart>
        </ChartCard>
      </div>

      <div className="panel mt-5 p-6">
        <p className="label-xs">Weekly streak</p>
        <div className="mt-4 grid grid-cols-7 gap-2">
          {week.map((l) => {
            const hit = l.sleep >= 7 && l.study >= 1;
            return (
              <div
                key={l.id}
                className={`flex aspect-square flex-col items-center justify-center rounded-md border text-xs ${
                  hit
                    ? "border-foreground/40 bg-accent shadow-[0_0_18px_-8px_var(--color-foreground)]"
                    : "border-dashed border-border text-muted-foreground"
                }`}
              >
                {hit ? <Check className="h-4 w-4" /> : <span>—</span>}
                <span className="mt-1">{l.date.slice(5)}</span>
              </div>
            );
          })}
          {week.length === 0 && (
            <p className="col-span-7 py-6 text-center text-sm text-muted-foreground">No logs yet.</p>
          )}
        </div>
      </div>

      <div className="panel mt-5 overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Sleep</TableHead>
              <TableHead>Screen</TableHead>
              <TableHead>Study</TableHead>
              <TableHead>Exercise</TableHead>
              <TableHead>Mood</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {state.logs
              .slice()
              .reverse()
              .slice(0, 15)
              .map((l) => (
                <TableRow key={l.id}>
                  <TableCell>{l.date}</TableCell>
                  <TableCell>{l.sleep}h</TableCell>
                  <TableCell>{l.screen}h</TableCell>
                  <TableCell>{l.study}h</TableCell>
                  <TableCell>{l.exercise}m</TableCell>
                  <TableCell>{l.mood}</TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </div>

      <HabitDrawer open={drawer} onOpenChange={setDrawer} onSave={addLog} />
    </AppShell>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactElement }) {
  return (
    <div className="panel p-6">
      <p className="label-xs">{title}</p>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
