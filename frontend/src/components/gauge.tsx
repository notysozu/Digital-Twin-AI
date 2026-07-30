import { useMemo } from "react";

type Props = {
  value: number;
  max?: number;
  label: string;
  sublabel?: string;
  size?: number;
  warning?: boolean;
  animating?: boolean;
  display?: string;
};

export function Gauge({
  value,
  max = 10,
  label,
  sublabel,
  size = 190,
  warning = false,
  animating = false,
  display,
}: Props) {
  const pct = Math.max(0, Math.min(1, value / max));
  const r = size / 2 - 14;
  const c = 2 * Math.PI * r;
  const dash = useMemo(() => `${(c * pct * 0.75).toFixed(2)} ${c}`, [c, pct]);

  return (
    <div className="flex max-w-full flex-col items-center">
      <div
        className={`relative rounded-full transition-all ${
          animating ? "animate-pulse-glow" : ""
        }`}
        style={{ width: size, height: size }}
      >
        <svg width={size} height={size} className="-rotate-[135deg]">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="currentColor"
            className="text-border"
            strokeWidth={10}
            strokeDasharray={`${(c * 0.75).toFixed(2)} ${c}`}
            strokeLinecap="round"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="currentColor"
            className={warning ? "text-muted-foreground" : "text-foreground"}
            strokeWidth={10}
            strokeDasharray={dash}
            strokeLinecap="round"
            style={{ transition: "stroke-dasharray 600ms cubic-bezier(.4,0,.2,1)" }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center font-display text-4xl font-semibold tabular-nums">
          {display ?? value.toFixed(1)}
        </span>
      </div>
      <span className="label-xs mt-2 text-center">{label}</span>
      {sublabel ? (
        <span className="mt-1 text-center text-xs text-muted-foreground">{sublabel}</span>
      ) : null}
    </div>
  );
}
