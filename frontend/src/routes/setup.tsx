import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { useTwin, type Profile } from "@/lib/twin-store";
import { toast } from "sonner";

export const Route = createFileRoute("/setup")({
  head: () => ({
    meta: [
      { title: "Set up your twin — Digital Twin" },
      { name: "description", content: "Answer a few questions so your twin can model your life." },
      { property: "og:title", content: "Set up your twin — Digital Twin" },
      {
        property: "og:description",
        content: "Answer a few questions so your twin can model your life.",
      },
    ],
  }),
  component: SetupPage,
});

type Q = {
  key: keyof Profile;
  question: string;
  hint: string;
  kind: "slider" | "text" | "number";
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
};

const QUESTIONS: Q[] = [
  { key: "age", question: "How old are you?", hint: "Sets the starting point of every projection.", kind: "slider", min: 16, max: 75, step: 1 },
  { key: "targetAge", question: "By what age do you want to be financially free?", hint: "Your horizon for the wealth model.", kind: "slider", min: 30, max: 80, step: 1 },
  { key: "monthlyIncome", question: "What comes in each month?", hint: "Take-home income after tax.", kind: "slider", min: 0, max: 20000, step: 100, unit: "$" },
  { key: "monthlyExpenses", question: "What goes out each month?", hint: "Rent, food, subscriptions, everything.", kind: "slider", min: 0, max: 15000, step: 100, unit: "$" },
  { key: "netWorth", question: "What have you saved so far?", hint: "Cash plus investments, minus debt.", kind: "number", unit: "$" },
  { key: "targetNetWorth", question: "What number would feel like enough?", hint: "Your long-term target.", kind: "number", unit: "$" },
  { key: "sleepHours", question: "How many hours do you usually sleep?", hint: "The single strongest driver of your focus score.", kind: "slider", min: 3, max: 11, step: 0.5, unit: "h" },
  { key: "screenTime", question: "How much screen time on an average day?", hint: "Outside of work.", kind: "slider", min: 0, max: 12, step: 0.5, unit: "h" },
  { key: "studyHours", question: "Hours a week on learning or side work?", hint: "Courses, reading, building.", kind: "slider", min: 0, max: 40, step: 0.5, unit: "h" },
  { key: "exerciseDays", question: "How many active days per week?", hint: "Any movement counts.", kind: "slider", min: 0, max: 7, step: 1 },
  { key: "focusArea", question: "What are you focused on right now?", hint: "One line is enough.", kind: "text" },
  { key: "goalName", question: "Name your first goal.", hint: "Something you can finish this year.", kind: "text" },
  { key: "goalTarget", question: "What does that goal cost?", hint: "The finish line in dollars.", kind: "number", unit: "$" },
  { key: "goalCurrent", question: "How far along are you?", hint: "Already saved toward it.", kind: "number", unit: "$" },
];

function SetupPage() {
  const { state, updateProfile } = useTwin();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [dir, setDir] = useState<1 | -1>(1);
  const [draft, setDraft] = useState<Profile>(state.profile);

  const q = QUESTIONS[step];
  const value = draft[q.key];
  const progress = ((step + 1) / QUESTIONS.length) * 100;

  const next = () => {
    if (step === QUESTIONS.length - 1) {
      const savingsRate = Math.max(
        0,
        Math.round(
          ((draft.monthlyIncome - draft.monthlyExpenses) / Math.max(1, draft.monthlyIncome)) * 100,
        ),
      );
      updateProfile({ ...draft, savingsRate, onboarded: true });
      toast.success("Twin initialised");
      navigate({ to: "/" });
      return;
    }
    setDir(1);
    setStep((s) => s + 1);
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <div className="h-0.5 w-full bg-border">
        <div
          className="h-full bg-foreground transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex flex-1 items-center justify-center overflow-hidden px-6">
        <div
          key={step}
          className="w-full max-w-xl"
          style={{
            animation: `slide-q 420ms cubic-bezier(.22,1,.36,1) both`,
            ["--from" as string]: dir === 1 ? "56px" : "-56px",
          }}
        >
          <p className="label-xs">
            Question {step + 1} of {QUESTIONS.length}
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold leading-tight md:text-4xl">
            {q.question}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">{q.hint}</p>

          <div className="mt-10">
            {q.kind === "slider" ? (
              <div>
                <div className="font-display text-5xl font-semibold tabular-nums">
                  {q.unit === "$" ? "$" : ""}
                  {Number(value).toLocaleString()}
                  {q.unit && q.unit !== "$" ? q.unit : ""}
                </div>
                <Slider
                  className="mt-8"
                  min={q.min}
                  max={q.max}
                  step={q.step}
                  value={[Number(value)]}
                  onValueChange={([v]) => setDraft({ ...draft, [q.key]: v })}
                />
                <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                  <span>{q.min}</span>
                  <span>{q.max}</span>
                </div>
              </div>
            ) : (
              <Input
                autoFocus
                type={q.kind === "number" ? "number" : "text"}
                value={String(value ?? "")}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    [q.key]: q.kind === "number" ? Number(e.target.value) : e.target.value,
                  })
                }
                onKeyDown={(e) => e.key === "Enter" && next()}
                className="h-14 border-0 border-b border-border bg-transparent px-0 font-display !text-3xl shadow-none focus-visible:ring-0"
                placeholder="Type your answer"
              />
            )}
          </div>

          <div className="mt-12 flex items-center gap-3">
            <Button
              variant="ghost"
              disabled={step === 0}
              onClick={() => {
                setDir(-1);
                setStep((s) => Math.max(0, s - 1));
              }}
            >
              <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </Button>
            <Button onClick={next}>
              {step === QUESTIONS.length - 1 ? (
                <>
                  <Check className="mr-2 h-4 w-4" /> Finish setup
                </>
              ) : (
                <>
                  Next <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      <style>{`@keyframes slide-q { from { opacity:0; transform: translateX(var(--from)); } to { opacity:1; transform:none; } }`}</style>
    </div>
  );
}
