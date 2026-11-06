
import { useId } from "react";

export default function Input({
  label,
  value,
  onChange,
  placeholder = "",
  type = "text",
  error = "",
  ...props
}) {
  const id = useId();
  const errorId = `${id}-error`;

  return (
    <div className="flex w-full flex-col gap-1">
      <label
        htmlFor={id}
        className="text-sm font-medium text-gray-700"
      >
        {label}
      </label>

      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        className={`rounded-md border px-3 py-2
          focus:outline-none focus:ring-2
          focus:ring-green-700
          ${error ? "border-red-600" : "border-gray-300"}
        `}
        {...props}
      />

      {error && (
        <span
          id={errorId}
          role="alert"
          className="text-sm text-red-700"
        >
          {error}
        </span>
      )}
    </div>
  );
}
