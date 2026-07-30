import { useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Check, Clock, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { useGuard } from "@/lib/use-guard";
import { today, useTwin, type Task } from "@/lib/twin-store";

export const Route = createFileRoute("/planner")({
  head: () => ({
    meta: [
      { title: "Tasks & Planner — Digital Twin" },
      { name: "description", content: "Today's plan, built from your tasks and adopted suggestions." },
      { property: "og:title", content: "Tasks & Planner — Digital Twin" },
      {
        property: "og:description",
        content: "Today's plan, built from your tasks and adopted suggestions.",
      },
    ],
  }),
  component: PlannerPage,
});

const CATEGORIES: Task["category"][] = ["Work", "Study", "Health", "Money", "Personal"];

function PlannerPage() {
  const ok = useGuard();
  const { state, addTask, toggleTask, removeTask } = useTwin();
  const [title, setTitle] = useState("");
  const [start, setStart] = useState("09:00");
  const [minutes, setMinutes] = useState(45);
  const [category, setCategory] = useState<Task["category"]>("Work");

  const todays = useMemo(
    () =>
      state.tasks
        .filter((t) => t.date === today())
        .slice()
        .sort((a, b) => a.start.localeCompare(b.start)),
    [state.tasks],
  );

  if (!ok) return null;

  const done = todays.filter((t) => t.done).length;
  const planned = todays.reduce((s, t) => s + t.minutes, 0);

  const submit = () => {
    if (!title.trim()) {
      toast.error("Give the task a name");
      return;
    }
    addTask({ title: title.trim(), start, minutes, category, done: false, date: today() });
    setTitle("");
    toast.success("Task added to today's plan");
  };

  return (
    <AppShell
      title="Today's Plan"
      subtitle={`${done} of ${todays.length} done · ${Math.round(planned / 60 * 10) / 10}h scheduled`}
    >
      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <div className="panel divide-y divide-border">
          {todays.length === 0 && (
            <p className="p-8 text-center text-sm text-muted-foreground">
              Nothing planned yet. Add a task, or adopt a suggestion to drop it straight in here.
            </p>
          )}
          {todays.map((t) => (
            <div key={t.id} className="flex items-center gap-4 p-4 transition-colors hover:bg-accent/40">
              <Checkbox checked={t.done} onCheckedChange={() => toggleTask(t.id)} />
              <div className="w-14 shrink-0 font-display text-sm font-semibold tabular-nums">
                {t.start}
              </div>
              <div className="min-w-0 flex-1">
                <p className={`truncate text-sm ${t.done ? "text-muted-foreground line-through" : ""}`}>
                  {t.title}
                </p>
                <p className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="rounded border border-border px-1.5 py-px">{t.category}</span>
                  <Clock className="h-3 w-3" />
                  {t.minutes}m
                  {t.fromSuggestion && <span className="italic">from suggestions</span>}
                </p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => removeTask(t.id)} aria-label="Delete task">
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>

        <div className="space-y-5">
          <div className="panel p-5">
            <p className="label-xs">Add a task</p>
            <div className="mt-4 space-y-3">
              <div className="grid gap-1.5">
                <Label className="label-xs">Task</Label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && submit()}
                  placeholder="Write the report"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label className="label-xs">Start</Label>
                  <Input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
                </div>
                <div className="grid gap-1.5">
                  <Label className="label-xs">Minutes</Label>
                  <Input type="number" value={minutes} onChange={(e) => setMinutes(Number(e.target.value))} />
                </div>
              </div>
              <div className="grid gap-1.5">
                <Label className="label-xs">Category</Label>
                <Select value={category} onValueChange={(v) => setCategory(v as Task["category"])}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map((c) => (
                      <SelectItem key={c} value={c}>
                        {c}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button className="w-full" onClick={submit}>
                <Plus className="mr-2 h-4 w-4" /> Add to plan
              </Button>
            </div>
          </div>

          <div className="panel p-5">
            <p className="label-xs">Timetable</p>
            <div className="mt-4 space-y-1">
              {Array.from({ length: 16 }, (_, i) => i + 6).map((hour) => {
                const slot = todays.find((t) => Number(t.start.slice(0, 2)) === hour);
                return (
                  <div key={hour} className="flex items-center gap-3 text-xs">
                    <span className="w-8 text-muted-foreground tabular-nums">{`${hour}`.padStart(2, "0")}</span>
                    <div
                      className={`h-6 flex-1 rounded border px-2 text-[11px] leading-6 ${
                        slot
                          ? "border-foreground/30 bg-accent font-medium"
                          : "border-dashed border-border text-muted-foreground"
                      }`}
                    >
                      {slot ? slot.title : ""}
                    </div>
                    {slot?.done && <Check className="h-3 w-3" />}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
