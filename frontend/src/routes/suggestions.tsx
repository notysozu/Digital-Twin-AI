import { createFileRoute } from "@tanstack/react-router";
import { Check, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { useGuard } from "@/lib/use-guard";
import { SUGGESTIONS, baseline, useTwin } from "@/lib/twin-store";

export const Route = createFileRoute("/suggestions")({
  head: () => ({
    meta: [
      { title: "Suggestions — Digital Twin" },
      { name: "description", content: "Ideas your twin recommends, ready to drop into today's plan." },
      { property: "og:title", content: "Suggestions — Digital Twin" },
      {
        property: "og:description",
        content: "Ideas your twin recommends, ready to drop into today's plan.",
      },
    ],
  }),
  component: SuggestionsPage,
});

function SuggestionsPage() {
  const ok = useGuard();
  const { state, adopt } = useTwin();
  if (!ok) return null;

  const base = baseline(state.logs);

  return (
    <AppShell
      title="Suggestions"
      subtitle="Kept separate from your task list until you choose to adopt one."
    >
      <div className="panel mb-5 p-5 text-sm text-muted-foreground">
        Based on {base.days || 0} logged days: sleep {base.sleep || state.profile.sleepHours}h,
        screen {base.screen || state.profile.screenTime}h, study{" "}
        {base.study || (state.profile.studyHours / 7).toFixed(1)}h per day.
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {SUGGESTIONS.map((s) => {
          const taken = state.adopted.includes(s.id);
          return (
            <div
              key={s.id}
              className="panel flex flex-col justify-between p-5 transition-shadow hover:shadow-[0_0_24px_-10px_var(--color-foreground)]"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="label-xs">{s.category}</span>
                  <span className="text-xs text-muted-foreground">{s.impact}</span>
                </div>
                <h3 className="mt-3 font-display text-lg font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.detail}</p>
              </div>
              <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
                <span className="text-xs text-muted-foreground">
                  {s.start} · {s.minutes} min
                </span>
                <Button
                  size="sm"
                  variant={taken ? "ghost" : "default"}
                  disabled={taken}
                  onClick={() => {
                    adopt(s);
                    toast.success("Added to today's plan");
                  }}
                >
                  {taken ? (
                    <>
                      <Check className="mr-2 h-4 w-4" /> In your plan
                    </>
                  ) : (
                    <>
                      <Plus className="mr-2 h-4 w-4" /> Add to tasks
                    </>
                  )}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </AppShell>
  );
}
