
export default function Button({
  children,
  variant = "primary",
  loading = false,
  disabled = false,
  onClick,
  type = "button",
  ...props
}) {
  const baseStyles = `
    inline-flex items-center justify-center gap-2
    rounded-md px-4 py-2 font-medium
    transition-colors
    focus-visible:outline
    focus-visible:outline-2
    focus-visible:outline-offset-2
    focus-visible:outline-green-800
    disabled:cursor-not-allowed
    disabled:cursor-not-allowed
  `;

  const variants = {
    primary:
      "bg-green-700 text-white hover:bg-green-800",
    secondary:
      "bg-gray-200 text-gray-800 hover:bg-gray-300",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      aria-busy={loading}
      className={`${baseStyles} ${variants[variant]}`}
      {...props}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="
            h-4 w-4 animate-spin rounded-full
            border-2 border-current
            border-t-transparent
          "
        />
      )}

      {loading ? "Cargando..." : children}
    </button>
  );
}

