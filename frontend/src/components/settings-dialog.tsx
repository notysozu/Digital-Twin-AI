import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { useTwin, type Profile } from "@/lib/twin-store";

const FIELDS: { key: keyof Profile; label: string; type?: string; suffix?: string }[] = [
  { key: "name", label: "Name" },
  { key: "age", label: "Current age", type: "number" },
  { key: "targetAge", label: "Target age", type: "number" },
  { key: "monthlyIncome", label: "Monthly income", type: "number" },
  { key: "monthlyExpenses", label: "Monthly expenses", type: "number" },
  { key: "netWorth", label: "Current net worth", type: "number" },
  { key: "targetNetWorth", label: "Target net worth", type: "number" },
  { key: "savingsRate", label: "Savings rate (%)", type: "number" },
  { key: "sleepHours", label: "Usual sleep (h/night)", type: "number" },
  { key: "studyHours", label: "Study or learning (h/week)", type: "number" },
  { key: "screenTime", label: "Screen time (h/day)", type: "number" },
  { key: "exerciseDays", label: "Active days per week", type: "number" },
  { key: "focusArea", label: "Main focus right now" },
  { key: "goalName", label: "Primary goal" },
  { key: "goalCurrent", label: "Goal progress", type: "number" },
  { key: "goalTarget", label: "Goal target", type: "number" },
];

export function SettingsDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const { state, updateProfile } = useTwin();
  const [draft, setDraft] = useState<Profile>(state.profile);

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (v) setDraft(state.profile);
        onOpenChange(v);
      }}
    >
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Everything your twin uses to model your future. Change it any time.
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="max-h-[55vh] pr-4">
          <div className="grid gap-4 sm:grid-cols-2">
            {FIELDS.map((f) => (
              <div key={String(f.key)} className="grid gap-1.5">
                <Label className="label-xs" htmlFor={String(f.key)}>
                  {f.label}
                </Label>
                <Input
                  id={String(f.key)}
                  type={f.type ?? "text"}
                  value={String(draft[f.key] ?? "")}
                  onChange={(e) =>
                    setDraft({
                      ...draft,
                      [f.key]: f.type === "number" ? Number(e.target.value) : e.target.value,
                    })
                  }
                />
              </div>
            ))}
          </div>
        </ScrollArea>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={async () => {
              try {
                await updateProfile(draft);
                toast.success("Settings saved");
                onOpenChange(false);
              } catch (e: any) {
                toast.error(e.message || "Failed to save settings");
              }
            }}
          >
            Save Settings
          </Button>

        </div>
      </DialogContent>
    </Dialog>
  );
}
