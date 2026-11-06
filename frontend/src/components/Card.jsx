
import { useId } from "react";

export default function Card({
  title,
  children,
  footer,
  className = "",
  headingLevel = 3,
  ...props
}) {
  const titleId = useId();

  const Heading =
    headingLevel >= 1 && headingLevel <= 6
      ? `h${headingLevel}`
      : "h3";

  return (
    <article
      aria-labelledby={title ? titleId : undefined}
      className={`
        w-full rounded-lg border border-gray-200
        bg-white p-4 shadow-sm sm:p-6
        ${className}
      `}
      {...props}
    >
      {title && (
        <Heading
          id={titleId}
          className="mb-3 text-lg font-semibold text-gray-800"
        >
          {title}
        </Heading>
      )}

      <div className="text-gray-700">
        {children}
      </div>

      {footer && (
        <footer className="mt-4 border-t border-gray-200 pt-3">
          {footer}
        </footer>
      )}
    </article>
  );
}

