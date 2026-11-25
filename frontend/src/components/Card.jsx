import { useId } from 'react';

export default function Card({ title, children, footer, className = '', headingLevel = 3, ...props }) {
  const titleId = useId();
  const Heading = headingLevel >= 1 && headingLevel <= 6 ? `h${headingLevel}` : 'h3';

  return (
    <article
      aria-labelledby={title ? titleId : undefined}
      className={`w-full rounded-md border border-linea bg-white p-5 sm:p-6 ${className}`}
      {...props}
    >
      {title && (
        <Heading id={titleId} className="ancho-seccion mb-4 text-xl font-bold">
          {title}
        </Heading>
      )}

      <div>{children}</div>

      {footer && <footer className="mt-4 border-t border-linea pt-3">{footer}</footer>}
    </article>
  );
}
