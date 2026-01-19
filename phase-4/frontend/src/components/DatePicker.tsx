/**
 * Date Picker Component
 *
 * Task: T028
 * Spec: specs/1-phase2-advanced-features/spec.md (US1)
 */
'use client';

import { format } from 'date-fns';

interface DatePickerProps {
  value?: Date;
  onChange: (date: Date | undefined) => void;
  minDate?: Date;
  label?: string;
}

export function DatePicker({ value, onChange, minDate, label }: DatePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const dateValue = e.target.value;
    if (dateValue) {
      onChange(new Date(dateValue));
    } else {
      onChange(undefined);
    }
  };

  const handleClear = () => {
    onChange(undefined);
  };

  const formattedValue = value ? format(value, "yyyy-MM-dd'T'HH:mm") : '';
  const minDateStr = minDate ? format(minDate, "yyyy-MM-dd'T'HH:mm") : undefined;

  return (
    <div className="flex flex-col gap-2">
      {label && (
        <label className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <div className="flex gap-2">
        <input
          type="datetime-local"
          value={formattedValue}
          onChange={handleChange}
          min={minDateStr}
          className="flex-1 px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-primary/50 transition-all"
        />
        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="px-3 py-2 rounded-lg border border-border bg-background text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
            title="Clear date"
          >
            ✕
          </button>
        )}
      </div>
      {value && (
        <p className="text-xs text-muted-foreground">
          Due: {format(value, 'PPpp')}
        </p>
      )}
    </div>
  );
}
